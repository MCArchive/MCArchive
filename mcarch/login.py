"""
This module implements the app's login system.

It contains functions for logging in and out users and managing their sessions as well as some
decorators for making certain routes require authentication.

It also provides a function to register a context processor with the app, which provides functions
such as `cur_user` and `cur_session` inside templates.
"""

import uuid
from datetime import datetime
from functools import wraps

from flask import session, request, redirect, url_for, flash

from mcarch.app import db, bcrypt
from mcarch.model.user import User, Session

def login_required(func):
    """
    This decorator can be used on a route to redirect the user to the login page if they aren't
    logged in.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not cur_user():
            flash('You must log in to access that page.')
            return redirect(url_for('user.login', next=request.url))
        else:
            return func(*args, **kwargs)
    return wrapped

def logout_required(func):
    """
    The inverse of login_required. Redirects a user to the home page if they're already logged in.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        if cur_user():
            flash('You are already logged in.')
            return redirect(url_for('root.home'))
        else:
            return func(*args, **kwargs)
    return wrapped

def user_required(func):
    """
    Like login_required, but also passes the currently logged in user to the function.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        user = cur_user()
        if user:
            return func(*args, user=user, **kwargs)
        else:
            flash('You must log in to access that page.')
            return redirect(url_for('user.login', next=request.url))
    return wrapped


def log_out():
    """Logs out the current user. Does nothing if there is no login session."""
    sess = cur_session()
    if sess:
        # Remove the session from the database.
        db.session.delete(sess)
        db.session.commit()
    # Remove the session information from the user's cookies.
    session['sessid'] = None
    session['user'] = None

def log_in(uname, passwd):
    """Attempts to log in with the given credentials. Returns true on success, false on failure."""
    user = User.query.filter_by(name=uname).first()
    if not user: return False

    if bcrypt.check_password_hash(user.password, passwd):
        create_sess(user)
        return True
    else:
        return False

def create_sess(user):
    """Creates a new session for the given user and stores the session ID in the flask session
    object"""
    sessid = uuid.uuid4()
    dbsess = Session(
        sess_id = sessid,
        user_id = user.id,
        ip_addr = request.remote_addr,
        login_date = datetime.now(),
    )
    db.session.add(dbsess)
    db.session.commit()

    # Add the session ID to the flask session cookie.
    session['sessid'] = str(sessid)
    # Also add the user object for insecure_cur_user
    session['user'] = dict(
        id=user.id,
        name=user.name,
        email=user.email,
        avatar=user.avatar_url(),
    )

def cur_session():
    """
    Gets the current login session from the database.
    
    Returns None if there is no session.
    """
    if 'sessid' not in session: return None
    return Session.query.filter_by(sess_id=session['sessid']).first()

def cur_user():
    """
    Gets the currently logged in user from the database.
    
    Returns None if the user is not logged in.
    """
    sess = cur_session()
    if not sess: return None
    return sess.user

def insecure_cur_user():
    """
    Gets information about the currently logged in user as stored in the user's cookies.

    This information could potentially be modified by the user, but it doesn't
    require a database query unlike `cur_user`, so it should only be used in
    places where it doesn't really matter, such as in the navigation bar, where
    you might not want to query the database for every page load.

    Unlike `cur_user`, this returns a dict with a limited set of fields, not
    the actual database entry.
    """
    if 'user' not in session: return None
    return session['user']


def register_conproc(app):
    """
    Registers a context processor with the flask app which provides access to the following
    functions within jinja templates:

    `cur_user`, `cur_session`, `insecure_cur_user`
    """
    @app.context_processor
    def inject():
        return dict(
            cur_session = cur_session,
            cur_user = cur_user,
            insecure_cur_user = insecure_cur_user,
        )
    

