from collections import OrderedDict

from sqlalchemy.ext.declarative import declared_attr

from mcarch.app import db
from mcarch.util.copydiff import CopyDiff
from mcarch.model.file import StoredFile

def mk_authored_by_table(mod_table):
    """Generates an association table between mods and the author table"""
    return db.Table('{}_authored_by'.format(mod_table), db.Model.metadata,
        db.Column('mod_id', db.Integer,
            db.ForeignKey('{}.id'.format(mod_table), ondelete='CASCADE'), primary_key=True),
        db.Column('author_id', db.Integer,
            db.ForeignKey('author.id', ondelete='CASCADE'), primary_key=True)
    )

def mk_for_game_vsn_table(mod_vsn_table):
    """Generates an assocation table between mod versions and the game version table"""
    return db.Table('{}_for_game_version'.format(mod_vsn_table), db.Model.metadata,
        db.Column('mod_vsn_id', db.Integer,
            db.ForeignKey('{}.id'.format(mod_vsn_table), ondelete='CASCADE'), primary_key=True),
        db.Column('game_vsn_id', db.Integer,
            db.ForeignKey('game_version.id', ondelete='CASCADE'), primary_key=True),
    )


#### Mixins for mod tables ####
# Fields are shared between Mod and LogMod

class ModBase(CopyDiff):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.Text)
    website = db.Column(db.String(120))

    def vsns_by_game_vsn(self):
        """
        Returns a dict mapping supported Minecraft versions to a list of
        versions of this mod that support that Minecraft version.
        """
        vsns = OrderedDict()
        for v in self.mod_vsns:
            vsns.setdefault(v.game_vsns[0].name, []).append(v)
        return vsns

    # Methods for CopyDiff
    def copydiff_fields(self): return ['name', 'desc', 'website', 'authors']
    def get_children(self): return self.mod_vsns
    def add_child(self, ch): self.mod_vsns.append(ch)
    def rm_child(self, ch): self.mod_vsns.remove(ch)

class ModVersionBase(CopyDiff):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(40), nullable=False)
    desc = db.Column(db.Text)
    url = db.Column(db.String(120))

    def game_versions_str(self):
        """Returns a comma separated string listing the supported game versions for this mod."""
        return ", ".join(map(lambda v: v.name, self.game_vsns))

    def copydiff_fields(self): return ['name', 'desc', 'url', 'game_vsns']
    def get_children(self): return self.files
    def add_child(self, ch): self.files.append(ch)
    def rm_child(self, ch): self.files.remove(ch)

class ModFileBase(CopyDiff):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    desc = db.Column(db.Text)

    @declared_attr
    def stored_id(cls):
        return db.Column(db.Integer, db.ForeignKey('stored_file.id'), nullable=True)

    @declared_attr
    def stored(cls):
        return db.relation('StoredFile')

    # Link to official web page with download links.
    page_url = db.Column(db.String(120))
    # Official download link through redirect such as adfly.
    redirect_url = db.Column(db.String(120))
    # Official direct file download link.
    direct_url = db.Column(db.String(120))

    def copydiff_fields(self):
        return ['stored', 'page_url', 'redirect_url', 'direct_url']
    def get_children(self): return []


# These models are shared between Mod and LogMod.

class ModAuthor(db.Model):
    __versioned__ = {}
    __tablename__ = "author"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    desc = db.Column(db.Text)
    website = db.Column(db.String(120))

class GameVersion(db.Model):
    __versioned__ = {}
    __tablename__ = "game_version"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)

