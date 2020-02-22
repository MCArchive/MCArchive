from typing import Optional, Any, Iterable

from flask_wtf import FlaskForm
from wtforms.fields import BooleanField, SubmitField

from mcarch.app import db

# This dict specifies the default value of each setting.
# Any key not present in this dict is considered to not be a valid setting.
defaults = dict(
    notify_draft_ready=True,
    notify_draft_merged=True,
)

class SettingsForm(FlaskForm):
    """
    A form for changing user settings.

    The `UserSettings` class provides a convenient `form` property which
    constructs one of these containing the user's current settings.
    """
    notify_draft_ready = BooleanField('Notify me when a draft is ready')
    notify_draft_merged = BooleanField('Notify me when my drafts are merged')
    submit = SubmitField('Save')

class UserSettings(object):
    """
    Provides access to a user's settings.

    This class exposes a user's settings as if they were attributes on a normal
    object by overriding the behavior of getattr and setattr.
    """
    def __init__(self, user):
        self.user = user

    def keys(self) -> Iterable[str]:
        """Gets a list of valid setting keys"""
        return defaults.keys()

    def form(self) -> SettingsForm:
        """Constructs a `SettingsForm` with values from the user's current settings."""
        args = {}
        for key in self.keys():
            args[key] = self.get(key)
        return SettingsForm(**args)

    def apply_form(self, form: SettingsForm):
        """Takes a settings form and applies the changes made in it to this user's settings."""
        for key in self.keys():
            # Only apply settings that have actually been changed. This
            # prevents inserting extra rows into the settings table for
            # settings the user hasn't changed from the default.
            newval = getattr(form, key).data
            if self.get(key) != newval:
                self.set(key, newval)

    def get(self, name: str) -> Optional[Any]:
        if name in defaults:
            val = UserSetting.query \
                    .filter_by(user_id=self.user.id) \
                    .filter_by(key=name) \
                    .first()
            if val:
                return val.value
            else:
                return defaults[name]
        else:
            raise AttributeError('No setting called {} exists'.format(name))

    def set(self, name: str, val: Any):
        if name in defaults:
            if val is None:
                UserSetting.query.filter_by(key=name, user=self.user).delete()
            else:
                # If an existing setting matching the same user and key exists,
                # the DB will replace it with the new one.
                db.session.execute(
                        "INSERT INTO user_setting "
                        "(key, value, user_id) VALUES (:key, to_json(:value), :user_id) "
                        "ON CONFLICT (key, user_id) DO "
                        "UPDATE SET value = to_json(:value) ",
                        dict(key=name, value=val, user_id=self.user.id))
        else:
            raise AttributeError('No setting called {} exists'.format(name))

    def __getattr__(self, name: str) -> Optional[Any]:
        return self.get(name)

    def __setattr_(self, name: str, val: Any):
        self.set(name, val)

class UserSetting(db.Model): # type: ignore
    """
    Table for storing user settings.

    Each setting the user has changed from the defaults is stored as a separate
    row containing a key, value pair in this table.

    This schema allows for new settings to be added without requiring a
    database migration.
    """
    key = db.Column(db.String(40), nullable=False, primary_key=True)
    value = db.Column(db.JSON, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    user = db.relationship('User')

