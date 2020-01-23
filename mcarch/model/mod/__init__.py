from .base import *
from .logs import LogMod, LogModVersion, LogModFile
from .draft import DraftMod, DraftModVersion, DraftModFile

from mcarch.app import db

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

    # If this is set to false, the mod will be de-listed.
    redist = db.Column(db.Boolean, nullable=False, default=True)

    @staticmethod
    def search_query(game_vsn=None, author=None, keyword=None,
            include_delisted=False):
        """
        Returns a pre-made standard search query for listing mods. Optional
        parameters may be specified for filtering.
        """
        query = Mod.query
        if not include_delisted:
            query = query.filter_by(redist=True)
        if author and len(author) > 0:
            query = query.join(ModAuthor, Mod.authors).filter(ModAuthor.name == author)
        if game_vsn and len(game_vsn) > 0:
            query = query.join(ModVersion) \
                                .join(GameVersion, ModVersion.game_vsns) \
                                .filter(GameVersion.name == game_vsn)
        if keyword and len(keyword) > 0:
            query = query.filter(Mod.name.ilike("%"+keyword+"%"))
        return query

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
    def blank_child(self, **kwargs): return ModVersion(**kwargs)

    def log_change(self, user, approved_by=None):
        """
        Logs a new change for this mod.

        Assigns the change to `user`, and if `approved_by` is not `None`,
        assigns them as the user who approved it.
        """
        entry = LogMod(user=user, approved_by=approved_by, cur_id=self.id, index=len(self.logs))
        entry.copy_from(self)
        db.session.add(entry)
        return entry

    @property
    def latest_vsn(self):
        # FIXME: This could probably be done faster with a DB query.
        return self.logs[len(self.logs)-1]

    def make_draft(self, user):
        """Creates a DraftMod based on the latest version of this mod."""
        latest = self.latest_vsn
        draft = DraftMod(user=user)
        draft.copy_from(latest)
        return draft

    def revert_to(self, log):
        """
        Takes a `ModLog` and reverts this mod to its state at the time of that log entry.
        Raises `ValueError` if the given log entry is not for this mod.
        """
        if log.cur_id != self.id:
            raise ValueError('Log entry {} is not for mod {}'.format(log, self))
        self.copy_from(log)

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
    def blank_child(self, **kwargs): return ModFile(**kwargs)

class ModFile(ModFileBase, db.Model):
    __tablename__ = "mod_file"
    version_id = db.Column(db.Integer, db.ForeignKey('mod_version.id'))
    version = db.relationship("ModVersion", back_populates="files")

    # Whether we're providing our own download links for this file.
    redist = db.Column(db.Boolean)

    def blank(self, **kwargs): return ModFile(**kwargs)

