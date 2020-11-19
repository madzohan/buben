import json

import psycopg2
import pytest
import sqlalchemy
from _pytest.logging import LogCaptureFixture

from api import config as app_config_obj
from api import create_app
from api.models import db


def clear_db(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        try:
            db.engine.execute("DROP TABLE alembic_version")
        except (psycopg2.errors.UndefinedTable, sqlalchemy.exc.ProgrammingError):
            pass


@pytest.fixture(scope="session")
def app():
    """Create and configure a new app instance for all tests."""
    # session scope setup
    app = create_app(app_config_obj)
    assert app.testing is True
    with app.app_context():
        db.create_all()
    yield app
    # session scope teardown
    clear_db(app)


@pytest.fixture
def app_clear_db(app):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
    return app


# override caplog fixture to have json property
@pytest.fixture
def caplog(caplog):
    LogCaptureFixture.json = property(lambda c: [json.loads(m.replace('\'', '"')) for m in c.messages])
    return caplog


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def cli_runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
