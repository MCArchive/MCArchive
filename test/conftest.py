import os
import tempfile

import pytest

from sqlalchemy import event

from mcarch import create_app
from mcarch.app import db
import mcarch.model

@pytest.fixture
def _db():
    return db

@pytest.fixture(scope='session')
def app(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("db")
    dburi = "sqlite:////{}".format(tmp_path / "db.sqlite")
    class TestConfig:
        DATABASE = dburi
        SQLALCHEMY_DATABASE_URI = dburi
        SQLALCHEMY_ECHO = False
        SECRET_KEY = "secret!"
        TESTING = True
        WTF_CSRF_ENABLED = False # disable CSRF protection so we can test forms
    app = create_app(TestConfig)
    yield app

@pytest.fixture(scope='function', autouse=True)
def fresh_db(app):
    """A fixture that drops and re-creates the database tables before every test."""
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

