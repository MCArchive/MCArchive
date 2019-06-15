from flask import Blueprint, render_template, url_for, redirect, abort, flash, request

from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

from mcarch.app import db
from mcarch.model.user import User, ResetToken
from mcarch.login import login_required, logout_required, log_in, log_out, \
    cur_user, insecure_cur_user
from mcarch.util.security import is_safe_url

user = Blueprint('user', __name__, template_folder="templates")

# Bcrypt can't handle passwords longer than 72 characters
MAX_PASSWORD_LEN = 72

class LoginForm(FlaskForm):
    username = StringField('Username',
            validators=[DataRequired(), Length(max=User.name.type.length)])
    password = PasswordField('Password',
            validators=[DataRequired(), Length(max=MAX_PASSWORD_LEN)])

@user.route("/login", methods=['GET', 'POST'])
@logout_required
def login():
    form = LoginForm()
    if request.method == 'POST':
        nextpage = request.args.get('next')
        if nextpage and not is_safe_url(nextpage):
            return abort(400)
        if form.validate() and log_in(form.data['username'], form.data['password']):
            user = insecure_cur_user()
            flash('Logged in as {}.'.format(user['name']))
            if nextpage: return redirect(nextpage)
            else: return redirect(url_for('root.home'))
        else:
            flash('Login failed.')
    return render_template("login.html", form=form)

@user.route("/logout")
def logout():
    log_out()
    flash('Logged out.')
    return redirect(url_for('root.home'))


class PassResetForm(FlaskForm):
    password = PasswordField('New Password',
            validators=[DataRequired(), Length(max=MAX_PASSWORD_LEN),
                EqualTo('confirm', message='Passwords must match')
            ])
    confirm = PasswordField('Confirm Password',
            validators=[DataRequired(), Length(max=MAX_PASSWORD_LEN)])

@user.route("/reset-password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    token = ResetToken.query.filter_by(token=token).first_or_404()
    form = PassResetForm()
    if request.method == 'POST':
        if form.validate():
            token.user.set_password(form.data['password'])
            db.session.delete(token)
            db.session.commit()
            flash('Your password has been changed. Please log in with your new password.')
            return redirect(url_for('user.login'))
    return render_template("reset-password.html", form=form)

