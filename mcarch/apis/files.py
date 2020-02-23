from . import api
from . import models

from mcarch.app import db
from mcarch.model.mod import ModFile
from mcarch.model.file import StoredFile
from flask_restx import Resource, fields, reqparse

ns = api.namespace('files', 'Provides access to information about files in the archive.')

@ns.route("/by_hash/sha256/<shasum>")
class FilesByHash(Resource):
    @api.doc("files_by_hash_sha256")
    @api.marshal_with(models.file_with_version, skip_none=True, mask='{}')
    def get(self, shasum, **kwargs):
        '''Returns a list of archived files with the given hash.'''
        return ModFile.query \
            .join(StoredFile) \
            .filter(StoredFile.sha256 == shasum, ) \
            .all()

@ns.route("/by_filename/<filename>")
class FilesByName(Resource):
    @api.doc("files_by_filename")
    @api.marshal_with(models.file_with_version, skip_none=True, mask='{}')
    def get(self, filename, **kwargs):
        '''Returns a list of archived files with the given filename.'''
        return ModFile.query \
            .join(StoredFile) \
            .filter(StoredFile.name == filename, ) \
            .all()

