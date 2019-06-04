"""This module provides JSON schemas for the mod database entries."""

from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

from mcarch.model.mod import *

class ModFileSchema(ModelSchema):
    class Meta:
        model = ModFile
        exclude = ('b2_path', 'local_path', 'redist', 'version')

class ModAuthorSchema(ModelSchema):
    class Meta:
        model = ModAuthor
        exclude = ('mods',)

class GameVersionSchema(ModelSchema):
    class Meta:
        model = GameVersion
        exclude = ('mod_vsns',)

class ModVersionSchema(ModelSchema):
    files = fields.Nested(ModFileSchema, many=True, exclude=("version",))
    game_vsns = fields.Nested(GameVersionSchema, many=True, exclude=("mod_vsns",))
    class Meta:
        model = ModVersion

class ModSchema(ModelSchema):
    versions = fields.Nested(ModVersionSchema, many=True, exclude=("mod",))
    authors = fields.Nested(ModAuthorSchema, many=True, exclude=("mods",))
    class Meta:
        model = Mod


