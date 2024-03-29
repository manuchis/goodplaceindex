from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, json
import requests
from flask_login import current_user, login_required
from flask_principal import Principal, Permission, identity_loaded, RoleNeed, UserNeed
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.models import User, Post, Message, Notification, Company, Role, UserRoles
from app.translate import translate
from app.main import bp
from app.property.forms import PropertySearch
from app.main.forms import SearchForm
from app.property import bp
from geopy.geocoders import Nominatim

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

# Flask Principal
@identity_loaded.connect
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'roles'):
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role.name))

# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('admin'))

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def property():
    form = PropertySearch()
    if form.validate_on_submit():
    #    flash(_('You searched for a Property'))
        return redirect(url_for('property.property_details'))
    return render_template('property/index.html', title=_('Home'), form=form, maptoken=current_app.config['MAPBOX_TOKEN'])

@bp.route('/georeference', methods=['POST'])
@login_required
def georeference():
    try:
        geolocator = Nominatim(user_agent="goodplaceindex/1")
        location = geolocator.geocode(request.form["text"])
        return jsonify(location.raw)
                #{'place_id': 138642704, 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. https://osm.org/copyright', 'osm_type': 'way', 'osm_id': 264768896, 'boundingbox': ['40.7407597', '40.7413004', '-73.9898715', '-73.9895014'], 'lat': '40.7410861', 'lon': '-73.9896298241625', 'display_name': 'Flatiron Building, 175, 5th Avenue, Flatiron District, Manhattan, Manhattan Community Board 5, New York County, NYC, New York, 10010, USA', 'class': 'tourism', 'type': 'attraction', 'importance': 0.793003315521974, 'icon': 'https://nominatim.openstreetmap.org/images/mapicons/poi_point_of_interest.p.20.png'}
    except Exception as e:
        #return str(e)
        return jsonify({'text': str(e)})

@bp.route('/details', methods=['GET', 'POST'])
@login_required
def property_details():
    prop_data = requests.get(request.url_root+'static/property_example.json').json()
    return render_template('property/details.html', title=_('Property details'), prop_data=prop_data)
