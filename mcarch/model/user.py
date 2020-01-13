import enum
from datetime import datetime, timedelta
import hashlib
import uuid
import pyotp
from flask import Flask, request, current_app as app
from flask_sqlalchemy import SQLAlchemy

from mcarch.app import db, bcrypt
from mcarch.util.sqla_uuid import GUID

class UserRole(enum.IntEnum):
    user = 1
    archivist = 2
    moderator = 3
    admin = 4

roles = UserRole

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.Binary(60), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    totp_secret = db.Column(db.String(16))
    totp_last_auth = db.Column(db.String(6)) # To avoid replay attacks
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
        self.clear_sessions()
        self.password = None

    def reset_2fa_secret(self):
        """Generates a new TOTP secret for this user."""
        self.clear_sessions()
        self.totp_secret = pyotp.random_base32()

    def clear_sessions(self):
        """Logs this user out by clearing all of their login sessions."""
        for sess in self.sessions:
            sess.disable()

    def gen_passwd_reset_token(self):
        """Creates a reset token for this user and returns the string token."""
        self.reset_token = ResetToken(kind=reset_type.password)
        token = self.reset_token.token
        return str(token)

    def gen_2fa_reset_token(self):
        """Creates a reset token for this user's 2-factor authentication secret."""
        self.reset_token = ResetToken(kind=reset_type.otp)
        token = self.reset_token.token
        return str(token)

    def totp_uri(self):
        return pyotp.TOTP(self.totp_secret).provisioning_uri(self.email, "MCArchive")

    def validate_otp(self, code):
        if self.totp_last_auth == code:
            # Reject repeated codes to prevent a replay attack.
            return False
        else:
            totp = pyotp.TOTP(self.totp_secret)
            if totp.verify(code, valid_window=1):
                self.totp_last_auth = code
                return True
            else: return False

    def disable(self):
        for sess in self.sessions:
            sess.disable()
        self.disabled = True

    def enable(self):
        self.disabled = False

    def __repr__(self):
        return '<User %r>' % self.name

class Session(db.Model):
    """Represents a user's login session.

    A session may not be considered fully authenticated if `authed_2fa` is false.
    """
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

    authed_2fa = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    def __init__(self, *args, sess_id=None, **kwargs):
        if not sess_id:
            sess_id = uuid.uuid4()
        super(Session, self).__init__(*args, sess_id=sess_id, **kwargs)

    def expired(self):
        if not self.active: return False
        if self.authed_2fa:
            return self.last_seen < datetime.utcnow() - app.config['SERV_SESSION_EXPIRE_TIME']
        else:
            return self.last_seen < datetime.utcnow() - \
                    app.config['SERV_PARTIAL_SESSION_EXPIRE_TIME']

    def auth_2fa(self, code):
        """Authenticates the user's second factor with the given code.

        Returns true on success, false on failure. If successful, this session
        will be marked as fully authenticated.

        If the user's 2 factor is disabled, this has no effect.
        """
        if self.user.totp_secret and self.user.validate_otp(code):
            self.authed_2fa = True
            db.session.commit()
            return True
        else:
            return False

    def disable(self):
        self.active = False

    def touch(self):
        """Updates this session's last seen date."""
        now = datetime.utcnow()
        self.last_seen = now
        self.user.last_seen = now



class ResetType(enum.IntEnum):
    password = 1
    otp = 2

reset_type = ResetType

class ResetToken(db.Model):
    """Represents a one time use key that allows a user to reset (or set) their password."""
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(GUID(), nullable=False, unique=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    active = db.Column(db.Boolean, nullable=False, default=True)
    kind = db.Column(db.Enum(ResetType), nullable=False)

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

