import csv
import logging
import os
from typing import Union, Optional, Dict, List, Iterable

import marshmallow
import psycopg2.errors
import requests
import sqlalchemy
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only, lazyload

from api import schemas

logger = logging.getLogger(__name__)
bp = Blueprint('docs', __name__)
schema_id_map = {schemas.Product: os.getenv("PRODUCT_DOC_ID", ""),
                 schemas.Review: os.getenv("REVIEW_DOC_ID", "")}
_models = Union[schemas.models.Review, schemas.models.Product]


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
            logger.error("Cannot handle request to url=%s exception=%s", url, str(e))
        return fetched


class DocParser:
    def __init__(self, response: str,
                 schema: schemas.models.ma.SQLAlchemyAutoSchema,
                 db: SQLAlchemy,
                 product_asin_data: Optional[Dict[str, schemas.models.Product]] = None):
        self.product_asin_data = product_asin_data
        self.schema = schema
        self.db = db
        self.asin_data: Dict[str, Union[_models, List[_models]]] = dict()
        csv_lines = response.splitlines()
        self.csv_col_names = self.get_csv_col_names(csv_lines.pop(0).split(","))
        self.csv_rows = self.get_csv_rows(csv_lines)
        for csv_row in self.csv_rows:
            kwargs = dict(zip(self.csv_col_names, csv_row))
            valid_kwargs = self.get_valid_kwargs(kwargs)
            if not valid_kwargs:
                continue
            obj = schema.Meta.model(**valid_kwargs)
            self.save(obj)
            self.set_asin_data(obj)
        is_committed = self.save(commit=True)
        if not is_committed:
            self.asin_data = {}
            return  # if there is duplicate - skip whole dataset

    def set_asin_data(self, obj: Optional[_models]):
        """Make mappings to link tables (product_id fk) later without extra select queries"""
        self.asin_data[obj.asin] = obj

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
            kwargs["product_id"] =\
                self.product_asin_data.get(kwargs["asin"]).query.options(
                    load_only("id"), lazyload("reviews")).first().id
        try:
            valid_kwargs = self.schema().load(kwargs)
        except marshmallow.exceptions.ValidationError as e:
            logger.error("Skipped invalid data=%s validation_errors=%s", kwargs, e.messages)
        return valid_kwargs

    def save(self, obj: Optional[_models] = None, commit=False) -> bool:
        is_committed = False
        if obj:
            self.db.session.add(obj)
        if commit:
            try:
                self.db.session.commit()
            except (psycopg2.errors.UniqueViolation, sqlalchemy.exc.IntegrityError) as e:
                logger.error("Skipped duplicate data=%s", str(e))
            else:
                is_committed = True
        return is_committed


def parse(db):
    product_response = DocFetcher.fetch(schema_id_map[schemas.Product])
    product_parser = DocParser(product_response, schemas.Product, db)
    # Semantic logic of this cmd is loading initial data to empty DB, so let's say
    # if there is duplicate - skip whole cmd call
    if not product_parser.asin_data:
        return
    review_response = DocFetcher.fetch(schema_id_map[schemas.Review])
    DocParser(review_response, schemas.Review, db, product_parser.asin_data)
