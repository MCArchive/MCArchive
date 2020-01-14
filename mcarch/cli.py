from flask import Blueprint, url_for
import click
from getpass import getpass
import yaml
import sys
import os

from mcarch.app import db, current_app as app
from mcarch.model.user import *
from mcarch.model.mod import *
from mcarch.model.file import *

bp = Blueprint('commands', __name__, cli_group=None)

def role_from_str(s):
    strs = dict(
        user=roles.user,
        archivist=roles.archivist,
        moderator=roles.moderator,
        admin=roles.admin
    )
    if s in strs: return strs[s]
    else: return None

@bp.cli.command('adduser')
@click.argument('name')
@click.argument('email')
@click.argument('role')
def add_user(name, email, role):
    role = role_from_str(role)
    if not role:
        print("Error: no such role {}".format(role))
        return

    while True:
        password = getpass("Password for {}: ".format(name))
        if password != getpass("Repeat password: "):
            print("Passwords didn't match")
            continue
        else: break

    user = User(name=name, email=email, role=role, password=password)
    db.session.add(user)
    db.session.commit()

    print('User {} created'.format(name))


@bp.cli.command('import')
@click.argument('path')
def import_old_format(path):
    from os import listdir
    from os.path import isdir, isfile, join, splitext

    print("Importing old archive format from {}", path)

    modyaml = {}
    for name in [f for f in listdir(path) if isfile(join(path, f))]:
        p = join(path, name)
        print("Loading YAML {}".format(p))
        obj = None
        with open(p, 'r') as f:
            modyaml[name] = yaml.safe_load(f)

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
    print("Import complete")


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
    mfile = ModFile()
    if 'desc' in obj: mfile.desc=obj['desc']

    if 'urls' in obj:
        for url in obj['urls']:
            if url['type'] == 'page':
                mfile.page_url = url['url']
            elif url['type'] == 'original' and 'adf.ly' in url['url']:
                mfile.redirect_url = url['url']
            elif url['type'] == 'original':
                mfile.direct_url = url['url']
    mfile.stored = import_b2_stored_file(obj)
    return mfile

def import_b2_stored_file(obj):
    """Imports a StoredFile that's already in the local storage directory."""
    filehash = obj['hash']['digest']
    path = os.path.join(filehash, obj['filename'])
    print('Import stored file {}'.format(path))
    sfile = StoredFile(name=obj['filename'], sha256=obj['hash']['digest'], b2_path=path)
    return sfile

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

