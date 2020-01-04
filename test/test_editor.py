"""
This module contains basic tests that make sure all the pages in the `mods` module render without
major problems.
"""

from flask import url_for

from mcarch.model.mod import Mod, ModVersion, ModFile
from mcarch.model.mod.draft import DraftMod, DraftModVersion, DraftModFile
from mcarch.model.user import User
from helpers.login import login_as, log_out, check_allowed

# Makes a draft of the mod and returns the `DraftMod`.
def mk_draft(db, mod):
    user = User.query.first()
    draft = mod.make_draft(user)
    db.add(draft)
    db.commit()
    return draft

def test_new_mod(client, sample_users, sample_mods):
    data = dict(
        name='New Test Mod', website='', authors=['1'],
        desc='This is a test',
    )
    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.new_mod'), data=data, follow_redirects=True)
    assert data['name'].encode('utf-8') in rv.data

    # Check the DB
    mod = DraftMod.query.filter_by(name=data['name']).first()
    assert mod != None, "Added mod not found in DB"
    assert mod.name == data['name']
    assert mod.website == data['website']
    assert mod.desc == data['desc']

def test_mk_draft(client, sample_users, sample_mods):
    mod = sample_mods[0]
    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.new_draft', slug=mod.slug), follow_redirects=True)
    assert mod.name.encode('utf-8') in rv.data

    # Check the DB
    draft = DraftMod.query.filter_by(name=mod.name).first()
    assert draft != None, "Draft not found in DB"


def test_edit_mod(db_session, client, sample_users, sample_mods):
    mod = mk_draft(db_session, sample_mods[0])
    data = dict(
        name='Edited', desc='This is a test',
    )
    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.edit_mod', id=mod.id), data=data, follow_redirects=True)
    assert data['name'].encode('utf-8') in rv.data

    # Check the DB
    mod = DraftMod.query.filter_by(id=mod.id).first()
    assert mod != None, "Edited draft not found in DB"
    assert mod.name == data['name']
    assert mod.desc == data['desc']


def test_new_vsn(db_session, client, sample_users, sample_mods):
    mod = mk_draft(db_session, sample_mods[0])
    data = dict(
        name='New Version', desc='This is a test',
    )
    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.new_mod_version', id=mod.id), data=data,
            follow_redirects=True)
    assert data['name'].encode('utf-8') in rv.data

    # Check the DB
    vsn = DraftModVersion.query.filter_by(name=data['name']).first()
    assert vsn != None, "New version not found in DB"
    assert vsn.name == data['name']
    assert vsn.desc == data['desc']

def test_edit_vsn(db_session, client, sample_users, sample_mods):
    mod = mk_draft(db_session, sample_mods[0])
    vsn = mod.mod_vsns[0]
    data = dict(
        name='Edited', desc='This is a test',
    )
    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.edit_mod_version', id=vsn.id), data=data,
            follow_redirects=True)
    assert data['name'].encode('utf-8') in rv.data

    # Check the DB
    vsn = DraftModVersion.query.filter_by(id=vsn.id).first()
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

def test_draft_page_perm(client, sample_users, sample_mod, db_session):
    sample_mod = mk_draft(db_session, sample_mod)
    page = url_for('edit.draft_page', id=sample_mod.id)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)

def test_edit_mod_perm(db_session, client, sample_users, sample_mod):
    sample_mod = mk_draft(db_session, sample_mod)
    page = url_for('edit.edit_mod', id=sample_mod.id)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)


def test_new_vsn_perm(db_session, client, sample_users, sample_mod):
    sample_mod = mk_draft(db_session, sample_mod)
    page = url_for('edit.new_mod_version', id=sample_mod.id)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)

def test_edit_vsn_perm(db_session, client, sample_users, sample_mod):
    sample_mod = mk_draft(db_session, sample_mod)
    page = url_for('edit.edit_mod_version', id=sample_mod.mod_vsns[0].id)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)


def test_new_file_perm(db_session, client, sample_users, sample_mod):
    sample_mod = mk_draft(db_session, sample_mod)
    page = url_for('edit.new_mod_file', id=sample_mod.mod_vsns[0].id)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)

def test_edit_file_perm(db_session, client, sample_users, sample_mod):
    sample_mod = mk_draft(db_session, sample_mod)
    page = url_for('edit.edit_mod_file', id=sample_mod.mod_vsns[0].files[0].id)
    check_allowed(client, sample_users['admin'], page, expect=True)
    check_allowed(client, sample_users['moderator'], page, expect=True)
    check_allowed(client, sample_users['archivist'], page, expect=True)
    check_allowed(client, sample_users['user'], page, expect=False)

