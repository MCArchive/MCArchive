from flask import Blueprint, render_template, url_for, redirect, abort, flash, request

from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired, Length

from mcarch.model.user import User
from mcarch.login import login_required, logout_required, log_in, log_out, cur_user

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
        if form.validate() and log_in(form.data['username'], form.data['password']):
            user = cur_user()
            flash('Logged in as {}.'.format(user.name))
            nextpage = request.args.get('next')
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

