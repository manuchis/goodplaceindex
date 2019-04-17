from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField, DecimalField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Length, InputRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES
from flask_babel import _, lazy_gettext as _l
from app.models import User, Company, Product

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
    image = FileField(validators=[FileRequired(),FileAllowed(IMAGES, _l('Images only!'))])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_name, *args, **kwargs):
        super(EditCompanyForm, self).__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            company = Company.query.filter_by(name=name.data).first()
            if company is not None:
                raise ValidationError(_('Please use a different name.'))

class CreateProductForm(FlaskForm):
    name = StringField(_l('Product Name'), validators=[DataRequired()])
    type = SelectField(_l('Type of subscription'), coerce=int, choices=[(0, 'Unlimited'), (1, 'Month'), (2, 'Year')], validators=[InputRequired()])
    price = DecimalField(_l('Price'), validators=[InputRequired()], description='In euros (€)')
    requests_limit = IntegerField(_l('Member requests limit'), validators=[DataRequired()], description='-1 for unlimited, 0 is not valid', default=-1)
    visible = SelectField(_l('Published'),coerce=lambda x: x == 'True', choices=[(True, 'Yes'), (False, 'No')], validators=[InputRequired()], default=False)
    submit = SubmitField(_l('Submit'))
