from .base import *

authored_by_table = mk_authored_by_table('draft_mod')
for_game_vsn_table = mk_for_game_vsn_table('draft_mod_version')

class DraftMod(ModBase, db.Model):
    """Represents pending changes to a mod."""
    __tablename__ = "draft_mod"

    # The user that owns this draft
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='drafts')

    # The version of a mod this draft was made on. If null, this draft represents
    # a new mod.
    base_id = db.Column(db.Integer, db.ForeignKey('log_mod.id'), nullable=True)
    base_vsn = db.relationship("LogMod")

    authors = db.relationship(
        "ModAuthor",
        secondary=authored_by_table)
    mod_vsns = db.relationship("DraftModVersion", back_populates="mod")

    def blank(self, **kwargs): return DraftMod(**kwargs)
    def blank_child(self, **kwargs): return DraftModVersion(**kwargs)
    def copy_from(self, other):
        assert hasattr(other, 'cur_id'), "Draft mod must copy from a log entry."
        self.base_id = other.id
        super(ModBase, self).copy_from(other)

    @property
    def current(self):
        """Returns this draft's current `Mod` entry. `None` if this is a draft of a new mod"""
        if self.base_vsn:
            return self.base_vsn.current
        else:
            return None

    def draft_diff(self):
        """Returns a diff representing changes made in this draft versus its base version."""
        if self.base_vsn:
            return self.base_vsn.diff(self)
        else:
            return None

class DraftModVersion(ModVersionBase, db.Model):
    __tablename__ = "draft_mod_version"
    mod_id = db.Column(db.Integer, db.ForeignKey('draft_mod.id'))
    mod = db.relationship("DraftMod", back_populates="mod_vsns")
    game_vsns = db.relationship(
        "GameVersion",
        secondary=for_game_vsn_table)
    files = db.relationship("DraftModFile", back_populates="version")

    # The version of a mod version this draft was made on. If null, this draft represents
    # a new version.
    base_id = db.Column(db.Integer, db.ForeignKey('log_mod_version.id'), nullable=True)
    base_vsn = db.relationship("LogModVersion")

    def blank(self, **kwargs): return DraftModVersion(**kwargs)
    def blank_child(self, **kwargs): return DraftModFile(**kwargs)
    def copy_from(self, other):
        assert hasattr(other, 'cur_id'), "Draft mod must copy from a log entry."
        self.base_id = other.id
        super(ModVersionBase, self).copy_from(other)

class DraftModFile(ModFileBase, db.Model):
    __tablename__ = "draft_mod_file"
    version_id = db.Column(db.Integer, db.ForeignKey('draft_mod_version.id'))
    version = db.relationship("DraftModVersion", back_populates="files")

    # The version of a mod file this draft was made on. If null, this draft represents
    # a new file.
    base_id = db.Column(db.Integer, db.ForeignKey('log_mod_file.id'), nullable=True)
    base_vsn = db.relationship("LogModFile")

    def blank(self, **kwargs): return DraftModFile(**kwargs)
    def copy_from(self, other):
        assert hasattr(other, 'cur_id'), "Draft mod must copy from a log entry."
        self.base_id = other.id
        super(ModFileBase, self).copy_from(other)

