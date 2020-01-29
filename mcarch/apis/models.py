from . import api

from flask_restx import fields

class ArchiveUrl(fields.Raw):
    def format(self, value):
        return value.b2_download_url()

game_version = api.model('Game Version', {
    'game_version': fields.String(attribute='name') 
})

file = api.model('File', {
    'uuid': fields.String,
    'name': fields.String,
    'description': fields.String(attribute='desc'),
    'page_url': fields.String,
    'redirect_url': fields.String,
    'direct_url': fields.String,
    'archive_url': ArchiveUrl(attribute='stored')
})

author = api.model('Author', {
    'name': fields.String,
    'description': fields.String(attribute='desc'),
    'website': fields.String,
})

mod = api.model('Mod', {
    'uuid': fields.String,
    'slug': fields.String,
    'name': fields.String,
    'description': fields.String(attribute='desc'),
    'website': fields.String,
    'authors': fields.List(fields.Nested(author, skip_none=True))
})

mod_version = api.model('Mod Version', {
    'mod': fields.Nested(mod, skip_none=True),
    'files': fields.List(fields.Nested(file, skip_none=True))
})

file_with_parent = api.inherit('File with Mod Information', file, {
    'mod_version': fields.Nested(mod_version, attribute='version')
})


