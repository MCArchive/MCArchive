"""
This module implements the app's login system.

It contains functions for logging in and out users and managing their sessions as well as some
decorators for making certain routes require authentication.

It also provides a function to register a context processor with the app, which provides functions
such as `cur_user` and `cur_session` inside templates.
"""

import uuid
import functools
from datetime import datetime

from flask import session, request, redirect, url_for, flash, abort

from mcarch.app import db, bcrypt
from mcarch.model.user import User, Session, roles

def login_required(func=None, role=None, pass_user=False):
    """
    This decorator can be used on a route to redirect the user to the login page if they aren't
    logged in.
    """
    if not func: return functools.partial(login_required, role=role, pass_user=pass_user)
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        sess = cur_session(only_fully_authed=False)
        if sess:
            if sess.authed_2fa:
                user = sess.user
                if user.has_role(role):
                    if pass_user: kwargs['user'] = user
                    return func(*args, **kwargs)
                else:
                    return abort(403)
            else:
                flash('You must complete 2-factor authentication.')
                return redirect(url_for('user.prompt_2fa', next=request.url))
        else:
            flash('You must log in to access that page.')
            return redirect(url_for('user.login', next=request.url))
    return wrapped

def logout_required(func):
    """
    The inverse of login_required. Redirects a user to the home page if they're already logged in.
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if cur_user():
            flash('You are already logged in.')
            return redirect(url_for('root.home'))
        else:
            return func(*args, **kwargs)
    return wrapped

def log_out():
    """Logs out the current user. Does nothing if there is no login session."""
    sess = cur_session()
    if sess:
        # Remove the session from the database.
        sess.disable()
        db.session.commit()
    clear_session()

def clear_session():
    session['sessid'] = None
    session['user'] = None

def log_in(uname, passwd):
    """Attempts to log in with the given credentials. Returns true on success, false on failure."""
    user = User.query.filter_by(name=uname).first()
    if not user: return False
    if user.disabled or not user.password:
        return False

    if bcrypt.check_password_hash(user.password, passwd):
        create_sess(user)
        return True
    else:
        return False

def create_sess(user):
    """Creates a new session for the given user and stores the session ID in the flask session
    object.

    If the user has 2 factor authentication enabled, this will create a session
    that isn't fully authenticated yet.
    """
    dbsess = Session(
        user_id = user.id,
        login_ip = request.remote_addr,
        authed_2fa=not user.totp_secret,
    )
    db.session.add(dbsess)
    db.session.commit()

    # Add the session ID to the flask session cookie.
    session['sessid'] = str(dbsess.sess_id)

def cur_session(only_fully_authed=True):
    """
    Gets the current login session from the database.
    
    Returns None if there is no session.

    If `only_fully_authed` is true, only returns sessions where the user either
    has no 2FA set up, or the user has authenticated with their 2nd factor.
    """
    if 'sessid' not in session: return None
    sess = Session.query.filter_by(sess_id=session['sessid'], active=True).first()
    if sess:
        # If the session is expired or the user has a different IP, remove it from the database
        # and pretend it didn't exist.
        if sess.expired():
            flash('Your last session expired. Please log in again.')
            sess.disable()
            clear_session()
            db.session.commit()
            return None
        elif sess.login_ip != request.remote_addr:
            flash('Your IP address changed. Please log in again.')
            sess.disable()
            clear_session()
            db.session.commit()
            return None
        elif only_fully_authed and not sess.authed_2fa:
            return None
        # Update `last_seen` and `last_ip`.
        sess.touch()
        db.session.commit()
    return sess

def cur_user(only_fully_authed=True):
    """
    Gets the currently logged in user from the database.
    
    Returns None if the user is not logged in.

    See `cur_session` for info on `only_fully_authed`
    """
    sess = cur_session(only_fully_authed)
    if not sess: return None
    return sess.user

def has_role(role):
    """Returns true if the current user has the given role."""
    user = cur_user()
    if user: return user.has_role(role)
    else: return False

def register_conproc(app):
    """
    Registers a context processor with the flask app which provides access to the following
    functions within jinja templates:

    `cur_user`, `cur_session`
    """
    @app.context_processor
    def inject():
        return dict(
            cur_session = cur_session,
            cur_user = cur_user,
            has_role = has_role,
            _roles = roles,
        )
    

