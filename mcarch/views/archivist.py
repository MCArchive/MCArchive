from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_wtf import FlaskForm

from mcarch.login import login_required
from mcarch.model.user import roles
from mcarch.model.mod.logs import LogMod, slow_gen_diffs
from mcarch.model.mod import Mod

arch = Blueprint('archivist', __name__, template_folder="templates")

@arch.route("/panel")
@login_required(role=roles.archivist)
def main():
    changes = slow_gen_diffs(LogMod.query.order_by(LogMod.index.desc()).limit(3).all())
    drafts = Mod.query.filter_by(draft=True).limit(4).all()
    return render_template("/archivist/main.html", changes=changes, drafts=drafts)