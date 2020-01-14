import os
import os.path
from datetime import timedelta
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flaskext.markdown import Markdown

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
b2api = None

from mcarch import login
from mcarch.util.filters import register_filters

class DefaultConfig(object):
    # Whether we're running the test suite
    TESTING = False
    # Time until sessions in the database expire
    SERV_SESSION_EXPIRE_TIME = timedelta(days=5)
    # Expire time for sessions that haven't completed 2FA
    SERV_PARTIAL_SESSION_EXPIRE_TIME = timedelta(hours=1)
    PASSWD_RESET_EXPIRE_TIME = timedelta(hours=1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REQUIRE_2FA = True
    B2_KEY_ID = None
    B2_APP_KEY = None
    B2_BUCKET_NAME = None

class DevelopmentConfig(object):
    DEBUG = True
    ASSETS_DEBUG = True
    SECRET_KEY = "notsecret"
    REQUIRE_2FA = True

def create_app(config_object={}):
    app = Flask(__name__)
    app.config.from_object(DefaultConfig)

    if 'MCARCH_CONFIG' in os.environ:
        app.config.from_envvar('MCARCH_CONFIG')
    else:
        print("Warning: no `MCARCH_CONFIG` set. Read README.md")

    if app.env == 'development':
        app.config.from_object(DevelopmentConfig)
        print('APP IS USING DEVELOPMENT CONFIG. DO NOT USE IN PRODUCTION')

    app.config.from_object(config_object)

    if app.config['TESTING']:
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['TEST_DATABASE_URI']

    register_extensions(app)
    register_blueprints(app)
    register_filters(app)
    register_conprocs(app)

    if 'B2_KEY_ID' in app.config and app.config['B2_KEY_ID']:
        init_b2(app)
    else:
        print('B2_KEY_ID is not set! File uploads will not work properly unless backblaze is configured!')
    return app

def register_extensions(app):
    Markdown(app)
    # import db tables before we init the DB
    import mcarch.model.mod
    import mcarch.model.file
    import mcarch.model.user
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

def register_conprocs(app):
    login.register_conproc(app)
    @app.context_processor
    def inject():
        return dict(
            list = list,
            enumerate = enumerate,
            map = map,
            len = len
        )


def register_blueprints(app):
    from mcarch.views import root
    app.register_blueprint(root)
    from mcarch.views.user import user
    app.register_blueprint(user)
    from mcarch.views.mods import modbp
    app.register_blueprint(modbp)
    from mcarch.views.editor import edit
    app.register_blueprint(edit)
    from mcarch.views.admin import admin
    app.register_blueprint(admin)
    from mcarch.views.archivist import arch
    app.register_blueprint(arch)
    from mcarch.cli import bp as cli
    app.register_blueprint(cli)

def init_b2(app):
    global b2api
    from b2sdk.account_info.in_memory import InMemoryAccountInfo
    from b2sdk.account_info.sqlite_account_info import SqliteAccountInfo
    from b2sdk.api import B2Api
    info = InMemoryAccountInfo()
    b2api = B2Api(info)
    b2api.authorize_account('production', app.config['B2_KEY_ID'], app.config['B2_APP_KEY'])

def get_b2bucket():
    """Gets a reference to the archive's B2 bucket from the B2 API"""
    return b2api.get_bucket_by_name(current_app.config['B2_BUCKET_NAME'])

