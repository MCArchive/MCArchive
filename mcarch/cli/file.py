"""Command line interface for managing files."""

from flask import Blueprint, url_for
import click

from mcarch.app import db
from mcarch.model.file import StoredFile

bp = Blueprint('file', __name__)

@bp.cli.command('normalize')
def normalize():
    """Convert all hashes in the database to lowercase."""
    files = StoredFile.query.all()
    for f in files:
        f.sha256 = f.sha256.lower()
    db.session.commit()

