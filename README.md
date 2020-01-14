<img src="https://avatars3.githubusercontent.com/u/26308620" alt="MCArchive logo"
     width="128" height="128" align="right" />

# Minecraft Archive

This is a website where old (and new) Minecraft mods can be hosted and
preserved for future generations.

## Running

To set up a development environment for the website, you'll need Python 3, pip,
and yarn for the frontend assets.

It is recommended to install pip-tools (`pip install pip-tools`) in your
virtualenv if you're going to be contributing. This will allow you to use
pip-sync to keep your dependencies in sync with the requirements.

Before you run any `flask` commands, set the following environment variables.
You can add this to the end of `bin/activate` in your virtualenv to have it set
for you when you activate your environment.

```
export FLASK_APP=mcarch
export FLASK_ENV=development
export MCARCH_CONFIG=dev_config.py
```

Copy `config.py.example` to `dev_config.py` and edit it to configure your
database (PostgreSQL is used in production and recommended for development),
Redis, and B2 bucket. If you're not uploading files, you can exclude the B2 API
keys and bucket name and use MCArchive's official B2 public URL:
`https://b2.mcarchive.net/file/mcarchive/`.

Now you can install dependencies and build the assets.

1. Run `yarn` to install the frontend dependencies.
2. Run `yarn run webpack` to build frontend assets. If you want to make changes
   to them, you can run `yarn run webpack --watch` to auto-rebuild them.
3. Run `pip-sync` if you're using pip-tools, or just `pip install -r
   requirements.txt` otherwise.
4. Run `flask db upgrade` to create the database.

To create an admin user for yourself, run `flask adduser <name> <email> admin`.

To import metadata from the old archive format, you can run `flask import
/path/to/metadata`, where the path is a folder containing metadata files for
the old archive. The script assumes all the files in the imported metadata are
already stored on Backblaze B2, and will add them to the database as such.

When you're done setting up, you can start the development server with `flask
run`.

