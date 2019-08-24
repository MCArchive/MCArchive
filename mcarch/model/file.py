import os
import enum
import hashlib
from urllib.parse import urljoin

from flask import url_for, current_app as app

from mcarch.app import db, get_b2bucket

class StoredFile(db.Model):
    """Represents a file stored in some sort of storage medium."""
    __tablename__ = 'stored_file'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    sha256 = db.Column(db.String(130), nullable=False)

    upload_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    upload_by = db.relationship('User')

    # Path to this file within the B2 bucket. Null if file is not on B2.
    b2_path = db.Column(db.String(300), nullable=True)

    def b2_download_url(self):
        """Gets the URL to download this file from the archive's B2 bucket."""
        if self.b2_path:
            return urljoin(app.config['B2_PUBLIC_URL'], self.b2_path)

def gen_b2_path(filename, sha):
    """Generates the path where a file should be stored in B2 based on name and hash."""
    return os.path.join(sha, filename)

def sha256_file(path):
    BUF_SZ = 65536
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        buf = f.read(BUF_SZ)
        while buf:
            h.update(buf)
            buf = f.read(BUF_SZ)
    return h.hexdigest()


def upload_b2_file(path, name, user=None):
    """Uploads a local file to B2, adds it to the DB, and returns the StoredFile.

    This adds the StoredFile to the database and does a commit.

    @param path: path to the file on disk
    @param name: name of the file as it should be in B2
    @param user: user to associate the stored file with. Can be None
    """
    bucket = get_b2bucket()

    fhash = sha256_file(path)
    b2path = gen_b2_path(name, fhash)
    bucket.upload_local_file(path, b2path)

    stored = StoredFile(name=name, sha256=fhash, b2_path=b2path, upload_by=user)
    db.session.add(stored)
    db.session.commit()
    return stored

