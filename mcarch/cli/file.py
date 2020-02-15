"""Command line interface for managing files."""

from flask import Blueprint, url_for
import click

from mcarch.app import db
from mcarch.model.file import StoredFile
from mcarch.model.mod import ModFile
from mcarch.model.mod.logs import LogModFile
from mcarch.model.mod.draft import DraftModFile

bp = Blueprint('file', __name__)

@bp.cli.command('normalize')
def normalize():
    """Convert all hashes in the database to lowercase."""
    files = StoredFile.query.all()
    for f in files:
        f.sha256 = f.sha256.lower()
    db.session.commit()

@bp.cli.command('dedup')
@click.option('--pretend/--no-pretend', default=True,
        help="Don't actually do anything, but print what would be done. Defaults to --pretend.")
@click.option('--verbose/--no-verbose', default=True,
        help="Print more information about what's happening.")
def dedup(pretend, verbose):
    """Remove duplicate `StoredFile` entries from the database.

    Files with the same `b2_path` are considered duplicates.

    Any rows referencing them will be consolidated to refer to a single `StoredFile`.
    """
    dup_files = db.session.query(db.func.count(StoredFile.b2_path), StoredFile.b2_path) \
            .filter(StoredFile.b2_path.isnot(None)) \
            .group_by(StoredFile.b2_path) \
            .having(db.func.count(StoredFile.b2_path) > 1).all()

    if pretend:
        print("This is a pretend run. To dedup for real, use --no-pretend.")
    if verbose: print("Duplicate files: {}".format(dup_files))

    for _, fpath in dup_files:
        if verbose: print("De-duplicate path {}".format(fpath))
        sfiles = StoredFile.query.filter_by(b2_path=fpath).all()
        # Choose a "canonical" version of the file, which will be the only one
        # left after de-duplication.
        canon = sfiles[0]
        if verbose: print("Canonical file chosen: {}".format(canon))
        for sfile in sfiles[1:]:
            if verbose: print("\tClean duplicate file {}".format(sfile))
            # Find all references to the duplicate file.
            refs  = ModFile.query.filter_by(stored_id=sfile.id).all()
            refs += LogModFile.query.filter_by(stored_id=sfile.id).all()
            refs += DraftModFile.query.filter_by(stored_id=sfile.id).all()
            for ref in refs:
                assert ref.stored.b2_path == fpath
                if verbose:
                    mod = ref.version.mod
                    print("\t\tRemap reference {} by mod {}".format(ref, mod.name))
                if not pretend:
                    ref.stored = canon
            if not pretend:
                print("\tDelete stored file {}".format(sfile))
                db.session.delete(sfile)
                db.session.commit()
    if pretend:
        print("This was a pretend run. To dedup for real, use --no-pretend.")

