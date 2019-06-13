"""
This module contains basic tests that make sure all the pages in the `mods` module render without
major problems.
"""

def login_as(client, user):
    client.post('/login', data={
        'username': user.name,
        'password': user.plainpasswd,
    }, follow_redirects=True)
    return client.post('/login', follow_redirects=True)

def log_out(client):
    return client.get('/logout', follow_redirects=True).data

def check_allowed(client, user, page, expect=True):
    """Checks if the site allows the given user to view the given page.
    If expect is true, asserts that the user can view the page, otherwise
    asserts that the user can't."""
    login_as(client, user)
    rv = client.get(page)
    if expect: assert rv.status_code == 200
    else: assert rv.status_code == 302
    log_out(client)

def test_browse(client, sample_mods):
    rv = client.get('/mods')
    assert sample_mods[0].name.encode('utf-8') in rv.data

def test_mod_page(client, sample_mods):
    for mod in sample_mods:
        rv = client.get('/mods/{}'.format(mod.slug))
        for vsn in mod.mod_vsns:
            assert vsn.name.encode('utf-8') in rv.data
            for f in vsn.files:
                assert f.filename.encode('utf-8') in rv.data

def test_mod_page_json(client, sample_mods):
    for mod in sample_mods:
        rv = client.get('/mods/{}.json'.format(mod.slug))
        for vsn in mod.mod_vsns:
            assert vsn.name.encode('utf-8') in rv.data
            for f in vsn.files:
                assert f.filename.encode('utf-8') in rv.data

def test_authors(client, sample_authors):
    rv = client.get('/authors')
    for a in sample_authors:
        assert a.name.encode('utf-8') in rv.data

def test_gamevsns(client, sample_gvsns):
    rv = client.get('/gamevsns')
    for v in sample_gvsns:
        assert v.name.encode('utf-8') in rv.data

def test_mod_hist(client, sample_users, sample_mods):
    sm = sample_mods[0]
    login_as(client, sample_users['admin'])
    rv = client.get('/mods/{}/history'.format(sm.slug))
    assert b'Revision 0' in rv.data

def test_mod_hist_perm(client, sample_users, sample_mod):
    sm = sample_mod
    page = '/mods/{}/history/{}'.format(sm.slug, 0)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)

def test_mod_revision(client, sample_users, sample_mods):
    sm = sample_mods[0]
    login_as(client, sample_users['admin'])
    rv = client.get('/mods/{}/history/{}'.format(sm.slug, 0))
    assert b'revision 0' in rv.data

def test_mod_revision_perm(client, sample_users, sample_mod):
    sm = sample_mod
    page = '/mods/{}/history/{}'.format(sm.slug, 0)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)

#def test_edit_mod(client, sample_users):
#    login_as(sample_users['admin'])

