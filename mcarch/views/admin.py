from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_wtf import FlaskForm

from mcarch.app import db
from mcarch.login import login_required
from mcarch.model.mod.logs import LogMod, slow_gen_diffs
from mcarch.model.user import User, Session, roles, UserRole

from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Length, DataRequired, Email, ValidationError
from wtforms.fields.html5 import EmailField

admin = Blueprint('admin', __name__, template_folder="templates")

@admin.route("/admin")
@login_required(role=roles.moderator, pass_user=True)
def main(user):
    users = User.query.order_by(User.last_seen.desc()).limit(5).all()
    changes = slow_gen_diffs(LogMod.query.order_by(LogMod.index.desc()).limit(3).all())
    return render_template('/admin/main.html', user=user, changes=changes, users=users)


@admin.route("/admin/changes")
@login_required(role=roles.moderator)
def changes():
    changes = slow_gen_diffs(LogMod.query.order_by(LogMod.index.desc()).all())
    return render_template('/admin/changes.html', changes=changes)


@admin.route("/admin/users")
@login_required(role=roles.admin)
def users():
    users = User.query.all()
    return render_template('/admin/users.html', users=users)

@admin.route("/admin/users/<name>")
@login_required(role=roles.admin)
def user(name):
    user = User.query.filter_by(name=name).first_or_404()
    return render_template('/admin/user.html', user=user)

@admin.route("/admin/disable-session/<sessid>", methods=['GET', 'POST'])
@login_required(role=roles.admin)
def disable_sess(sessid):
    sess = Session.query.filter_by(id=sessid).first_or_404()
    if sess.expired():
        flash('That session is already disabled.')
        return redirect(url_for('admin.user', name=sess.user.name))

    if request.method == 'GET':
        return render_template('/admin/confirm-disable-sess.html', sess=sess)
    elif request.method == 'POST':
        sess.disable()
        db.session.commit()
        flash('Session {} for user {} has been disabled.'.format(sess.id, sess.user.name))
        return redirect(url_for('admin.user', name=sess.user.name))

@admin.route("/admin/reset-password/<name>", methods=['GET', 'POST'])
@login_required(role=roles.admin)
def reset_passwd(name):
    user = User.query.filter_by(name=name).first_or_404()
    if request.method == 'GET':
        return render_template('/admin/confirm-password-reset.html', user=user)
    elif request.method == 'POST':
        user.clear_password()
        token = user.gen_passwd_reset_token()
        db.session.commit()
        return render_template('/admin/password-reset.html', user=user, token=token)

@admin.route("/admin/disable-user/<name>", methods=['GET', 'POST'])
@login_required(role=roles.admin)
def disable_user(name):
    user = User.query.filter_by(name=name).first_or_404()
    if request.method == 'GET':
        return render_template('/admin/confirm-disable-user.html', user=user)
    elif request.method == 'POST':
        if user.has_role(UserRole.admin):
            flash("You cannot disable an admin's login. How'd you get here?")
            return redirect(url_for('admin.user', name=user.name))

        if user.disabled:
            user.enable()
        else:
            user.disable()

        db.session.commit()
        return render_template('/admin/disable-user-success.html', user=user)


class CreateUserForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(),
        Length(max=User.name.type.length)], render_kw={"placeholder": "Username"})
    email = EmailField('email', validators=[Email(), DataRequired(),
        Length(max=User.email.type.length)], render_kw={"placeholder": "Email"})
    role = SelectField('role',
            choices=[(member.name, name.capitalize()) for
                        name, member in UserRole.__members__.items()],
        validators=[DataRequired()])
    submit = SubmitField('Submit')

@admin.route("/admin/create-user", methods=['GET', 'POST'])
@login_required(role=roles.admin)
def create_user():
    form = CreateUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(name=form.name.data, email=form.email.data,
                role=UserRole[form.role.data],
                passhash="non-empty", password="non-empty")
            db.session.add(new_user)
            new_user.clear_password()
            token = new_user.gen_passwd_reset_token()
            db.session.commit()
            return render_template('/admin/create-user-success.html',
                    user=new_user, token=token)
        else:
            flash("Username and Email are required")
        
    return render_template('/admin/create-user.html', roles=UserRole, form=form)
        
