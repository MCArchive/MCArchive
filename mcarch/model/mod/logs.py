"""
This module contains models for "logs" which are change submissions for mods.
"""

from datetime import datetime
from collections import OrderedDict
from sqlalchemy.orm import backref

from .base import *

from mcarch.model.user import User
from mcarch.app import db

def gen_diffs(mod):
    """
    Takes a mod and generates a list of diffs representing the changes made in each log entry.
    """
    logs = mod.logs
    for i, log in enumerate(logs):
        diff = None
        if i > 0: diff = logs[i-1].diff(log)
        else: diff = LogMod().diff(log)
        yield {
            'obj': log,
            'user': log.user,
            'approved_by': log.approved_by,
            'date': log.date,
            'diff': diff,
        }

def slow_gen_diffs(logs):
    """
    Unlike regular `gen_diffs`, this takes a list of logs entries that aren't
    all for the same mod, and returns a list of diffs between each one and its
    previous version. This is probably much slower than `gen_diffs` since it
    queries the database for the entry previous to each one in the list.
    """
    for i, log in enumerate(logs):
        prev = LogMod.query.filter_by(cur_id=log.cur_id, index=log.index-1).first()
        diff = prev.diff(log) if prev else LogMod().diff(log)
        yield {
            'obj': log,
            'user': log.user,
            'approved_by': log.approved_by,
            'date': log.date,
            'diff': diff,
        }


authored_by_table = mk_authored_by_table('log_mod')
for_game_vsn_table = mk_for_game_vsn_table('log_mod_version')

class LogMod(ModBase, db.Model):
    """Represents a change made to a mod."""
    __tablename__ = "log_mod"

    # The user that made this change.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', foreign_keys=[user_id], backref='changes')

    # The moderator that approved this draft
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])

    # Date this change was made.
    date = db.Column(db.DateTime, default=datetime.utcnow)

    cur_id = db.Column(db.Integer, db.ForeignKey('mod.id'), nullable=True)
    current = db.relationship("Mod", backref=backref("logs", order_by='LogMod.date'))

    # Index within this mod's list of versions.
    index = db.Column(db.Integer, nullable=False)

    authors = db.relationship(
        "ModAuthor",
        secondary=authored_by_table)
    mod_vsns = db.relationship("LogModVersion", back_populates="mod")

    def blank(self, **kwargs): return LogMod(**kwargs)
    def blank_child(self, **kwargs): return LogModVersion(**kwargs)
    def copy_from(self, other):
        if hasattr(other, 'cur_id'): self.cur_id = other.cur_id
        self.cur_id = other.id
        super(ModBase, self).copy_from(other)

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
        if hasattr(other, 'cur_id'): self.cur_id = other.cur_id
        self.cur_id = other.id
        super(ModVersionBase, self).copy_from(other)

class LogModFile(ModFileBase, db.Model):
    __tablename__ = "log_mod_file"
    version_id = db.Column(db.Integer, db.ForeignKey('log_mod_version.id'))
    version = db.relationship("LogModVersion", back_populates="files")

    cur_id = db.Column(db.Integer, db.ForeignKey('mod_file.id'), nullable=True)
    current = db.relationship("ModFile")

    def blank(self, **kwargs): return LogModFile(**kwargs)
    def copy_from(self, other):
        if hasattr(other, 'cur_id'): self.cur_id = other.cur_id
        self.cur_id = other.id
        super(ModFileBase, self).copy_from(other)

