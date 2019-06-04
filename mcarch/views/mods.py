from flask import Blueprint, render_template, jsonify

from mcarch.model.mod import Mod, ModAuthor, GameVersion
from mcarch.login import login_required
from mcarch.jsonschema import ModSchema, ModAuthorSchema, GameVersionSchema

modbp = Blueprint('mods', __name__, template_folder="templates")


@modbp.route("/mods")
def browse():
    mods = Mod.query.all()
    return render_template("mods/browse.html", mods=mods)

@modbp.route("/mods/<slug>")
def mod_page(slug):
    mod = Mod.query.filter_by(slug=slug).first_or_404()
    return render_template("mods/mod.html", mod=mod)

@modbp.route("/mods/<slug>.json")
def mod_page_json(slug):
    mod = Mod.query.filter_by(slug=slug).first_or_404()
    return jsonify(ModSchema().dump(mod).data)

@modbp.route("/mods/<slug>/edit")
@login_required
def edit_mod(slug):
    mod = Mod.query.filter_by(slug=slug).first_or_404()
    authors = ModAuthor.query.all()
    game_vsns = GameVersion.query.all()

    authorjson = [ModAuthorSchema().dump(a).data for a in authors]
    gvsnjson = [GameVersionSchema().dump(g).data for g in game_vsns]
    return render_template("mods/edit.html", mod=mod,
            modjson=ModSchema().dump(mod).data, authorjson=authorjson, gvsnjson=gvsnjson)

