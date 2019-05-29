# This file creates an empty SQLite database for development.

from mcarch.app import create_app, db
import mcarch.model

from mcarch.app import DevelopmentConfig
from mcarch.model import User

app = create_app(DevelopmentConfig)
with app.app_context():
    db.create_all()
    test_usr = User(name="test", password="a", email="test@example.com")
    db.session.add(test_usr)
    db.session.commit()

