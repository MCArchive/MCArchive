import pytest
from flask import url_for

from mcarch.model.mod import Mod, ModVersion, ModFile, ModAuthor, GameVersion
from mcarch.model.file import StoredFile

import re



def test_log(sample_mod):
    sm = sample_mod
    entry = sm.log_change(user=None)
    assert entry.name == sample_mod.name
    assert entry.desc == sample_mod.desc
    assert len(entry.mod_vsns) == len(sample_mod.mod_vsns)
    assert entry.mod_vsns[0].name == sample_mod.mod_vsns[0].name
    assert len(entry.mod_vsns[0].files) == len(sample_mod.mod_vsns[0].files)
    assert entry.mod_vsns[0].files[0].stored.sha256 == sample_mod.mod_vsns[0].files[0].stored.sha256

def test_copy(sample_mod):
    copy = sample_mod.copy(slug='copy')
    assert copy.name == sample_mod.name
    assert copy.desc == sample_mod.desc
    assert len(copy.mod_vsns) == len(sample_mod.mod_vsns)
    assert copy.mod_vsns[0].name == sample_mod.mod_vsns[0].name
    assert len(copy.mod_vsns[0].files) == len(sample_mod.mod_vsns[0].files)
    assert copy.mod_vsns[0].files[0].stored.sha256 == sample_mod.mod_vsns[0].files[0].stored.sha256

def test_same_as(sample_mod, db_session):
    sm = sample_mod

    assert sm.same_as(sm.logs[0])
    assert sm.logs[0].same_as(sm)
    assert sm.mod_vsns[0].same_as(sm.logs[0].mod_vsns[0])
    assert sm.logs[0].mod_vsns[0].same_as(sm.mod_vsns[0])

    sm.mod_vsns.append(ModVersion(
        name='6.9',
        game_vsns=[GameVersion(name='a1.2.4')],
        files=[
            ModFile(stored=StoredFile(name='test-6.9-client.jar', sha256='fakeclient2')),
        ]
    ))

    sm.log_change(user=None)
    db_session.commit()

    assert sm.logs[0].same_as(sm.logs[1])
    assert sm.logs[1].same_as(sm.logs[0])
    assert sm.logs[0].same_as(sm)
    assert sm.logs[1].same_as(sm)
    assert sm.logs[0].mod_vsns[0].same_as(sm.logs[1].mod_vsns[0])
    assert sm.logs[1].mod_vsns[0].same_as(sm.logs[0].mod_vsns[0])

    assert sm.same_as(sm.logs[1])
    assert sm.same_as(sm.logs[0])

def test_diff(sample_mod, db_session):
    sm = sample_mod

    sm.name = 'changed'
    sm.mod_vsns[0].desc = 'changed'
    sm.mod_vsns[1].files[0].stored.sha256 = 'changed'

    log = sm.log_change(user=None)
    db_session.commit()

    diff = sm.logs[0].diff(log)
    print('Diff: {}'.format(diff))
    assert diff['name']['old'] == sm.logs[0].name
    assert diff['name']['new'] == log.name
    assert diff['children']['changed'][0]['changes']['desc']['old'] == sm.logs[0].mod_vsns[0].desc
    assert diff['children']['changed'][0]['changes']['desc']['new'] == log.mod_vsns[0].desc

def test_log_add(sample_mod, db_session):
    sm = sample_mod

    sm.mod_vsns.append(ModVersion(
        name='6.9',
        desc='This is also a test',
        game_vsns=[GameVersion(name='a1.2.4')],
        files=[
            ModFile(stored=StoredFile(name='test-6.9-client.jar', sha256='fakeclient2')),
            ModFile(stored=StoredFile(name='test-6.9-server.jar', sha256='fakeserver2')),
        ]
    ))
    log = sm.log_change(user=None)
    db_session.commit()

    diff = sm.logs[0].diff(log)
    print('Diff: {}'.format(diff))
    assert diff['children']['added'][0] == log.mod_vsns[2]

def test_diff_rm(sample_mod, db_session):
    sm = sample_mod

    del sm.mod_vsns[0]
    log = sm.log_change(user=None)
    db_session.commit()

    diff = sm.logs[0].diff(log)
    print('Diff: {}'.format(diff))
    assert diff['children']['removed'][0] == sm.logs[0].mod_vsns[0]

def test_diff_no_child_changes(sample_mod, db_session):
    sm = sample_mod
    log1 = sm.logs[0]
    sm.name = 'test'
    log2 = sm.log_change(user=None)
    diff = log1.diff(log2)
    db_session.add(log2)
    db_session.commit()
    print('Diff: {}'.format(diff))
    assert diff['name']['old'] == log1.name
    assert diff['name']['new'] == log2.name
    assert 'children' not in diff

def test_revert_to(sample_mod, db_session):
    sm = sample_mod

    sm.name = 'changed'
    sm.mod_vsns[0].name = 'changed'
    sm.mod_vsns[0].files[0].name = 'changed'
    sm.mod_vsns.append(ModVersion(
        name='6.9',
        game_vsns=[GameVersion(name='a1.2.4')],
        files=[
            ModFile(stored=StoredFile(name='test-6.9-client.jar', sha256='fakeclient2')),
        ]
    ))
    sm.log_change(user=None)
    db_session.commit()

    assert sm.name == 'changed'

    # Revert back to original form
    sm.revert_to(sm.logs[0])

    assert sm.name == sm.logs[0].name
    assert sm.mod_vsns[0].name == sm.logs[0].mod_vsns[0].name
    assert sm.mod_vsns[0].files[0].stored.name == sm.logs[0].mod_vsns[0].files[0].stored.name
    assert len(sm.mod_vsns) == len(sm.logs[0].mod_vsns)

