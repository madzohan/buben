import csv
import logging
import os
from typing import Union, Optional, Dict, List, Iterable

import marshmallow
import requests
import sqlalchemy
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only

from api import schemas, models

logger = logging.getLogger(__name__)
bp = Blueprint('docs', __name__)
schema_id_map = {schemas.Product: os.getenv("PRODUCT_DOC_ID", ""),
                 schemas.Review: os.getenv("REVIEW_DOC_ID", "")}
_models = Union[models.Review, models.Product]


class DocFetcher:
    url_template = "https://docs.google.com/spreadsheets/d/{doc_id}/export?exportFormat=csv"

    @classmethod
    def fetch(cls, doc_id: str) -> Optional[str]:
        url = cls.url_template.format(doc_id=doc_id)
        fetched = None
        try:
            response = requests.get(url)
            fetched = response.text
        except requests.exceptions.RequestException as e:
            logger.error(dict(action="fetch", url=url, message=str(e)))
        return fetched


class DocParser:
    def __init__(self, response: str,
                 schema: models.ma.SQLAlchemyAutoSchema,
                 db: SQLAlchemy,
                 product_asin_data: Optional[Dict[str, int]] = None):
        self.product_asin_data = product_asin_data
        self.schema = schema
        self.db = db
        csv_lines = response.splitlines()
        self.csv_col_names = self.get_csv_col_names(csv_lines.pop(0).split(","))
        self.csv_rows = self.get_csv_rows(csv_lines)
        for csv_row in self.csv_rows:
            kwargs = dict(zip(self.csv_col_names, csv_row))
            valid_kwargs = self.get_valid_kwargs(kwargs)
            if not valid_kwargs:
                continue
            obj = schema.Meta.model(**valid_kwargs)
            is_committed = self.save(obj, commit=True)
            if not is_committed:
                return  # if there is duplicate - skip whole dataset
        if not self.product_asin_data:
            self.set_product_asin_data()

    def set_product_asin_data(self):
        """Make mappings for feature tables link (Review product_id fk)
        """
        query = models.Product.query.options(load_only("id", "asin")).all()
        self.product_asin_data = {p.asin: p.id for p in query}

    @staticmethod
    def get_csv_col_names(csv_first_line: List[str]) -> List[str]:
        """Normalize column names to model column names"""
        return [c.lower() if c.lower() != "review" else "body" for c in csv_first_line]

    @staticmethod
    def get_csv_rows(csv_lines: List[str]) -> Iterable[str]:
        return csv.reader(csv_lines, delimiter=",", quotechar="\"")

    def get_valid_kwargs(self, kwargs: dict) -> Optional[dict]:
        valid_kwargs = None
        if self.product_asin_data:
            kwargs["product_id"] = self.product_asin_data.get(kwargs["asin"])
        try:
            valid_kwargs = self.schema().load(kwargs)
        except marshmallow.exceptions.ValidationError as e:
            logger.error(dict(action="validate", data=kwargs, message=e.messages))
        return valid_kwargs

    def save(self, obj: Optional[_models] = None, commit=False) -> bool:
        is_committed = False
        if obj:
            self.db.session.add(obj)
        if commit:
            try:
                self.db.session.commit()
            except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.ProgrammingError) as e:
                logger.error(dict(action="save", message=str(e)))
            else:
                is_committed = True
        return is_committed


def parse(db):
    product_response = DocFetcher.fetch(schema_id_map[schemas.Product])
    product_parser = DocParser(product_response, schemas.Product, db)
    # Semantic logic of this cmd is loading initial data to empty DB, so let's say
    # if there is duplicate - skip whole cmd call
    if not product_parser.product_asin_data:
        return
    review_response = DocFetcher.fetch(schema_id_map[schemas.Review])
    DocParser(review_response, schemas.Review, db, product_parser.product_asin_data)
