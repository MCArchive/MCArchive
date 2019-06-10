from collections import OrderedDict

from .base import *

from sqlalchemy_continuum import make_versioned
from mcarch.app import db

make_versioned(user_cls='User', options={'table_name': '%s_log'})

authored_by_table = mk_authored_by_table('mod')
for_game_vsn_table = mk_for_game_vsn_table('mod_version')

class Mod(ModBase, db.Model):
    __tablename__ = "mod"
    slug = db.Column(db.String(80), nullable=False, unique=True)

    authors = db.relationship(
        "ModAuthor",
        secondary=authored_by_table,
        backref="mods")
    mod_vsns = db.relationship("ModVersion", back_populates="mod")

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

    def blank(self, **kwargs): return Mod(**kwargs)

class ModVersion(ModVersionBase, db.Model):
    __tablename__ = "mod_version"
    mod_id = db.Column(db.Integer, db.ForeignKey('mod.id'))
    mod = db.relationship("Mod", back_populates="mod_vsns")
    game_vsns = db.relationship(
        "GameVersion",
        secondary=for_game_vsn_table,
        backref="mod_vsns")
    files = db.relationship("ModFile", back_populates="version")

    def blank(self, **kwargs): return ModVersion(**kwargs)

class ModFile(ModFileBase, db.Model):
    __tablename__ = "mod_file"
    version_id = db.Column(db.Integer, db.ForeignKey('mod_version.id'))
    version = db.relationship("ModVersion", back_populates="files")

    # Whether we're providing our own download links for this file.
    redist = db.Column(db.Boolean)

    def blank(self, **kwargs): return ModFile(**kwargs)

