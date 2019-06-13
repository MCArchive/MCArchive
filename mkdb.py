# This file creates an empty SQLite database for development.

import sys

from mcarch.app import create_app, db
import mcarch.model

from mcarch.app import DevelopmentConfig
from mcarch.model.user import *
from mcarch.model.mod import *

def import_mod(obj, slug):
    mod = Mod(slug=slug, name=obj['name'])
    if 'desc' in obj: mod.desc=obj['desc']
    for name in obj['authors']:
        # Try to find the author in the database.
        auth = ModAuthor.query.filter_by(name=name).first()
        if auth is None:
            # Add a new author to the database.
            auth = ModAuthor(name=name)
        mod.authors.append(auth)
    for vsn in obj['versions']:
        mod.mod_vsns.append(import_mod_vsn(vsn))
    return mod

def import_mod_vsn(obj):
    vsn = ModVersion(name=obj['name'])
    if 'desc' in obj: vsn.desc=obj['desc']
    for name in obj['mcvsn']:
        # Try to find the game version in the database.
        gvsn = GameVersion.query.filter_by(name=name).first()
        if gvsn is None:
            print("Missing game version {}".format(name))
            exit(1)
        vsn.game_vsns.append(gvsn)
    for mfile in obj['files']:
        vsn.files.append(import_mod_file(mfile))
    return vsn

def import_mod_file(obj):
    mfile = ModFile(filename=obj['filename'], sha256=obj['hash']['digest'])
    if 'desc' in obj: mfile.desc=obj['desc']

    if 'urls' in obj:
        for url in obj['urls']:
            if url['type'] == 'page':
                mfile.page_url = url['url']
            elif url['type'] == 'original' and 'adf.ly' in url['url']:
                mfile.redirect_url = url['url']
            elif url['type'] == 'original':
                mfile.direct_url = url['url']

    return mfile

def import_game_vsns(mod):
    """Import game versions from a mod."""
    gvsns = []
    added = set()
    for vsn in mod['versions']:
        for name in vsn['mcvsn']:
            if name in added: continue
            gvsn = GameVersion.query.filter_by(name=name).first()
            if gvsn is None:
                added.add(name)
                gvsns.append(GameVersion(name=name))
    return gvsns


app = create_app(DevelopmentConfig)
with app.app_context():
    db.create_all()

    db.session.add(User(name="admin", password="a", email="test@example.com", role=UserRole.admin))
    db.session.add(User(name="mod", password="a", email="a@example.com", role=UserRole.moderator))
    db.session.add(User(name="arch", password="a", email="b@example.com", role=UserRole.archivist))
    db.session.add(User(name="user", password="a", email="c@example.com", role=UserRole.user))
    db.session.commit()

    if len(sys.argv) > 1:
        from os import listdir
        from os.path import isdir, isfile, join, splitext
        import yaml

        path = sys.argv[1]
        if not isdir(path):
            print("Expected metarepo directory to import as first argument")
            exit()
        print("Importing old archive files from {}".format(path))
        
        modyaml = {}
        for name in [f for f in listdir(path) if isfile(join(path, f))]:
            p = join(path, name)
            print("Loading YAML {}".format(p))
            obj = None
            with open(p, 'r') as f:
                modyaml[name] = yaml.load(f)

        for _, obj in modyaml.items():
            vsns = import_game_vsns(obj)
            for v in vsns: db.session.add(v)
            db.session.commit()

        for name, obj in modyaml.items():
            mod = import_mod(obj, splitext(name)[0])
            db.session.add(mod)
            db.session.commit()
            mod.log_change(user=None)
            db.session.commit()

    db.session.commit()

