import json

def find_by_id(objs, id):
    for obj in objs:
        if obj.id == id: return obj
    assert False, "Found no object with ID {} in {}".format(id, objs)

def find_by_slug(objs, slug):
    for obj in objs:
        if obj.slug == slug: return obj
    assert False, "Found no object with ID {} in {}".format(slug, objs)

def find_by_uuid(objs, uuid):
    for obj in objs:
        if str(obj.uuid) == str(uuid): return obj
    assert False, "Found no object with UUID {} in {}".format(uuid, objs)

def test_authors(client, sample_authors):
    rv = client.get('/api/v1/authors',
            headers={ 'X-Fields': '*' })
    objs = json.loads(rv.data)
    for a in objs:
        match = find_by_id(sample_authors, a['id'])
        assert a['name'] == match.name

def test_mod_list(client, sample_mods):
    rv = client.get('/api/v1/mods/',
            headers={ 'X-Fields': '*' })
    objs = json.loads(rv.data)
    for a in objs:
        match = find_by_uuid(sample_mods, a['uuid'])
        assert a['name'] == match.name
        assert a['slug'] == match.slug
        assert a['description'] == match.desc
        assert a['website'] == match.website

def test_mod_by_slug(client, sample_mods):
    rv = client.get('/api/v1/mods/by_slug/guide',
            headers={ 'X-Fields': '*' })
    obj = json.loads(rv.data)
    match = find_by_slug(sample_mods, 'guide')
    assert obj['name'] == match.name
    assert obj['slug'] == match.slug
    assert obj['description'] == match.desc
    assert obj['website'] == match.website

def test_files_by_hash(client, sample_mods):
    rv = client.get('/api/v1/files/by_hash/sha256/theanswer',
            headers={ 'X-Fields': '*' })
    assert b'theanswer' in rv.data
    assert b'guide-4.2.jar' in rv.data
    assert b"Don't Panic" in rv.data

def test_files_by_name(client, sample_mods):
    rv = client.get('/api/v1/files/by_filename/guide-4.2.jar',
            headers={ 'X-Fields': '*' })
    assert b'theanswer' in rv.data
    assert b'guide-4.2.jar' in rv.data
    assert b"Don't Panic" in rv.data

