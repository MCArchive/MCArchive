import enum
from datetime import datetime, timedelta
import hashlib
import uuid
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
    password = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    last_seen = db.Column(db.DateTime)
    disabled = db.Column(db.Boolean)

    def __init__(self, *args, password, passhash=None, **kwargs):
        """
        Creates a new `User` object. The given password will be hashed automatically.

        The `passhash` parameter specifies an already hashed password, and can
        be used to speed up tests, as bcrypt is intentionally slow.
        """
        pwd = None
        if passhash is not None: pwd = passhash
        else: pwd = bcrypt.generate_password_hash(password)
        super(User, self).__init__(*args, password=pwd, **kwargs)

    def has_role(self, role):
        """Returns True if the user's role is equal or greater than the given role.
        If the given role is None, returns True."""
        if role is None: return True
        return self.role >= role

    def avatar_url(self):
        """Returns the Gravatar URL for this user based on their email."""
        # See https://en.gravatar.com/site/implement/hash/
        # Trim whitespace, convert to lowercase, md5 hash
        email = self.email.encode("utf-8")
        gravatar_hash = hashlib.md5(email.strip().lower()).hexdigest()
        return "https://gravatar.com/avatar/{}?d=identicon".format(gravatar_hash)

    def set_password(self, password):
        """Sets a new password. The given password will be hashed."""
        self.password = bcrypt.generate_password_hash(password)

    def clear_password(self):
        """Clears this user's password, preventing them from logging in anymore.
        Also clears all of the user's sessions, logging them out."""
        for sess in self.sessions:
            sess.disable()
        self.password = None

    def gen_passwd_reset_token(self):
        """Creates a reset token for this user and returns the string token."""
        self.reset_token = ResetToken()
        token = self.reset_token.token
        return str(token)

    def disable(self):
        for sess in self.sessions:
            sess.disable()
        self.disabled = True

    def enable(self):
        self.disabled = False

    def __repr__(self):
        return '<User %r>' % self.name

class Session(db.Model):
    """Represents a user's login session."""
    id = db.Column(db.Integer, primary_key=True)
    # Session ID stored in the user's browser cookies.
    sess_id = db.Column(GUID(), nullable=False, unique=True)

    login_ip = db.Column(db.String(128), nullable=False)
    login_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # User this session is logged in as.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User',
            backref=db.backref('sessions', lazy=True, order_by=last_seen.desc()))

    active = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, *args, sess_id=None, **kwargs):
        if not sess_id:
            sess_id = uuid.uuid4()
        super(Session, self).__init__(*args, sess_id=sess_id, **kwargs)

    def expired(self):
        return not self.active or \
                self.last_seen < datetime.utcnow() - app.config['SERV_SESSION_EXPIRE_TIME']

    def disable(self):
        self.active = False

    def touch(self):
        """Updates this session's last seen date."""
        now = datetime.utcnow()
        self.last_seen = now
        self.user.last_seen = now

class ResetToken(db.Model):
    """Represents a one time use key that allows a user to reset (or set) their password."""
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(GUID(), nullable=False, unique=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Boolean, nullable=False, default=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('reset_token', uselist=False,
        cascade='all, delete-orphan'))

    def __init__(self, *args, token=None, **kwargs):
        if not token:
            token = uuid.uuid4()
        super(ResetToken, self).__init__(*args, token=token, **kwargs)

    def expired(self):
        return not self.active or \
                self.created < datetime.utcnow() - app.config['PASSWD_RESET_EXPIRE_TIME']

