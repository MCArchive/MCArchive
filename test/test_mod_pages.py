"""
This module contains basic tests that make sure all the pages in the `mods` module render without
major problems.
"""


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

def test_authors(client, sample_gvsns):
    rv = client.get('/gamevsns')
    for v in sample_gvsns:
        assert v.name.encode('utf-8') in rv.data

def test_(client, sample_mods):
    rv = client.get('/mods')
    assert sample_mods[0].name.encode('utf-8') in rv.data

