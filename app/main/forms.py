from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User, Company
from sqlalchemy import func

class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
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
    name = StringField(_l('Change name'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_name, *args, **kwargs):
        super(EditCompanyForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            ## In this case the comparison also looks for non case sensitive equivalences
            company = Company.query.filter(func.lower(Company.name) == func.lower(name.data)).first()
            if company is not None:
                raise ValidationError(_('Please use a different name.'))

class CreateCompanyForm(FlaskForm):
    name = StringField(_l('Name'), validators=[DataRequired()])
    user_id = SelectField(_l('Company owner'),  coerce=int, validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

    def validate_name(self, name):
        company = Company.query.filter(func.lower(Company.name) == func.lower(name.data)).first()
        if company is not None:
            raise ValidationError(_('Please use a different name.'))

class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class PropertySearch(FlaskForm):
    post = StringField(_l('Insert address'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class MessageForm(FlaskForm):
    message = TextAreaField(_l('Message'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))
