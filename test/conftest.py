import os
import tempfile

import pytest

from sqlalchemy import event

from mcarch.app import create_app, db
import mcarch.model
from mcarch.model.mod import Mod, ModVersion, ModFile, GameVersion, ModAuthor

@pytest.fixture(scope='session')
def _db(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
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
    return app

@pytest.fixture(scope='function')
def fresh_db(app):
    """A fixture that drops and re-creates the database tables before every test."""
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()


# Generate a list of sample mods to test with
def mk_sample_mods():
    gv_125 = GameVersion(name='1.2.5')
    gv_b173 = GameVersion(name='b1.7.3')
    gv_a123 = GameVersion(name='a1.2.3')
    return [
        Mod(
            name="Test", slug="test", desc="This is a test", authors=[ModAuthor(name="tester")],
            mod_vsns=[
                ModVersion(
                    name='4.2.0',
                    desc='This is a test',
                    game_vsns=[gv_125],
                    files=[
                        ModFile(filename='test-4.2.0.jar', sha256='fake')
                    ]
                ),
                ModVersion(
                    name='1.3.3.7',
                    desc='This is another test',
                    game_vsns=[gv_b173],
                    files=[
                        ModFile(filename='test-1.3.3.7-client.jar', sha256='fakeclient'),
                        ModFile(filename='test-1.3.3.7-server.jar', sha256='fakeserver'),
                    ]
                ),
            ]
        ),
        Mod(name="Don't Panic", slug="guide",
            authors=[ModAuthor(name="Ford Prefect"), ModAuthor(name="Arthur Dent")],
            mod_vsns=[
                ModVersion(
                    name='4.2',
                    game_vsns=[gv_b173],
                    files=[
                        ModFile(filename='guide-4.2.jar', sha256='theanswer')
                    ]
                ),
                ModVersion(
                    name='2.7',
                    game_vsns=[gv_a123],
                    files=[
                        ModFile(filename='guide-2.7.jar', sha256='bypass')
                    ]
                ),
            ]
        ),
    ]


@pytest.fixture
def sample_mod(db_session):
    mod = mk_sample_mods()[0]
    db_session.add(mod)
    db_session.commit()
    mod.log_change(user=None)
    db_session.commit()
    return mod

@pytest.fixture
def sample_mods(db_session):
    mods = mk_sample_mods()
    for m in mods:
        db_session.add(m)
        db_session.commit()
        m.log_change(user=None)
        db_session.commit()
    return mods

@pytest.fixture
def sample_authors(sample_mods):
    authors = []
    for m in sample_mods:
        authors.extend(m.authors)
    return authors

@pytest.fixture
def sample_gvsns(sample_mods):
    gvsns = []
    for m in sample_mods:
        for v in m.mod_vsns:
            gvsns.extend(v.game_vsns)
    return gvsns

