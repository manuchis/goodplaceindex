from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User, Company

class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), render_kw={'readonly': True}, validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), render_kw={'readonly': True},
                             validators=[Length(min=0, max=140)])
    roles = SelectMultipleField(_l('Roles'), coerce=int)
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))

class EditCompanyForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    user_id = SelectField(_l('Company owner'), coerce=int, validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_name, *args, **kwargs):
        super(EditCompanyForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            company = Company.query.filter_by(name=name.data).first()
            if company is not None:
                raise ValidationError(_('Please use a different name.'))
