"""
This module contains basic tests that make sure all the pages in the `mods` module render without
major problems.
"""

from flask import url_for

from mcarch.model.mod import Mod, ModVersion, ModFile, ModAuthor, GameVersion
from mcarch.model.mod.draft import DraftMod, DraftModVersion, DraftModFile
from mcarch.model.user import User
from helpers.login import login_as, log_out, check_allowed

# Makes a draft of the mod and returns the `DraftMod`.
def mk_draft(db, mod, user=None):
    if not user: user = User.query.first()
    draft = mod.make_draft(user)
    db.add(draft)
    db.commit()
    return draft

def test_mk_draft(client, sample_users, sample_mods):
    mod = sample_mods[0]
    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.new_draft', slug=mod.slug), follow_redirects=True)
    assert mod.name.encode('utf-8') in rv.data

    # Check the DB
    draft = DraftMod.query.filter_by(name=mod.name).first()
    assert draft != None, "Draft not found in DB"

def test_empty_draft(db_session, client, sample_users, sample_mods):
    """Ensures that drafts with no changes can't be merged."""
    mod = sample_mods[0]
    draft = mk_draft(db_session, mod, sample_users['admin'])

    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.draft_diff', id=draft.id), follow_redirects=True)
    assert b'no changes' in rv.data


# Test draft merging

def test_merge_draft(db_session, client, sample_users, sample_mods):
    mod = sample_mods[0]

    oldauthors = mod.authors

    draft = mk_draft(db_session, mod, sample_users['admin'])
    draft.name = "Changed 1"
    draft.desc = "Changed 2"
    draft.mod_vsns[0].desc = "Changed 3"
    db_session.commit()

    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.draft_diff', id=draft.id), follow_redirects=True)

    assert mod.name == draft.name
    assert mod.desc == draft.desc
    assert mod.authors == oldauthors

    mvsn = mod.find_same_child(draft.mod_vsns[0])
    assert mvsn.desc == draft.mod_vsns[0].desc

def test_merge_new_version_draft(db_session, client, sample_users, sample_mods):
    mod = sample_mods[0]

    oldauthors = mod.authors

    draft = mk_draft(db_session, mod, sample_users['admin'])
    draft.mod_vsns.append(DraftModVersion(
        name='6.9',
        desc='Testing',
    ))
    db_session.commit()

    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.draft_diff', id=draft.id), follow_redirects=True)

    mvsn = mod.find_same_child(draft.mod_vsns[0])
    assert mvsn.name == draft.mod_vsns[0].name
    assert mvsn.desc == draft.mod_vsns[0].desc

def test_merge_new_mod_draft(db_session, client, sample_users, sample_mods):
    draft = DraftMod(
        name="New Mod", desc="This is a draft of a new mod",
        authors=[ModAuthor(name="testing")],
        user=sample_users['admin'],
        mod_vsns=[
            DraftModVersion(
                name='6.9',
                desc='Testing',
                game_vsns=[GameVersion(name='1.7.10')]
            )
        ]
    )
    db_session.add(draft)
    db_session.commit()

    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.draft_diff', id=draft.id), follow_redirects=True, data=dict(
        slug='added'
    ))
    print(rv.data)

    mod = Mod.query.filter_by(slug='added').first()
    assert mod.name == draft.name
    assert mod.desc == draft.desc
    assert mod.authors == draft.authors
    assert mod.mod_vsns[0].name == draft.mod_vsns[0].name
    assert mod.mod_vsns[0].desc == draft.mod_vsns[0].desc
    assert mod.mod_vsns[0].game_vsns == draft.mod_vsns[0].game_vsns


# Test editor UI

def test_new_mod(client, sample_users, sample_mods):
    author = ModAuthor.query.filter_by(name='tester').first()
    data = dict(
        name='New Test Mod', website='', authors=','.join([author.name, 'newauthor']),
        desc='This is a test',
    )

    author2 = ModAuthor.query.filter_by(name='newauthor').first()
    assert author2 == None

    login_as(client, sample_users['admin'])
    rv = client.post(url_for('edit.new_mod'), data=data, follow_redirects=True)
    assert data['name'].encode('utf-8') in rv.data

    # Check the DB
    mod = DraftMod.query.filter_by(name=data['name']).first()
    author2 = ModAuthor.query.filter_by(name='newauthor').first()
    assert mod != None, "Added mod not found in DB"
    assert mod.name == data['name']
    assert mod.website == data['website']
    assert mod.desc == data['desc']
    assert mod.authors == [author, author2]

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

