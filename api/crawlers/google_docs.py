import csv
import logging
import os

import marshmallow
import psycopg2.errors
import requests
import sqlalchemy
from flask import Blueprint

from api import schemas

logger = logging.getLogger(__name__)
bp = Blueprint('docs', __name__)
url_template = "https://docs.google.com/spreadsheets/d/{doc_id}/export?exportFormat=csv"
schema_id_map = (schemas.Product, os.getenv("PRODUCT_DOC_ID", "")), \
                (schemas.Review, os.getenv("REVIEW_DOC_ID", ""))


def parse(db):
    asin_to_data_list = list()
    for schema, doc_id in schema_id_map:
        url = url_template.format(doc_id=doc_id)
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            logger.error("Cannot handle request to url=%s exception=%s", url, str(e))
            continue
        lines = response.text.splitlines()

        # normalize column names to model column names
        columns = [c.lower() if c.lower() != "review" else "body"
                   for c in lines.pop(0).split(",")]

        # read csv data
        rows = csv.reader(lines, delimiter=",", quotechar="\"")

        # make mapping {asin: schema object} to link tables later without extra select queries
        asin_to_data = dict()

        # read & validate & save to db
        for row in rows:
            kwargs = dict(zip(columns, row))
            try:
                validated_kwargs = schema().load(kwargs)
            except marshmallow.exceptions.ValidationError as e:
                logger.error("Skipped invalid data=%s validation_errors=%s", kwargs, e.messages)
                continue
            new_obj = schema.Meta.model(**validated_kwargs)
            db.session.add(new_obj)
            if schema == schemas.Review:
                asin_to_data.setdefault(new_obj.asin, []).append(new_obj)
            else:
                asin_to_data[new_obj.asin] = new_obj
        # noinspection PyUnresolvedReferences
        #   Semantic logic of this cmd is loading data to empty DB, so let's say
        # if there is duplicate - skip whole cmd call
        try:
            db.session.commit()
        except (psycopg2.errors.UniqueViolation, sqlalchemy.exc.IntegrityError) as e:
            logger.error("Skipped duplicate data=%s", str(e))
            return
        asin_to_data_list.append(asin_to_data)
    # link data from product and review tables using mutual `asin` columns
    product_data, review_data = asin_to_data_list
    for asin, obj in product_data.items():
        reviews = review_data.get(asin)
        if not reviews:
            continue
        for review in reviews:
            review.product_id = obj.id
    db.session.flush()
    db.session.commit()
