from . import api
from . import models

from mcarch.app import db
from mcarch.model.mod import Mod

from flask import request
from flask_restx import Resource, fields

ns = api.namespace('mods', 'Provides access to information about mods in the archive.')

@ns.route("/")
class ModsList(Resource):
    @api.doc("mod_list")
    @api.param('author', 'Optionally filter mods by author name', required=False)
    @api.param('game_version', 'Optionally filter mods by supported game versions', required=False)
    @api.param('keyword', 'Optionally filter mods by name', required=False)
    @api.marshal_with(models.mod, skip_none=True, mask='{slug,name}')
    def get(self, **kwargs):
        '''Returns a list of all available mods.'''
        by_author = request.args.get('author')
        by_gvsn = request.args.get('game_version')
        kw = request.args.get('keyword')
        filters = {}
        if by_author:
            filters['author'] = by_author
        if by_gvsn:
            filters['game_vsn'] = by_gvsn
        if kw:
            filters['keyword'] = kw

        return Mod.search_query(**filters).all()

@ns.route("/by_slug/<slug>")
class ModBySlug(Resource):
    @api.doc("mod_info_by_slug")
    @api.marshal_with(models.mod_all, skip_none=True, mask='{}')
    def get(self, slug, **kwargs):
        '''Returns info on a specific mod and its versions'''
        return Mod.query.filter(Mod.slug == slug, Mod.redist == True).first_or_404()
