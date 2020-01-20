"""Views for archivists to edit and manage mods on the archive"""

from tempfile import NamedTemporaryFile

from flask import Blueprint, render_template, request, url_for, redirect, flash, abort
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from sqlalchemy.orm.exc import NoResultFound

from mcarch.app import db
from mcarch.login import login_required
import mcarch.login as login
from mcarch.model.mod import Mod, ModVersion, ModFile, ModAuthor, GameVersion
from mcarch.model.mod.draft import DraftMod, DraftModVersion, DraftModFile
from mcarch.model.mod.logs import LogMod, LogModVersion, LogModFile

from mcarch.model.file import upload_b2_file
from mcarch.model.user import roles
from mcarch.util.wtforms import BetterSelect, TagInput

from wtforms import StringField, SelectField, SelectMultipleField, TextAreaField, BooleanField, \
        SubmitField
from wtforms.validators import Length, DataRequired, Email, Regexp, ValidationError

edit = Blueprint('edit', __name__, template_folder="templates")

@edit.route('/drafts')
@login_required(role=roles.archivist)
def draft_list():
    archived = request.args.get('archived', False, type=bool)
    if archived:
        query = DraftMod.archived_time.isnot(None)
    else:
        query = DraftMod.archived_time.is_(None)
    drafts = DraftMod.query.filter(query)
    return render_template("editor/draft-list.html", drafts=drafts)

@edit.route('/drafts/<id>')
@login_required(role=roles.archivist, pass_user=True)
def draft_page(user, id):
    draft = DraftMod.query.filter_by(id=id).first_or_404()
    vsns = draft.vsns_by_game_vsn()
    return render_template("mods/mod.html", mod=draft, vsns_grouped=vsns, is_draft=True)


@edit.route('/mods/<slug>/new-draft', methods=['POST'])
@login_required(role=roles.archivist, pass_user=True)
def new_draft(user, slug):
    mod = Mod.query.filter_by(slug=slug).first_or_404()
    draft = mod.make_draft(user)
    db.session.add(draft)
    db.session.commit()
    return redirect(url_for('edit.draft_page', id=draft.id))


@edit.route('/drafts/<id>/archive', methods=['GET', 'POST'])
@login_required(role=roles.moderator)
def archive_draft(id):
    draft = DraftMod.query.filter_by(id=id).first_or_404()
    if draft.archived:
        flash('This draft is already archived.')
        return redirect(url_for('edit.draft_page', id=draft.id))

    if request.method == 'POST':
        draft.archived = True
        db.session.commit()
        return redirect(url_for('edit.draft_page', id=draft.id))
    return render_template('editor/confirm-archive.html', draft=draft, archiving=True)

@edit.route('/drafts/<id>/unarchive', methods=['GET', 'POST'])
@login_required(role=roles.moderator)
def unarchive_draft(id):
    draft = DraftMod.query.filter_by(id=id).first_or_404()
    if draft.merged:
        flash("This draft was merged and can't be un-archived.")
        return redirect(url_for('edit.draft_page', id=draft.id))
    if not draft.archived:
        flash('This draft is not archived.')
        return redirect(url_for('edit.draft_page', id=draft.id))

    if request.method == 'POST':
        draft.archived = False
        db.session.commit()
        return redirect(url_for('edit.draft_page', id=draft.id))
    return render_template('editor/confirm-archive.html', draft=draft, archiving=False)


class ReviewDraftForm(FlaskForm):
    slug = StringField('Slug', validators=[
        DataRequired(),
        Length(max=Mod.slug.type.length),
        Regexp(r'[a-zA-Z0-9-_]+')
    ])

@edit.route('/drafts/<id>/diff', methods=['GET', 'POST'])
@login_required(role=roles.archivist, pass_user=True)
def draft_diff(user, id):
    form = ReviewDraftForm()
    draft = DraftMod.query.filter_by(id=id).first_or_404()
    if draft.archived:
        flash('This draft is archived. It cannot be merged.')
        return redirect(url_for('edit.draft_page', id=draft.id))
    diff = draft.draft_diff()
    if request.method == 'POST':
        if not login.has_role(roles.moderator): return abort(403)
        if draft.current:
            if not draft.draft_diff().is_empty():
                draft.merge()
                return redirect(url_for('mods.mod_page', slug=draft.current.slug))
            else:
                flash("Can't merge a draft with no changes.")
        elif form.validate():
            mod = draft.into_mod(form.slug.data)
            return redirect(url_for('mods.mod_page', slug=mod.slug))
    return render_template("editor/draft_diff.html", mod=draft, diff=diff, form=form)


class EditModForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=Mod.name.type.length)])
    website = StringField('Website', validators=[Length(max=Mod.website.type.length)])
    authors = StringField("Authors", widget=TagInput())
    desc = TextAreaField("Description")
    submit = SubmitField('Submit')

    def get_selected_authors(self):
        """
        Generates list of authors selected in this form. Author names that don't
        exist in the DB will be added.
        """
        names = [s.strip() for s in self.authors.data.split(',')]
        for name in names:
            author = ModAuthor.query.filter_by(name=name).first()
            if not author:
                author = ModAuthor(name=name)
            yield author

@edit.route('/edit/new-mod', methods=['GET', 'POST'])
@login_required(role=roles.archivist, pass_user=True)
def new_mod(user):
    form = EditModForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            authors = list(form.get_selected_authors())
            mod = DraftMod(
                name=form.name.data,
                website=form.website.data,
                desc=form.desc.data,
                authors=authors,
                user=user,
            )
            db.session.add(mod)
            db.session.commit()
            return redirect(url_for('edit.draft_page', id=mod.id))
    return render_template('editor/edit-mod.html', form=form)

@edit.route("/drafts/<id>/edit", methods=['GET', 'POST'])
@login_required(role=roles.archivist, pass_user=True)
def edit_mod(user, id):
    mod = DraftMod.query.filter_by(id=id).first_or_404()
    if not mod.editable:
        flash('This draft is archived. It cannot be edited.')
        return redirect(url_for('edit.draft_page', id=mod.id))
    form = EditModForm(name=mod.name, website=mod.website, desc=mod.desc,
        authors=','.join([a.name for a in mod.authors]))
    if form.validate_on_submit():
        mod.touch()
        mod.name = form.name.data
        mod.website = form.website.data
        mod.desc = form.desc.data
        mod.authors = list(form.get_selected_authors())
        db.session.commit()
        return redirect(url_for('edit.draft_page', id=mod.id))
    return render_template('editor/edit-mod.html', form=form, editing=mod)


class EditVersionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=Mod.name.type.length)])
    url = StringField('Web Page', validators=[Length(max=Mod.website.type.length)])
    desc = TextAreaField("Description")
    gamevsns = SelectMultipleField("Game Versions", coerce=int,
        widget=BetterSelect(multiple=True))
    submit = SubmitField('Submit')

    def load_gamevsns(self):
        """Loads the game version select choices from the database

        This must be called before the form is used, or no versions will be listed in the form.
        """
        vsns = GameVersion.query.all()
        self.gamevsns.choices = list(map(lambda v: (v.id, v.name), vsns))

    def get_selected_gamevsns(self):
        """Get a list of authors from the database according to what is selected."""
        ids = self.gamevsns.data
        return GameVersion.query.filter(GameVersion.id.in_(ids)).all()

@edit.route("/drafts/<id>/edit/new-version", methods=['GET', 'POST'])
@login_required(role=roles.archivist, pass_user=True)
def new_mod_version(user, id):
    mod = DraftMod.query.filter_by(id=id).first_or_404()
    if not mod.editable:
        flash('This draft is archived. It cannot be edited.')
        return redirect(url_for('edit.draft_page', id=mod.id))

    form = EditVersionForm()
    form.load_gamevsns()
    if form.validate_on_submit():
        mod.touch()
        vsn = DraftModVersion(
            name=form.name.data,
            url=form.url.data,
            desc=form.desc.data,
            game_vsns=form.get_selected_gamevsns(),
        )
        mod.mod_vsns.append(vsn)
        db.session.commit()
        return redirect(url_for('edit.draft_page', id=mod.id))
    return render_template('editor/edit-version.html', form=form, mod=mod)

@edit.route("/drafts/edit/mod-version/<id>/rm", methods=['GET', 'POST'])
@login_required(role=roles.archivist, pass_user=True)
def rm_mod_version(user, id):
    vsn = DraftModVersion.query.filter_by(id=id).first_or_404()
    mod = vsn.mod
    if not mod.editable:
        flash('This draft is archived. It cannot be edited.')
        return redirect(url_for('edit.draft_page', id=mod.id))

    if request.method == 'POST':
        mod.touch()
        db.session.delete(vsn)
        db.session.commit()
        return redirect(url_for('edit.draft_page', id=mod.id))
    return render_template('editor/confirm-rm-version.html', vsn=vsn)

@edit.route("/drafts/edit/mod-version/<id>", methods=['GET', 'POST'])
@login_required(role=roles.archivist, pass_user=True)
def edit_mod_version(user, id):
    vsn = DraftModVersion.query.filter_by(id=id).first_or_404()
    mod = vsn.mod
    if not mod.editable:
        flash('This draft is archived. It cannot be edited.')
        return redirect(url_for('edit.draft_page', id=mod.id))

    form = EditVersionForm(name=vsn.name, url=vsn.url, desc=vsn.desc,
            gamevsns=list(map(lambda v: v.id, vsn.game_vsns)))
    form.load_gamevsns()
    if form.validate_on_submit():
        mod.touch()
        vsn.name = form.name.data
        vsn.url = form.url.data
        vsn.desc = form.desc.data
        vsn.game_vsns = form.get_selected_gamevsns()
        db.session.commit()
        return redirect(url_for('edit.draft_page', id=mod.id))
    return render_template('editor/edit-version.html', form=form, mod=mod, editing=vsn)


class EditFileForm(FlaskForm):
    file = FileField("Mod File")
    desc = TextAreaField("Description")
    page_url = StringField('Web Page', validators=[Length(max=Mod.website.type.length)])
    direct_url = StringField('Direct Download', validators=[Length(max=Mod.website.type.length)])
    redirect_url = StringField('Indirect Download', validators=[Length(max=Mod.website.type.length)])
    submit = SubmitField('Submit')

def upload_file(file, user):
    """Uploads a file from a `FileField` to B2 and returns the StoredFile object."""
    with NamedTemporaryFile() as tfile:
        file.save(tfile)
        print(file.filename)
        return upload_b2_file(tfile.name, file.filename, user)

@edit.route("/drafts/<id>/edit/new-file", methods=['GET', 'POST'])
@login_required(role=roles.archivist, pass_user=True)
def new_mod_file(user, id):
    vsn = DraftModVersion.query.filter_by(id=id).first_or_404()
    mod = vsn.mod
    if not mod.editable:
        flash('This draft is archived. It cannot be edited.')
        return redirect(url_for('edit.draft_page', id=mod.id))

    form = EditFileForm()
    form.file.validators.append(FileRequired())
    if form.validate_on_submit():
        mod.touch()
        stored = upload_file(form.file.data, user)
        mfile = DraftModFile(
            stored = stored,
            desc = form.desc.data,
            page_url = form.page_url.data,
            redirect_url = form.redirect_url.data,
            direct_url = form.direct_url.data,
        )
        vsn.files.append(mfile)
        db.session.commit()
        return redirect(url_for('edit.draft_page', id=mod.id))
    return render_template('editor/edit-file.html', form=form, mod=mod, vsn=vsn)

@edit.route("/drafts/edit/mod-file/<id>", methods=['GET', 'POST'])
@login_required(role=roles.archivist, pass_user=True)
def edit_mod_file(user, id):
    mfile = DraftModFile.query.filter_by(id=id).first_or_404()
    vsn = mfile.version
    mod = vsn.mod

    form = EditFileForm(
        desc=mfile.desc,
        page_url=mfile.page_url,
        redirect_url=mfile.redirect_url,
        direct_url=mfile.direct_url,
    )
    if form.validate_on_submit():
        mod.touch()
        if form.file.data:
            stored = upload_file(form.file.data, user)
            mfile.stored = stored
        mfile.desc = form.desc.data
        mfile.page_url = form.page_url.data
        mfile.redirect_url = form.redirect_url.data
        mfile.direct_url = form.direct_url.data
        db.session.commit()
        return redirect(url_for('edit.draft_page', id=mod.id))
    return render_template('editor/edit-file.html', form=form, mod=mod,
                vsn=vsn, editing=mfile, curfile=mfile.stored)

@edit.route("/drafts/edit/mod-file/<id>/rm", methods=['GET', 'POST'])
@login_required(role=roles.archivist, pass_user=True)
def rm_mod_file(user, id):
    mfile = DraftModFile.query.filter_by(id=id).first_or_404()
    mod = mfile.version.mod
    if request.method == 'POST':
        mod.touch()
        db.session.delete(mfile)
        db.session.commit()
        return redirect(url_for('edit.draft_page', id=mod.id))
    return render_template('editor/confirm-rm-file.html', file=mfile)

