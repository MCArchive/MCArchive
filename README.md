<img src="https://avatars3.githubusercontent.com/u/26308620" alt="MCArchive logo"
     width="128" height="128" align="right" />

# Minecraft Archive

This is a website where old (and new) Minecraft mods can be hosted and
preserved for future generations.

## Running

To run the website, you'll need Python 3, pip, and yarn for the frontend
assets.

It is recommended to install pip-tools (`pip install pip-tools`) in your
virtualenv if you're going to be contributing. This will allow you to use
pip-sync to keep your dependencies in sync with the requirements.

1. Run `yarn` to install the frontend dependencies.
2. Run `yarn run webpack` to build frontend assets. If you want to make changes
   to them, you can run `yarn run webpack --watch` to auto-rebuild them.
3. Create a virtualenv and activate it (install pip-tools here if you're using that).
4. Run `pip-sync` if you're using pip-tools, or just `pip install -r requirements.txt`
   otherwise.
5. Create the database with `python mkdb.py`. To import metadata from the old archive
   format, you can run `python mkdb.py /path/to/metadata`, where the path is a folder
   containing metadata files for the old archive. The script assumes all the files
   in the imported metadata are already stored on Backblaze B2, and will add them to
   the database as such.
6. Run `flask run` to start the web server. It will be available at `localhost:5000`.

If you're contributing, you'll want to set `FLASK_ENV=development` in your
environment.

