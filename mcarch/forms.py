from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length

from mcarch.model.mod import Mod, ModAuthor, ModVersion, GameVersion, ModFile

class EditModForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(),
        Length(max=Mod.name.property.columns[0].type.length)])
    website = StringField('website', validators=[DataRequired(),
        Length(max=Mod.website.property.columns[0].type.length)])
    desc = TextAreaField('desc')


class EditVersionForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(),
        Length(max=ModVersion.name.property.columns[0].type.length)])
    url = StringField('url', validators=[DataRequired(),
        Length(max=ModVersion.url.property.columns[0].type.length)])
    desc = TextAreaField('desc')
    # game_vsns

