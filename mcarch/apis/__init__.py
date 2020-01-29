from flask import Blueprint
from flask_restx import Api, Resource, fields

api_v1 = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(api_v1, version="1.0", title="MCArchive API", description="A test API for the MCArchive.", catch_all_404s=True)

from .mods import ns as mods
api.add_namespace(mods)
from .files import ns as files
api.add_namespace(files)
