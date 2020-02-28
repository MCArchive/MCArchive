from . import api

from flask_restx import fields

class ArchiveUrl(fields.Raw):
    def format(self, value):
        if value.should_redist:
            return value.stored.b2_download_url()

game_version = api.model('Game Version', {
    'id': fields.Integer(example=19),
    'name': fields.String(example="b1.7.3")
})

author = api.model('Author', {
    'id': fields.Integer(example=48),
    'name': fields.String(example="Forkk"),
    'description': fields.String(attribute='desc'),
    'website': fields.String(example="https://example.com"),
})


mod_file = api.model('File', {
    'uuid': fields.String(example="08f15883-bf6a-420d-b770-639a2551fbbe"),
    'name': fields.String(attribute=lambda f: f.stored.name if f.stored else None,
        example="forestry-A-2.3.0.1.jar"),
    'sha256': fields.String(attribute=lambda f: f.stored.sha256 if f.stored else None,
        example="2c42fe4c1e9498aa86fc05da13935b77d169328e2da2365dcf4e17dc76e36d3b"),
    'description': fields.String(attribute='desc', example="Requires X, Y and Z."),
    'page_url': fields.String(example="https://example.com/mod-downloads/cool-mod/"),
    'redirect_url': fields.String(description="A link to the file download, \
        through a redirect like adf.ly", example="https://adf.ly/example"),
    'direct_url': fields.String(
        description="A direct download link for this file. \
            Note: this may still be a download page like Mediafire.",
        example="https://example.com/mod-downloads/cool-mod/cool-mod-v1.3.5.zip"),
    'archive_url': ArchiveUrl(attribute=lambda f: f,
        description="A direct download link to the file as stored in the archive. Unlike direct_url, \
            this will never return an intermediary download page.\
            May be excluded for legal reasons.",
        example="https://b2.mcarchive.net/file/mcarchive/b4451368e478fb9a2192ed35176198c0bcef038d57880c8bf0189eae0543086d/Crossbows-0.2a.zip")
})


mod_version = api.model('Mod Version', {
    'uuid': fields.String(example="08f15883-bf6a-420d-b770-639a2551fbbe"),
    'name': fields.String(example="Crossbows-0.2a.zip"),
    'page_url': fields.String(attribute='url', example="https://example.com/mod-downloads/"),
    'description': fields.String(attribute='desc'),
    'game_versions': fields.List(fields.Nested(game_version, skip_none=True), attribute='game_vsns')
})

mod_version_files = api.inherit('Mod Version with Files', mod_version, {
    'files': fields.List(fields.Nested(mod_file, skip_none=True))
})


mod = api.model('Mod', {
    'uuid': fields.String(example="08f15883-bf6a-420d-b770-639a2551fbbe"),
    'slug': fields.String(example="ee"),
    'name': fields.String(example="Equivalent Exchange"),
    'description': fields.String(attribute='desc', example="The original Equivalent Exchange. Files were taken from the Technic pack."),
    'website': fields.String(example="https://example.com/cool-mod/"),
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

