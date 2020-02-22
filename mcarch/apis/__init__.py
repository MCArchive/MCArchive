from flask import Blueprint
from flask_restx import Api, Resource, fields

from mcarch.model.mod import ModAuthor, GameVersion

api_v1 = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(api_v1, version="1.0", title="MCArchive API",
        description="A test API for the MCArchive.", catch_all_404s=True)

from .mods import ns as mods
api.add_namespace(mods)
from .files import ns as files
api.add_namespace(files)

from . import models

@api.route("/authors")
class Authors(Resource):
    @api.doc("authors")
    @api.marshal_with(models.author, skip_none=True, mask='{id, name}')
    def get(self, **kwargs):
        '''Returns a list of mod authors.'''
        return ModAuthor.query.all()

@api.route("/game_versions")
class GameVersions(Resource):
    @api.doc("game_versions")
    @api.marshal_with(models.game_version, skip_none=True, mask='{id, name}')
    def get(self, **kwargs):
        '''Returns a list of mod authors.'''
        return GameVersion.query.all()

