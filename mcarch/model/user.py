import enum
from datetime import datetime, timedelta
import hashlib
from flask import Flask, request, current_app as app
from flask_sqlalchemy import SQLAlchemy

from util.sqla_uuid import GUID

from mcarch.app import db, bcrypt

class UserRole(enum.IntEnum):
    user = 1
    archivist = 2
    moderator = 3
    admin = 4

roles = UserRole

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(70), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    last_seen = db.Column(db.DateTime)

    def __init__(self, *args, password, passhash=None, **kwargs):
        """
        Creates a new `User` object. The given password will be hashed automatically.

        The `passhash` parameter specifies an already hashed password, and can
        be used to speed up tests, as bcrypt is intentionally slow.
        """
        pwd = None
        if passhash is not None: pwd = passhash
        else: pwd = bcrypt.generate_password_hash(password)
        db.Model.__init__(self, *args, password=pwd, **kwargs)

    def has_role(self, role):
        """Returns True if the user's role is equal or greater than the given role.
        If the given role is None, returns True."""
        if role is None: return True
        return self.role >= role

    def avatar_url(self):
        """Returns the Gravatar URL for this user based on their email."""
        md5 = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return "https://gravatar.com/avatar/{}?d=identicon".format(md5)

    def __repr__(self):
        return '<User %r>' % self.name

class Session(db.Model):
    """Represents a user's login session."""
    id = db.Column(db.Integer, primary_key=True)
    # Session ID stored in the user's browser cookies.
    sess_id = db.Column(GUID(), nullable=False, unique=True)
    # User this session is logged in as.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User',backref=db.backref('sessions', lazy=True))

    login_ip = db.Column(db.String(128), nullable=False)
    login_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def expired(self):
        return self.last_seen < datetime.utcnow() - app.config['SERV_SESSION_EXPIRE_TIME']

    def touch(self):
        """Updates this session's last seen date."""
        now = datetime.utcnow()
        self.last_seen = now
        self.user.last_seen = now

