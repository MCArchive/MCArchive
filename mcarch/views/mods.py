from flask import Blueprint, render_template, jsonify, request, url_for

from mcarch.model.mod import Mod, ModAuthor, ModVersion, GameVersion
from mcarch.model.mod.logs import LogMod
from mcarch.login import login_required, user_required
from mcarch.jsonschema import ModSchema, ModAuthorSchema, GameVersionSchema
from mcarch.util.minecraft import key_mc_version
from mcarch.app import db

modbp = Blueprint('mods', __name__, template_folder="templates")


@modbp.route("/mods")
def browse():
    mod_query = Mod.query
    by_author = request.args.get('author')
    by_gvsn = request.args.get('gvsn')
    # list of filters to be listed on the page
    filters = []

    if by_author:
        filters.append(('author', by_author))
        mod_query = mod_query.join(ModAuthor, Mod.authors).filter(ModAuthor.name == by_author)
    if by_gvsn:
        filters.append(('gvsn', by_gvsn))
        mod_query = mod_query.join(ModVersion) \
                             .join(GameVersion, ModVersion.game_vsns) \
                             .filter(GameVersion.name == by_gvsn)

    mods = mod_query.all()
    return render_template("mods/browse.html", mods=mods, filters=filters, gvsn=by_gvsn)

@modbp.route("/mods/<slug>")
def mod_page(slug):
    mod = Mod.query.filter_by(slug=slug).first_or_404()
    vsns = mod.vsns_by_game_vsn()

    by_gvsn = request.args.get('gvsn')
    if by_gvsn:
        vsns = { by_gvsn: vsns.get(by_gvsn) }

    return render_template("mods/mod.html", mod=mod, vsns_grouped=vsns, by_gvsn=by_gvsn)

@modbp.route("/mods/<slug>.json")
def mod_page_json(slug):
    mod = Mod.query.filter_by(slug=slug).first_or_404()
    return jsonify(ModSchema().dump(mod).data)


@modbp.route("/authors")
def authors():
    authors = ModAuthor.query.all()
    return render_template('mods/authors.html', authors=authors)

@modbp.route("/gamevsns")
def gamevsns():
    gamevsns = sorted(GameVersion.query.all(), key=lambda a: key_mc_version(a.name), reverse=True)
    return render_template('mods/gamevsns.html', gamevsns=gamevsns)


@modbp.route("/mods/<slug>/edit", methods=['GET', 'POST'])
@user_required
def edit_mod(user, slug):
    if request.method == 'POST':
        json = request.get_json()
        if json:
            mod = Mod.query.filter_by(slug=slug).first_or_404()
            mod_schema = ModSchema(instance=mod, session=db.session)
            mod_schema.load(json)
            mod.log_change(user=user)
            db.session.commit()
            return jsonify({
                "result": "success",
                "redirect": url_for('mods.mod_page', slug=slug)
            })
        else:
            response = jsonify({"result": "error", "error": "No JSON data received."})
            response.status_code = 400
            return response
    else:
        mod = Mod.query.filter_by(slug=slug).first_or_404()
        authors = ModAuthor.query.all()
        game_vsns = GameVersion.query.all()

        authorjson = [ModAuthorSchema().dump(a).data for a in authors]
        gvsnjson = [GameVersionSchema().dump(g).data for g in game_vsns]
        return render_template("mods/edit.html", mod=mod,
                modjson=ModSchema().dump(mod).data, authorjson=authorjson, gvsnjson=gvsnjson)

@modbp.route("/mods/<slug>/history")
@login_required
def mod_history(slug):
    mod = Mod.query.filter_by(slug=slug).first_or_404()
    changes = []
    for i, log in enumerate(mod.logs):
        diff = None
        if i > 0: diff = mod.logs[i-1].diff(log)
        else: diff = Mod(slug='').diff(log)
        changes.append({
            'obj': log,
            'user': log.user,
            'date': log.date,
            'diff': diff,
        })
    return render_template("mods/history.html", mod=mod, changes=changes)

@modbp.route("/mods/<slug>/history/<revid>")
@login_required
def mod_revision(slug, revid):
    rev = LogMod.query.filter_by(id=revid).first_or_404()
    vsns = rev.vsns_by_game_vsn()
    return render_template("mods/mod.html", mod=rev, rev=rev, vsns_grouped=vsns)

