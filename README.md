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
3. Run `pip-sync` if you're using pip-tools, or just `pip install -r requirements.txt`
   otherwise.
4. Run `flask run` to start the web server. It will be available at `localhost:5000`.

If you're contributing, you'll want to set `FLASK_ENV=development` in your
environment.

