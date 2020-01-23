def login_as(client, user, passwd=None):
    return client.post('/login', data={
        'username': user.name,
        'password': user.plainpasswd if passwd == None else passwd,
    }, follow_redirects=True)

def log_out(client):
    return client.get('/logout', follow_redirects=True).data

def assert_no_login(client, user, passwd=None, msg=None):
    """Asserts that the given username/password combo fails to login"""
    if msg == None:
        msg = "Expected to be unable to log in with credentials: {} {}".format(user.name, passwd)
    assert b'failed' in login_as(client, user, passwd).data, msg

def check_allowed(client, user, page, expect=True):
    """Checks if the site allows the given user to view the given page.
    If expect is true, asserts that the user can view the page, otherwise
    asserts that the user can't."""
    login_as(client, user)
    rv = client.get(page)
    if expect:
        assert rv.status_code == 200, \
                "Expected user {} to be able to access page {}".format(user.name, page)
    else:
        assert rv.status_code == 403, \
                "Expected user {} to be blocked from accessing page {}".format(user.name, page)
    log_out(client)

