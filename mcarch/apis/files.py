from . import api
from . import models

from mcarch.app import db
from mcarch.model.mod import ModFile
from mcarch.model.file import StoredFile
from flask_restx import Resource, fields, reqparse

ns = api.namespace('files')


@ns.route("/by_hash/sha256/<shasum>")
class FilesByHash(Resource):
    @api.doc("files_by_hash_sha256")
    @api.marshal_with(models.file_with_parent, skip_none=True)
    def get(self, shasum, **kwargs):
        '''Returns info on a file based on its hash.'''
        return ModFile.query \
            .join(StoredFile) \
            .filter(StoredFile.sha256 == shasum, ) \
            .all()
