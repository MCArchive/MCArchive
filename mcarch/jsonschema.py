"""This module provides JSON schemas for the mod database entries."""

from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

from mcarch.app import db
from mcarch.model.mod import *

class ModFileSchema(ModelSchema):
    class Meta:
        model = ModFile
        exclude = ('b2_path', 'local_path', 'redist', 'version')
        sqla_session = db.session

class ModAuthorSchema(ModelSchema):
    class Meta:
        model = ModAuthor
        sqla_session = db.session

class GameVersionSchema(ModelSchema):
    class Meta:
        model = GameVersion
        exclude = ('mod_vsns',)
        sqla_session = db.session

class ModVersionSchema(ModelSchema):
    files = fields.Nested(ModFileSchema, many=True, exclude=("version",))
    game_vsns = fields.Nested(GameVersionSchema, many=True, exclude=("mod_vsns",))
    class Meta:
        model = ModVersion
        sqla_session = db.session

class ModSchema(ModelSchema):
    mod_vsns = fields.Nested(ModVersionSchema, many=True, exclude=("mod",))
    authors = fields.Nested(ModAuthorSchema, many=True)
    class Meta:
        model = Mod
        sqla_session = db.session

