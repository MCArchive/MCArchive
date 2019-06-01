from flask import Blueprint, render_template

from mcarch.model.mod import Mod
from mcarch.forms import EditModForm

modbp = Blueprint('mods', __name__, template_folder="templates")


@modbp.route("/mods")
def browse():
    mods = Mod.query.all()
    return render_template("mods/browse.html", mods=mods)

@modbp.route("/mods/<slug>")
def mod_page(slug):
    mod = Mod.query.filter_by(slug=slug).first_or_404()
    return render_template("mods/mod.html", mod=mod)

@modbp.route("/edit/<slug>")
def edit_mod(slug):
    mod = Mod.query.filter_by(slug=slug).first_or_404()

