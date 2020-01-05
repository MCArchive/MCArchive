import os
import os.path
from datetime import timedelta
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from flaskext.markdown import Markdown

db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
b2api = None

from mcarch import login
from mcarch.util.filters import register_filters

class DefaultConfig(object):
    # Time until sessions in the database expire
    SERV_SESSION_EXPIRE_TIME = timedelta(days=5)
    PASSWD_RESET_EXPIRE_TIME = timedelta(hours=1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    B2_KEY_ID = None
    B2_APP_KEY = None
    B2_BUCKET_NAME = None

class DevelopmentConfig(object):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    ASSETS_DEBUG = True
    SECRET_KEY = "notsecret"
    if 'DATABASE_URL' in os.environ:
        DATABASE = os.environ['DATABASE_URL']
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    else:
        DATABASE = 'sqlite:////tmp/test.db'
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'


def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(DefaultConfig)
    if 'MCARCH_CONFIG' in os.environ:
        app.config.from_envvar('MCARCH_CONFIG')
    if app.env == 'development':
        app.config.from_object(DevelopmentConfig)
        print('APP IS USING DEVELOPMENT CONFIG. DO NOT USE IN PRODUCTION')
    app.config.from_object(config_object)

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
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

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

