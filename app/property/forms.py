from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, FormField, BooleanField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User, Company
import pycountry

class CountrySelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = [(country.alpha_2, country.name) for country in pycountry.countries]

class AddressForm(FlaskForm):
    street_type = StringField(_l('Street type'), validators=[DataRequired()])
    street_name = StringField(_l('Street'), validators=[DataRequired()])
    street_number = IntegerField(_l('Number'), validators=[DataRequired()])
    city = StringField(_l('City'), validators=[DataRequired()])
    postalcode = IntegerField(_l('Postal Code'), validators=[DataRequired()])
    province = StringField(_l('Province'))
    region = StringField(_l('Region'))
    country = CountrySelectField(_l('Country'), validators=[DataRequired()])

class PropertyDescription(FlaskForm):
    year = IntegerField(_l('Built year'))
    size = IntegerField(_l('Size'))
    use_size = IntegerField(_l('Usable size'))
    rooms = IntegerField(_l('Rooms'))
    bathrooms = IntegerField(_l('Bathrooms'))
    balcony = BooleanField(_l('Balcony'))
    terrace = BooleanField(_l('Terrace'))
    patio = BooleanField(_l('Patio/Garden'))
    garage = BooleanField(_l('Garage'))
    elevator = BooleanField(_l('Elevator'))
    airconditioner = BooleanField(_l('Air Conditioner'))
    centralheating = BooleanField(_l('Central Heating'))
    energycert = SelectField(_l('Energy Eficiency Certificate'), choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('D', 'D'), ('E', 'E'), ('F', 'F'), ('G', 'G'), ('H', 'H')])

class PropertySearch(FlaskForm):
    address = FormField(AddressForm)
    description = FormField(PropertyDescription)
    #post = StringField(_l('Insert address'), **{'id':'addressElem'}, validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))
