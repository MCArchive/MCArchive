from . import api

from flask_restx import fields

class ArchiveUrl(fields.Raw):
    def format(self, value):
        return value.b2_download_url()

game_version = api.model('Game Version', {
    'id': fields.Integer,
    'name': fields.String
})

author = api.model('Author', {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String(attribute='desc'),
    'website': fields.String,
})


mod_file = api.model('File', {
    'uuid': fields.String,
    'name': fields.String(attribute=lambda f: f.stored.name if f.stored else None),
    'sha256': fields.String(attribute=lambda f: f.stored.sha256 if f.stored else None),
    'description': fields.String(attribute='desc'),
    'page_url': fields.String,
    'redirect_url': fields.String,
    'direct_url': fields.String,
    'archive_url': ArchiveUrl(attribute='stored')
})


mod_version = api.model('Mod Version', {
    'uuid': fields.String,
    'name': fields.String,
    'page_url': fields.String(attribute='url'),
    'description': fields.String(attribute='desc'),
    'game_versions': fields.List(fields.Nested(game_version, skip_none=True), attribute='game_vsns')
})

mod_version_files = api.inherit('Mod Version with Files', mod_version, {
    'files': fields.List(fields.Nested(mod_file, skip_none=True))
})


mod = api.model('Mod', {
    'uuid': fields.String,
    'slug': fields.String,
    'name': fields.String,
    'description': fields.String(attribute='desc'),
    'website': fields.String,
    'authors': fields.List(fields.Nested(author, skip_none=True))
}, mask='{slug,name}')

mod_all = api.inherit('Mod Full', mod, {
    'mod_versions': fields.Nested(mod_version_files, attribute='mod_vsns')
})


mod_version_parent = api.inherit('Mod Version with Mod', mod_version, {
    'mod': fields.Nested(mod, skip_none=True)
})

file_with_version = api.inherit('File with Version', mod_file, {
    'mod_version': fields.Nested(mod_version_parent, attribute='version')
})

