import os
import os.path
from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from flaskext.markdown import Markdown

db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()

from mcarch import login
from mcarch.util.filters import register_filters

class DefaultConfig(object):
    # Time until sessions in the database expire
    SERV_SESSION_EXPIRE_TIME = timedelta(days=5)
    PASSWD_RESET_EXPIRE_TIME = timedelta(hours=1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    B2_KEY_ID = None
    B2_APP_KEY = None

class DevelopmentConfig(object):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    ASSETS_DEBUG = True
    SECRET_KEY = "notsecret"
    DATABASE = 'sqlite:////tmp/test.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    MOD_STORE_DIR = os.path.abspath('mod_store/')


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
    from mcarch.views.admin import admin
    app.register_blueprint(admin)

