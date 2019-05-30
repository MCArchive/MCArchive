from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_assets import Environment, Bundle
from flask_bcrypt import Bcrypt
from flaskext.markdown import Markdown

db = SQLAlchemy()
bcrypt = Bcrypt()

from mcarch import login

class DevelopmentConfig(object):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    ASSETS_DEBUG = True
    SECRET_KEY = "notsecret"
    DATABASE = 'sqlite:////tmp/test.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    print('APP IS USING DEVELOPMENT CONFIG. DO NOT USE IN PRODUCTION')


def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)
    if app.env == 'development': app.config.from_object(DevelopmentConfig)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    register_extensions(app)
    register_assets(app)
    register_blueprints(app)
    register_conprocs(app)
    return app

def register_extensions(app):
    Markdown(app)
    db.init_app(app)
    bcrypt.init_app(app)

def register_assets(app):
    assets = Environment(app)

    css = Bundle('scss/main.scss', 'scss/nav.scss', 'scss/forms.scss',
            filters='pyscss', output='gen/main.css')

    js = Bundle('js/accordion.js',
            filters='jsmin', output='gen/main.js')

    assets.register("css_all", css)
    assets.register("js_all", js)

def register_conprocs(app):
    login.register_conproc(app)
    @app.context_processor
    def inject():
        return dict(
            len = len
        )

def register_blueprints(app):
    from mcarch.views import root
    app.register_blueprint(root)
    from mcarch.views.user import user
    app.register_blueprint(user)
    from mcarch.views.mods import modbp
    app.register_blueprint(modbp)

