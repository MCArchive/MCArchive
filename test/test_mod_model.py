import pytest
from flask import url_for

from mcarch.model.mod import Mod, ModVersion, ModFile, ModAuthor, GameVersion

import re


@pytest.fixture
def sample_mod(db_session):
    mod = Mod(
        name="Test", slug="test", desc="This is a test",
        authors=[
            ModAuthor(name="tester")
        ],
        mod_vsns=[
            ModVersion(
                name='4.2.0',
                desc='This is a test',
                game_vsns=[GameVersion(name='1.2.5')],
                files=[
                    ModFile(filename='test-4.2.0.jar', sha256='fake')
                ]
            ),
            ModVersion(
                name='1.3.3.7',
                desc='This is another test',
                game_vsns=[GameVersion(name='b1.7.3')],
                files=[
                    ModFile(filename='test-1.3.3.7-client.jar', sha256='fakeclient'),
                    ModFile(filename='test-1.3.3.7-server.jar', sha256='fakeserver'),
                ]
            ),
        ]
    )
    db_session.add(mod)
    db_session.commit()
    return mod

def test_copy(sample_mod):
    """Checks that the home page renders with no channels added."""
    copy = sample_mod.copy(slug='copy')
    assert copy.name == sample_mod.name
    assert copy.desc == sample_mod.desc
    assert len(copy.mod_vsns) == len(sample_mod.mod_vsns)
    assert copy.mod_vsns[0].name == sample_mod.mod_vsns[0].name
    assert len(copy.mod_vsns[0].files) == len(sample_mod.mod_vsns[0].files)
    assert copy.mod_vsns[0].files[0].sha256 == sample_mod.mod_vsns[0].files[0].sha256

def test_diff(sample_mod):
    sm = sample_mod

    copy = sm.copy(slug='copy')
    copy.name = 'changed'
    copy.mod_vsns[0].desc = 'changed'
    copy.mod_vsns[1].files[0].sha256 = 'changed'

    diff = sm.diff(copy)
    print('Diff: {}'.format(diff))
    assert diff['name']['old'] == sm.name
    assert diff['name']['new'] == copy.name
    assert diff['children']['changed'][0]['changes']['desc']['old'] == sm.mod_vsns[0].desc
    assert diff['children']['changed'][0]['changes']['desc']['new'] == copy.mod_vsns[0].desc

def test_diff_add(sample_mod):
    sm = sample_mod

    copy = sm.copy(slug='copy')
    copy.mod_vsns.append(ModVersion(
        name='6.9',
        desc='This is also a test',
        game_vsns=[GameVersion(name='a1.2.3')],
        files=[
            ModFile(filename='test-6.9-client.jar', sha256='fakeclient2'),
            ModFile(filename='test-6.9-server.jar', sha256='fakeserver2'),
        ]
    ))

    diff = sm.diff(copy)
    print('Diff: {}'.format(diff))
    assert diff['children']['added'][0] == copy.mod_vsns[2]

def test_diff_rm(sample_mod):
    sm = sample_mod

    copy = sm.copy(slug='copy')
    del copy.mod_vsns[0]

    diff = sm.diff(copy)
    print('Diff: {}'.format(diff))
    assert diff['children']['removed'][0] == sm.mod_vsns[0]

