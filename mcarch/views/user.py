from flask import Blueprint, render_template, url_for, redirect, abort, flash, request, \
    current_app as app

from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

from mcarch.app import db, limiter
from mcarch.model.user import User, ResetToken, reset_type
from mcarch.login import login_required, logout_required, log_in, log_out, \
    cur_user, cur_session
from mcarch.util.security import is_safe_url

user = Blueprint('user', __name__, template_folder="templates")

# Bcrypt can't handle passwords longer than 72 characters
MAX_PASSWORD_LEN = 72

AUTH_RATELIMIT='10 per 5 minutes;30 per hour'
AUTH_RATELIMIT_ERRMSG='Too many attempts. Try again later.'

class LoginForm(FlaskForm):
    username = StringField('Username',
            validators=[DataRequired(), Length(max=User.name.type.length)])
    password = PasswordField('Password',
            validators=[DataRequired(), Length(max=MAX_PASSWORD_LEN)])

@user.route("/login", methods=['GET', 'POST'])
@limiter.limit(AUTH_RATELIMIT, methods=['POST'], error_message=AUTH_RATELIMIT_ERRMSG)
@logout_required
def login():
    form = LoginForm()
    if request.method == 'POST':
        nextpage = request.args.get('next')
        if nextpage and not is_safe_url(nextpage):
            return abort(400)
        if form.validate() and log_in(form.data['username'], form.data['password']):
            sess = cur_session(only_fully_authed=False)
            assert sess
            if sess.authed_2fa:
                flash('Logged in as {}.'.format(sess.user.name))
                if nextpage: return redirect(nextpage)
                else: return redirect(url_for('root.home'))
            else:
                return redirect(url_for('user.prompt_2fa', next=nextpage))
        else:
            flash('Login failed.')
    return render_template("login.html", form=form)

@user.route("/logout")
def logout():
    log_out()
    flash('Logged out.')
    return redirect(url_for('root.home'))


class OtpForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired(), Length(max=6, min=6)])

@user.route("/2fa", methods=['GET', 'POST'])
@limiter.limit(AUTH_RATELIMIT, methods=['POST'], error_message=AUTH_RATELIMIT_ERRMSG)
def prompt_2fa():
    nextpage = request.args.get('next')
    if nextpage:
        if not is_safe_url(nextpage): return abort(400)
    else:
        nextpage = url_for('root.home')

    sess = cur_session(False)
    if not sess: return redirect(url_for('user.login'))
    if sess.authed_2fa:
        flash("You are already fully authenticated.")
        return redirect(nextpage)

    form = OtpForm()
    if request.method == 'POST':
        if form.validate() and sess.auth_2fa(form.code.data):
            flash('Logged in.')
            return redirect(nextpage)
        else:
            flash('Login failed.')
    return render_template("2fa.html", form=form)

class PassResetForm(FlaskForm):
    password = PasswordField('New Password',
            validators=[DataRequired(), Length(max=MAX_PASSWORD_LEN),
                EqualTo('confirm', message='Passwords must match')
            ])
    confirm = PasswordField('Confirm Password',
            validators=[DataRequired(), Length(max=MAX_PASSWORD_LEN)])

@user.route("/reset/password/<token>", methods=['GET', 'POST'])
@limiter.limit(AUTH_RATELIMIT, error_message=AUTH_RATELIMIT_ERRMSG)
def reset_password(token):
    token = ResetToken.query.filter_by(token=token, kind=reset_type.password).first_or_404()
    if token.expired():
        db.session.delete(token)
        db.session.commit()
        flash('Your password reset link has expired. Please contact an administrator.')
        return redirect(url_for('root.home'))

    form = PassResetForm()
    if form.validate_on_submit():
        token.user.set_password(form.data['password'])
        db.session.delete(token)
        db.session.commit()
        if app.config['REQUIRE_2FA'] and not token.user.totp_secret:
            flash('Your password has been changed. Please set up 2-factor authentication now.')
            token.user.reset_2fa_secret()
            newtok = token.user.gen_2fa_reset_token()
            db.session.commit()
            return redirect(url_for('user.reset_2fa', token=newtok))
        else:
            flash('Your password has been changed. Please log in with your new password.')
            return redirect(url_for('user.login'))
    return render_template("reset-password.html", form=form)


class OtpSetupForm(FlaskForm):
    code = StringField('Authenticator Code',
            validators=[DataRequired(), Length(max=6, min=6)])

@user.route('/reset/2fa/<token>', methods=['GET', 'POST'])
@limiter.limit(AUTH_RATELIMIT, error_message=AUTH_RATELIMIT_ERRMSG)
def reset_2fa(token):
    token = ResetToken.query.filter_by(token=token, kind=reset_type.otp).first_or_404()
    if token.expired():
        db.session.delete(token)
        db.session.commit()
        flash('Your 2-factor reset link has expired. Please contact an administrator.')
        return redirect(url_for('root.home'))

    form = OtpSetupForm()
    if form.validate_on_submit():
        if token.user.validate_otp(form.code.data):
            db.session.delete(token)
            db.session.commit()
            flash("2-factor authentication set up successfully. For security reasons, "
                  "you must wait for the next code before you log in.")
            return redirect(url_for('user.login'))
        else:
            flash('Incorrect code. Are you sure you typed it correctly?')
    uri = token.user.totp_uri()
    return render_template("reset-2fa.html", form=form, totp_uri=uri)

