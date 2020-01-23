from flask import url_for
from datetime import timedelta
import pyotp

from mcarch.model.user import User, ResetToken

from helpers.login import login_as, assert_no_login


# Test normal login.

def test_login_success(sample_users, client):
    user = sample_users['admin']
    data = dict(
        username = user.name,
        password = user.plainpasswd,
    )
    rv = client.post(url_for('user.login'), data=data, follow_redirects=True)
    assert b'Logged in' in rv.data

def test_login_badpass(sample_users, client):
    user = sample_users['admin']
    data = dict(
        username = user.name,
        password = 'wrong',
    )
    rv = client.post(url_for('user.login'), data=data, follow_redirects=True)
    assert b'Login failed' in rv.data

def test_login_baduname(sample_users, client):
    user = sample_users['admin']
    data = dict(
        username = 'wrong',
        password = user.plainpasswd,
    )
    rv = client.post(url_for('user.login'), data=data, follow_redirects=True)
    assert b'Login failed' in rv.data


# Test 2-factor authentication.

def test_2fa_auth(sample_users, client):
    user = sample_users['2fa']
    data = dict(
        username = user.name,
        password = user.plainpasswd,
    )
    rv = client.post(url_for('user.login'), data=data, follow_redirects=True)
    # Make sure we've been redirected to the 2-factor page.
    assert b'2-factor' in rv.data

    # Input the correct code.
    totp = pyotp.TOTP(user.totp_secret)
    data = dict(code=totp.now())
    rv = client.post(url_for('user.prompt_2fa'), data=data, follow_redirects=True)
    assert b'Logged in' in rv.data

def test_2fa_badcode(sample_users, client):
    user = sample_users['2fa']
    data = dict(
        username = user.name,
        password = user.plainpasswd,
    )
    rv = client.post(url_for('user.login'), data=data, follow_redirects=True)
    # Make sure we've been redirected to the 2-factor page.
    assert b'2-factor' in rv.data

    # Input the correct code.
    totp = pyotp.TOTP(user.totp_secret)
    data = dict(code='A12345') # This code can't ever be right since it's got a letter in it.
    rv = client.post(url_for('user.prompt_2fa'), data=data, follow_redirects=True)
    assert b'Login failed' in rv.data

def test_2fa_incomplete(sample_users, client):
    """This test checks that a user who has entered their password, but not
    completed 2-factor has no access to any sensitive pages on the site until
    they finish logging in."""
    user = sample_users['2fa']
    data = dict(
        username = user.name,
        password = user.plainpasswd,
    )
    rv = client.post(url_for('user.login'), data=data, follow_redirects=True)
    # Make sure we've been redirected to the 2-factor page.
    assert b'2-factor' in rv.data

    # Check a bunch of admin pages and make sure we get redirected back to the 2-factor page.
    rv = client.get(url_for('admin.main'), follow_redirects=True)
    assert b'2-factor' in rv.data
    rv = client.get(url_for('admin.changes'), follow_redirects=True)
    assert b'2-factor' in rv.data
    rv = client.get(url_for('admin.users'), follow_redirects=True)
    assert b'2-factor' in rv.data


# Test resetting password

def test_passwd_reset_inactive(client, sample_users, db_session):
    user = sample_users['user']
    user.clear_password()
    token = user.gen_passwd_reset_token()
    user.reset_token.active = False
    db_session.commit()

    client.post(url_for('user.reset_password', token=token), follow_redirects=True, data=dict(
        password='test',
        confirm='test',
    ))
    assert_no_login(client, user, 'test')

def test_passwd_reset_expired(client, sample_users, db_session):
    user = sample_users['user']
    user.clear_password()
    token = user.gen_passwd_reset_token()
    db_session.commit()
    tkn = ResetToken.query.filter_by(token=token).first()
    tkn.created = tkn.created - timedelta(days=300)
    db_session.commit()

    client.post(url_for('user.reset_password', token=token), follow_redirects=True, data=dict(
        password='test',
        confirm='test',
    ))
    assert_no_login(client, user, 'test')

def test_passwd_and_2fa_reset(app, client, sample_users, db_session):
    user = sample_users['user']
    user.clear_password()
    token = user.gen_passwd_reset_token()
    user.totp_secret = None
    db_session.commit()

    rv = client.post(url_for('user.reset_password', token=token), data=dict(
        password='test',
        confirm='test',
    ))
    assert rv.status_code == 302
    assert rv.location != url_for('user.login', _external=True), \
            "Redirected to login page, not TOTP setup"

    user = User.query.get(user.id)
    totp = pyotp.TOTP(user.totp_secret)
    rv = client.post(rv.location, data=dict(
        code = totp.now()
    ))
    assert rv.status_code == 302
    assert rv.location == url_for('user.login', _external=True)

def test_2fa_reset_inactive(client, sample_users, db_session):
    user = sample_users['user']
    user.reset_2fa_secret()
    token = user.gen_2fa_reset_token()
    db_session.commit()
    tkn = ResetToken.query.filter_by(token=token).first()
    tkn.active = False
    db_session.commit()

    rv = client.get(url_for('user.reset_2fa', token=token))
    assert rv.status_code != 200

def test_2fa_reset_expired(client, sample_users, db_session):
    user = sample_users['user']
    user.reset_2fa_secret()
    token = user.gen_2fa_reset_token()
    db_session.commit()
    tkn = ResetToken.query.filter_by(token=token).first()
    tkn.created = tkn.created - timedelta(days=300)
    db_session.commit()

    rv = client.get(url_for('user.reset_2fa', token=token))
    assert rv.status_code != 200

