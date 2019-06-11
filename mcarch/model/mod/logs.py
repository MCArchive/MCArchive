"""
This module contains models for "logs" which are change submissions for mods.
"""

import datetime
from collections import OrderedDict
from sqlalchemy.orm import backref

from .base import *

from mcarch.model.user import User
from mcarch.app import db

authored_by_table = mk_authored_by_table('log_mod')
for_game_vsn_table = mk_for_game_vsn_table('log_mod_version')

class LogMod(ModBase, db.Model):
    """Represents a change made to a mod."""
    __tablename__ = "log_mod"

    # The user that made this change.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref='changes')

    # Date this change was made.
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    cur_id = db.Column(db.Integer, db.ForeignKey('mod.id'), nullable=True)
    current = db.relationship("Mod", backref=backref("logs", order_by='LogMod.date'))

    authors = db.relationship(
        "ModAuthor",
        secondary=authored_by_table)
    mod_vsns = db.relationship("LogModVersion", back_populates="mod")

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

    def blank(self, **kwargs): return LogMod(**kwargs)
    def blank_child(self, **kwargs): return LogModVersion(**kwargs)

    def copy_from(self, other):
        self.mod_id = other.id
        super(ModBase, self).copy_from(other)
    def same_as(self, other):
        return self.id == other.id or other.id == self.cur_id \
            or (hasattr(other, 'cur_id') and other.cur_id == self.cur_id)

class LogModVersion(ModVersionBase, db.Model):
    __tablename__ = "log_mod_version"
    mod_id = db.Column(db.Integer, db.ForeignKey('log_mod.id'))
    mod = db.relationship("LogMod", back_populates="mod_vsns")
    game_vsns = db.relationship(
        "GameVersion",
        secondary=for_game_vsn_table)
    files = db.relationship("LogModFile", back_populates="version")

    cur_id = db.Column(db.Integer, db.ForeignKey('mod_version.id'), nullable=True)
    current = db.relationship("ModVersion")

    def blank(self, **kwargs): return LogModVersion(**kwargs)
    def blank_child(self, **kwargs): return LogModFile(**kwargs)
    def copy_from(self, other):
        self.cur_id = other.id
        super(ModVersionBase, self).copy_from(other)
    def same_as(self, other):
        return self.id == other.id or other.id == self.cur_id \
            or (hasattr(other, 'cur_id') and other.cur_id == self.cur_id)

class LogModFile(ModFileBase, db.Model):
    __tablename__ = "log_mod_file"
    version_id = db.Column(db.Integer, db.ForeignKey('log_mod_version.id'))
    version = db.relationship("LogModVersion", back_populates="files")

    cur_id = db.Column(db.Integer, db.ForeignKey('mod_file.id'), nullable=True)
    current = db.relationship("ModFile")

    redist = False

    def blank(self, **kwargs): return LogModFile(**kwargs)
    def copy_from(self, other):
        self.cur_id = other.id
        super(ModFileBase, self).copy_from(other)
    def same_as(self, other):
        return self.id == other.id or other.id == self.cur_id \
            or (hasattr(other, 'cur_id') and other.cur_id == self.cur_id)

