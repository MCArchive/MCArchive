from . import api
from . import models

from mcarch.app import db
from mcarch.model.mod import Mod

from flask_restx import Resource, fields

ns = api.namespace('mods')

@ns.route("/")
class ModsList(Resource):
    @api.doc("mod_list")
    @api.marshal_with(models.mod, skip_none=True)
    def get(self, **kwargs):
        '''Returns a list of all available mods.'''
        return Mod.query.filter(Mod.redist == True).all()

@ns.route("/by_slug/<slug>")
class ModBySlug(Resource):
    @api.doc("mod_info_by_slug")
    @api.marshal_with(models.mod, skip_none=True)
    def get(self, slug, **kwargs):
        '''Returns info on a specific mod and its versions'''
        return Mod.query.filter(Mod.slug == slug, Mod.redist == True).first_or_404()
