import os
import tempfile

import pytest

from sqlalchemy import event

from mcarch.app import create_app, db, bcrypt
import mcarch.model
from mcarch.model.mod import Mod, ModVersion, ModFile, GameVersion, ModAuthor
from mcarch.model.file import StoredFile
from mcarch.model.user import User, roles

@pytest.fixture(scope='session')
def _db(app):
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        return db

@pytest.fixture(scope='session')
def app(tmp_path_factory):
    if 'TEST_DATABASE_URL' in os.environ:
        dburi = os.environ['TEST_DATABASE_URL']
    else:
        tmp_path = tmp_path_factory.mktemp("db")
        dburi = "sqlite:////{}".format(tmp_path / "db.sqlite")
    class TestConfig:
        DATABASE = dburi
        SQLALCHEMY_DATABASE_URI = dburi
        SQLALCHEMY_ECHO = False
        SECRET_KEY = "secret!"
        TESTING = True
        WTF_CSRF_ENABLED = False # disable CSRF protection so we can test forms
        RATELIMIT_ENABLED = False # the test suite exceeds the rate-limits, so disable them
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
    def mkfile(**kwargs):
        return ModFile(stored=StoredFile(b2_path=None, **kwargs))
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
                        mkfile(name='test-4.2.0.jar', sha256='fake')
                    ]
                ),
                ModVersion(
                    name='1.3.3.7',
                    desc='This is another test',
                    game_vsns=[gv_b173],
                    files=[
                        mkfile(name='test-1.3.3.7-client.jar', sha256='fakeclient'),
                        mkfile(name='test-1.3.3.7-server.jar', sha256='fakeserver'),
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
                        mkfile(name='guide-4.2.jar', sha256='theanswer')
                    ]
                ),
                ModVersion(
                    name='2.7',
                    game_vsns=[gv_a123],
                    files=[
                        mkfile(name='guide-2.7.jar', sha256='bypass')
                    ]
                ),
            ]
        ),
    ]

@pytest.fixture(scope='session')
def sample_passwds():
    """Pre-generates password hashes for `sample_users`. This drastically speeds up any tests
    relying on sample users, as bcrypt is intentionally very slow."""
    pwds = {
        'admin': 'a',
        'mod': 'b',
        'arch': 'c',
        'user': 'd',
        '2fa': 'e',
    }
    for k, pwd in pwds.items():
        pwds[k] = dict(password=pwd, passhash=bcrypt.generate_password_hash(pwd))
    return pwds

@pytest.fixture
def sample_users(db_session, sample_passwds):
    """Returns a dict of sample users keyed by their roles.
    This function also adds a field called `plainpasswd` to each user, which contains the
    password for that user in plain text.
    """
    def mk_user(name, **kwargs):
        u = User(name=name, **sample_passwds[name], **kwargs)
        # Add the `plainpasswd` field so tests can log in as these users.
        setattr(u, 'plainpasswd', sample_passwds[name]['password'])
        return u
    users = {
        "admin": mk_user(name="admin", email="test@example.com", role=roles.admin),
        "moderator": mk_user(name="mod", email="a@example.com", role=roles.moderator),
        "archivist": mk_user(name="arch", email="b@example.com", role=roles.archivist),
        "user": mk_user(name="user", email="c@example.com", role=roles.user),
        "2fa": mk_user(name="2fa", email="2fa@example.com", role=roles.admin,
            totp_secret='REEEEEEEEEEEEEEE'),
    }
    for _, u in users.items(): db_session.add(u)
    db_session.commit()
    return users

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

