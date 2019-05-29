from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from util.sqla_uuid import GUID

from mcarch.app import db, bcrypt

# Association table for relation between authors and mods.
authored_by_table = db.Table('authored_by', db.Model.metadata,
    db.Column('mod_id', db.Integer, db.ForeignKey('mod.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'))
)

# Association table for relation between Minecraft versions and mods.
for_game_vsn_table = db.Table('for_game_version', db.Model.metadata,
    db.Column('mod_vsn_id', db.Integer, db.ForeignKey('mod_version.id')),
    db.Column('game_vsn_id', db.Integer, db.ForeignKey('game_version.id'))
)


class Mod(db.Model):
    __tablename__ = "mod"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.Text)
    url = db.Column(db.String(120))
    authors = db.relationship(
        "ModAuthor",
        secondary=authored_by_table,
        back_populates="mods")
    versions = db.relationship("ModVersion", back_populates="mod")

class ModAuthor(db.Model):
    __tablename__ = "author"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    info = db.Column(db.Text)
    website = db.Column(db.String(120))
    mods = db.relationship(
        "Mod",
        secondary=authored_by_table,
        back_populates="authors")


class ModVersion(db.Model):
    __tablename__ = "mod_version"
    id = db.Column(db.Integer, primary_key=True)
    mod_id = db.Column(db.Integer, db.ForeignKey('mod.id'))
    mod = db.relationship("Mod", back_populates="versions")

    name = db.Column(db.String(40), nullable=False)
    desc = db.Column(db.Text)
    url = db.Column(db.String(120))
    game_vsns = db.relationship(
        "GameVersion",
        secondary=for_game_vsn_table,
        back_populates="mod_vsns")
    files = db.relationship("ModFile", back_populates="version")

class GameVersion(db.Model):
    __tablename__ = "game_version"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    mod_vsns = db.relationship(
        "ModVersion",
        secondary=for_game_vsn_table,
        back_populates="game_vsns")


class ModFile(db.Model):
    __tablename__ = "mod_file"
    id = db.Column(db.Integer, primary_key=True)
    version_id = db.Column(db.Integer, db.ForeignKey('mod_version.id'))
    version = db.relationship("ModVersion", back_populates="files")

    filename = db.Column(db.String(80), nullable=False)
    sha256 = db.Column(db.String(130), nullable=False)

    # Link to official web page with download links.
    page_url = db.Column(db.String(120))
    # Official download link through redirect such as adfly.
    redirect_url = db.Column(db.String(120))
    # Official direct file download link.
    direct_url = db.Column(db.String(120))

    # Path to the file on the local filesystem.
    local_path = db.Column(db.String(200))

    # Path to the file on B2 cloud storage.
    b2_path = db.Column(db.String(200))

    # Whether we're providing our own download links for this file.
    redist = db.Column(db.Boolean)



def import_mod(obj):
    mod = Mod(name=obj['name'])
    if 'desc' in obj: mod.desc=obj['desc']
    for name in obj['authors']:
        # Try to find the author in the database.
        auth = ModAuthor.query.filter_by(name=name).first()
        if auth is None:
            # Add a new author to the database.
            auth = ModAuthor(name=name)
        mod.authors.append(auth)
    for vsn in obj['versions']:
        mod.versions.append(import_mod_vsn(vsn))
    return mod

def import_mod_vsn(obj):
    vsn = ModVersion(name=obj['name'])
    if 'desc' in obj: vsn.desc=obj['desc']
    for name in obj['mcvsn']:
        # Try to find the game version in the database.
        gvsn = GameVersion.query.filter_by(name=name).first()
        if gvsn is None:
            # Add a new game version to the database.
            gvsn = GameVersion(name=name)
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

