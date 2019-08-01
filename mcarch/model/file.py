import enum
from urllib.parse import urljoin

from flask import url_for, current_app as app
from mcarch.app import db

class StoredFile(db.Model):
    """Represents a file stored in some sort of storage medium."""
    __tablename__ = 'stored_file'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    sha256 = db.Column(db.String(130), nullable=False)

    # Path to this file within the B2 bucket. Null if file is not on B2.
    b2_path = db.Column(db.String(300), nullable=True)

    def b2_download_url(self):
        """Gets the URL to download this file from the archive's B2 bucket."""
        if self.b2_path:
            return urljoin(app.config['B2_PUBLIC_URL'], self.b2_path)

