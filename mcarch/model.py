from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from util.sqla_uuid import GUID

from mcarch.app import db, bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(70), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self, *args, password, **kwargs):
        """
        Creates a new `User` object. The given password will be hashed automatically.
        """
        pwd = bcrypt.generate_password_hash(password)
        db.Model.__init__(self, *args, password=pwd, **kwargs)

    def __repr__(self):
        return '<User %r>' % self.username

class Session(db.Model):
    """Represents a user's login session."""
    id = db.Column(db.Integer, primary_key=True)
    # Session ID stored in the user's browser cookies.
    sess_id = db.Column(GUID(), nullable=False, unique=True)
    # User this session is logged in as.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User',backref=db.backref('sessions', lazy=True))

    ip_addr = db.Column(db.String(42), nullable=False)
    login_date = db.Column(db.DateTime, nullable=False)

