"""
This module acts as an interface for sending notifications via email or
discord.

This just contains a bunch of functions which send various notifications. The
logic for determining who to send what is handled by the functions.
"""

from flask import render_template, current_app as app
from flask_mail import Message

from mcarch.app import db, mail
from mcarch.model.user import User, roles
from mcarch.model.mod import Mod
from mcarch.model.mod.draft import DraftMod

def draft_ready(draft: DraftMod):
    """Notifies moderators that a new draft is ready."""
    users = User.query.filter(User.role.in_([roles.moderator, roles.admin])).all()
    users = [u for u in users if u.settings.notify_draft_ready]

    app.logger.info('Notifying {} about a ready draft of {}.'.format(users, draft.name))
    msg = Message("Draft of {} is ready for review".format(draft.name),
            bcc=[u.email for u in users])
    msg.body = render_template('mail/draft-ready.txt', draft=draft)
    msg.html = render_template('mail/draft-ready.html', draft=draft)
    mail.send(msg)

def draft_merged(draft: DraftMod, mod: Mod):
    """Notifies discord that a new change has been merged."""
    app.logger.info('Notifying {} about their merged draft.', draft.user.name)
    msg = Message("Your draft of {} was merged".format(draft.name),
            recipients=[draft.user.email])
    msg.body = render_template('mail/draft-merged.txt', draft=draft, mod=mod)
    msg.html = render_template('mail/draft-merged.html', draft=draft, mod=mod)
    mail.send(msg)

