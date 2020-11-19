from unittest.mock import Mock

import pytest
from flask_sqlalchemy import get_debug_queries

from api import schemas, models
from api.commands import docs_parse_cmd
from api.crawlers.google_docs import DocFetcher, requests, DocParser
from api.models import db


def test_fetch_ok(monkeypatch):
    response = "OK"
    monkeypatch.setattr(requests, "get", lambda _: Mock(text=response))
    fetched = DocFetcher.fetch("")
    assert fetched == response


def test_fetch_fail(monkeypatch, caplog):
    exc_txt = "Fail!"
    monkeypatch.setattr(requests, "get", Mock(side_effect=requests.exceptions.RequestException(exc_txt)))
    fetched = DocFetcher.fetch("http")
    assert fetched is None
    assert caplog.json[0] == dict(
        action="fetch",
        url="https://docs.google.com/spreadsheets/d/http/export?exportFormat=csv",
        message="Fail!")


def test_parse_product_invalid_data(app, caplog):
    """Test marshmallow validation which based on model schema"""
    # caplog.set_level(logging.ERROR)
    response = "Foo\nBar"
    with app.app_context():
        product_parser = DocParser(response, schemas.Product, db)
        assert len(get_debug_queries()) == 1  # 1 select query
        assert product_parser.product_asin_data == {}
    assert caplog.json[0] == {
        'action': 'validate',
        'data': {'foo': 'Bar'},
        'message': {'asin': ['Missing data for required field.'],
                    'title': ['Missing data for required field.'],
                    'foo': ['Unknown field.']}}


@pytest.mark.dependency(name="product")
def test_parse_product_ok(app, shared_datadir, request):
    """Test product table entries creation, parsed from csv"""
    response = (shared_datadir / "product.csv").read_text()
    with app.app_context():
        product_parser = DocParser(response, schemas.Product, db)
        assert len(get_debug_queries()) == 3  # 2 objects inserts + 1 product_asin_data select
    assert product_parser.product_asin_data == {"B06X14Z8JP": 1, "B06XYPJN4G": 2}
    request.config.cache.set("product_asin_data", product_parser.product_asin_data)  # save result in cache


@pytest.mark.dependency(name="product_duplicate", depends=["product"])
def test_parse_product_duplicate_fail(app, shared_datadir):
    """Test forbidden duplicate product entries"""
    response = (shared_datadir / "product.csv").read_text()
    with app.app_context():
        DocParser(response, schemas.Product, db)
        assert len(get_debug_queries()) == 0


@pytest.mark.dependency(name="review", depends=["product"])
def test_parse_review_ok(app, shared_datadir, request):
    """Test allowed duplicate review entries"""
    response = (shared_datadir / "review.csv").read_text()
    with app.app_context():
        product_asin_data = request.config.cache.get("product_asin_data", None)
        assert product_asin_data is not None
        DocParser(response, schemas.Review, db, product_asin_data)
        assert len(get_debug_queries()) == 2
        assert models.Review.query.count() == 2


@pytest.mark.dependency(name="review_duplicate", depends=["review"])
def test_parse_review_duplicate_ok(app, shared_datadir, request):
    """Test allowed duplicate review entries"""
    response = (shared_datadir / "review.csv").read_text()
    with app.app_context():
        product_asin_data = request.config.cache.get("product_asin_data", None)
        DocParser(response, schemas.Review, db, product_asin_data)
        assert len(get_debug_queries()) == 2
        assert models.Review.query.count() == 4


@pytest.mark.parametrize("response_is_valid, product_q_count, review_q_count", [(False, 0, 0), (True, 2, 2)])
def test_cli_parse_cmd(response_is_valid, product_q_count, review_q_count,
                       cli_runner, app_clear_db, monkeypatch, shared_datadir):
    """Test cli `flask parse` cmd"""
    with app_clear_db.app_context():
        assert models.Review.query.count() == 0
        assert models.Product.query.count() == 0
        if not response_is_valid:
            invalid_response = "Foo\nBar"
            responses = [invalid_response]
        else:
            product_response = (shared_datadir / "product.csv").read_text()
            review_response = (shared_datadir / "review.csv").read_text()
            responses = [product_response, review_response]
        monkeypatch.setattr(requests, "get", lambda _: Mock(text=responses.pop(0)))
        cli_runner.invoke(docs_parse_cmd)
        assert models.Product.query.count() == product_q_count
        assert models.Review.query.count() == review_q_count
