from flask import url_for
import pyotp


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
    rv = client.get(url_for('archivist.main'), follow_redirects=True)
    assert b'2-factor' in rv.data

