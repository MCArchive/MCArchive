"""
This module contains basic tests that make sure all the pages in the `mods` module render without
major problems.
"""

from flask import url_for

from mcarch.model.mod import Mod, ModVersion, ModFile
from helpers.login import login_as, log_out, check_allowed

def test_new_mod(client, sample_users, sample_mods):
    data = dict(
        slug='new', name='New Test Mod', website='', authors=['1'],
        desc='This is a test',
    )
    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.new_mod'), data=data, follow_redirects=True)
    assert data['name'].encode('utf-8') in rv.data

    # Check the DB
    mod = Mod.query.filter_by(slug=data['slug']).first()
    assert mod != None, "Added mod not found in DB"
    assert mod.slug == data['slug']
    assert mod.name == data['name']
    assert mod.website == data['website']
    assert mod.desc == data['desc']

def test_edit_mod(client, sample_users, sample_mods):
    mod = sample_mods[0]
    data = dict(
        name='Edited', desc='This is a test',
    )
    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.edit_mod', slug=mod.slug), data=data, follow_redirects=True)
    assert data['name'].encode('utf-8') in rv.data

    # Check the DB
    mod = Mod.query.filter_by(slug=mod.slug).first()
    assert mod != None, "Edited mod not found in DB"
    assert mod.name == data['name']
    assert mod.desc == data['desc']


def test_new_vsn(client, sample_users, sample_mods):
    mod = sample_mods[0]
    data = dict(
        name='New Version', desc='This is a test',
    )
    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.new_mod_version', slug=mod.slug), data=data,
            follow_redirects=True)
    assert data['name'].encode('utf-8') in rv.data

    # Check the DB
    vsn = ModVersion.query.filter_by(name=data['name']).first()
    assert vsn != None, "New version not found in DB"
    assert vsn.name == data['name']
    assert vsn.desc == data['desc']

def test_edit_vsn(client, sample_users, sample_mods):
    mod = sample_mods[0]
    vsn = mod.mod_vsns[0]
    data = dict(
        name='Edited', desc='This is a test',
    )
    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.edit_mod_version', vid=vsn.id), data=data,
            follow_redirects=True)
    assert data['name'].encode('utf-8') in rv.data

    # Check the DB
    vsn = ModVersion.query.filter_by(id=vsn.id).first()
    assert vsn != None, "Edited version not found in DB"
    assert vsn.name == data['name']
    assert vsn.desc == data['desc']

# TODO: Test file upload. Need to mock B2 API calls and figure out how to do file uploads in
# tests first.


# Test access permissions

def test_new_mod_perm(client, sample_users):
    page = url_for('edit.new_mod')
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)

def test_edit_mod_perm(client, sample_users, sample_mod):
    page = url_for('edit.edit_mod', slug=sample_mod.slug)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)


def test_new_vsn_perm(client, sample_users, sample_mod):
    page = url_for('edit.new_mod_version', slug=sample_mod.slug)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)

def test_edit_vsn_perm(client, sample_users, sample_mod):
    page = url_for('edit.edit_mod_version', vid=sample_mod.mod_vsns[0].id)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)


def test_new_file_perm(client, sample_users, sample_mod):
    page = url_for('edit.new_mod_file', vid=sample_mod.mod_vsns[0].id)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)

def test_edit_file_perm(client, sample_users, sample_mod):
    page = url_for('edit.edit_mod_file', fid=sample_mod.mod_vsns[0].files[0].id)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)

