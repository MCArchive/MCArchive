# This file creates an empty SQLite database for development.

import sys

from mcarch.app import create_app, db
import mcarch.model

from mcarch.app import DevelopmentConfig
from mcarch.model.user import *
from mcarch.model.mod import *

app = create_app(DevelopmentConfig)
with app.app_context():
    db.create_all()
    test_usr = User(name="admin", password="a", email="test@example.com", admin=True)
    db.session.add(test_usr)

    if len(sys.argv) > 1:
        from os import listdir
        from os.path import isdir, isfile, join, splitext
        import yaml

        path = sys.argv[1]
        if not isdir(path):
            print("Expected metarepo directory to import as first argument")
            exit()
        print("Importing old archive files from {}".format(path))
        
        for name in [f for f in listdir(path) if isfile(join(path, f))]:
            p = join(path, name)
            print("Importing {}".format(p))
            obj = None
            with open(p, 'r') as f:
                obj = yaml.load(f)
            db.session.add(import_mod(obj, splitext(name)[0]))

    db.session.commit()

