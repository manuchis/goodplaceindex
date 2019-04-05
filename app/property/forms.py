from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User, Company

class PropertySearch(FlaskForm):
    post = StringField(_l('Insert address'), **{'id':'addressElem'}, validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))
