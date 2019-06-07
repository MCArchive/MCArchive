from collections import OrderedDict

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_continuum import make_versioned

from util.sqla_uuid import GUID

from mcarch.app import db, bcrypt

make_versioned(user_cls='User', options={'table_name': '%s_log'})

# Association table for relation between authors and mods.
authored_by_table = db.Table('authored_by', db.Model.metadata,
    db.Column('mod_id', db.Integer,
        db.ForeignKey('mod.id', ondelete='CASCADE'), primary_key=True),
    db.Column('author_id', db.Integer,
        db.ForeignKey('author.id', ondelete='CASCADE'), primary_key=True)
)

# Association table for relation between Minecraft versions and mods.
for_game_vsn_table = db.Table('for_game_version', db.Model.metadata,
    db.Column('mod_vsn_id', db.Integer,
        db.ForeignKey('mod_version.id', ondelete='CASCADE'), primary_key=True),
    db.Column('game_vsn_id', db.Integer,
        db.ForeignKey('game_version.id', ondelete='CASCADE'), primary_key=True),
)


class Mod(db.Model):
    __versioned__ = {}
    __tablename__ = "mod"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.Text)
    website = db.Column(db.String(120))
    authors = db.relationship(
        "ModAuthor",
        secondary=authored_by_table,
        back_populates="mods")
    versions = db.relationship("ModVersion", back_populates="mod")

    def vsns_by_game_vsn(self):
        """
        Returns a dict mapping supported Minecraft versions to a list of
        versions of this mod that support that Minecraft version.
        """
        vsns = OrderedDict()
        for v in self.versions:
            vsns.setdefault(v.game_vsns[0].name, []).append(v)
        return vsns

    def game_versions(self):
        """Returns a list of game versions supported by all the versions of this mod."""
        gvs = GameVersion.query \
            .join(ModVersion, GameVersion.mod_vsns) \
            .filter(ModVersion.mod_id == self.id).all()
        gvsns = set()
        for gv in gvs:
            gvsns.add(gv.name)
        return sorted(list(gvsns))

    def game_versions_str(self):
        """Returns a comma separated string listing the supported game versions for this mod."""
        return ", ".join(map(lambda v: v, self.game_versions()))

class ModAuthor(db.Model):
    __versioned__ = {}
    __tablename__ = "author"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    desc = db.Column(db.Text)
    website = db.Column(db.String(120))
    mods = db.relationship(
        "Mod",
        secondary=authored_by_table,
        back_populates="authors")


class ModVersion(db.Model):
    __versioned__ = {}
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

    def game_versions_str(self):
        """Returns a comma separated string listing the supported game versions for this mod."""
        return ", ".join(map(lambda v: v.name, self.game_vsnsl))

class GameVersion(db.Model):
    __versioned__ = {}
    __tablename__ = "game_version"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    mod_vsns = db.relationship(
        "ModVersion",
        secondary=for_game_vsn_table,
        back_populates="game_vsns")


class ModFile(db.Model):
    __versioned__ = {}
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


