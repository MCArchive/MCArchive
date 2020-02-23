from flask import Blueprint
from flask_restx import Api, Resource, fields

from mcarch.model.mod import ModAuthor, GameVersion

api_v1 = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(api_v1, version="1.0", title="MCArchive API", description="""
The MCArchive API provides access to information about the mods we have archived.

The endpoints on this API require an `X-Fields` header specifying which fields
of the object should be returned. We kindly ask that you avoid requesting extra
information that you don't need in order to conserve our server resources.

This API is currently undergoing a testing period for a couple days. During
this time, we may introduce some breaking changes. If you have any questions or
requests regarding the API, come talk to us on Discord.  After the testing
period is over, we will remove this notice and no more breaking changes will be
made to this version of the API.

The testing period is planned to end Tuesday, February 25, 2020.
""", catch_all_404s=True)

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
        '''Returns a list of game versions.'''
        return GameVersion.query.all()

