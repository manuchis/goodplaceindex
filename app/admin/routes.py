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
from app.main.forms import SearchForm
from app.admin.forms import EditProfileForm
from app.admin import bp

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
@admin_permission.require()
def admin():
    users = User.query.order_by(User.username.asc())
    companies = Company.query.order_by(Company.name.asc())
    return render_template('admin/index.html', title=_('Admin'), users=users, companies=companies)

@bp.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_permission.require()
def admin_edit_user(id):

    user = User.query.filter_by(id=id).first_or_404()
    companies = Company.query.order_by(Company.name.asc())
    form = EditProfileForm(user.username)
    form.roles.choices = [(g.id, g.name) for g in Role.query.order_by('name')]
    if form.validate_on_submit():
        user.username = form.username.data
        user.about_me = form.about_me.data
        user.roles = Role.query.filter(Role.id.in_(form.roles.data)).all()
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('admin.admin_edit_user', id=id))
    elif request.method == 'GET':
        form.username.data = user.username
        form.about_me.data = user.about_me
        # pass roles id to list
        rls= user.roles
        rl = []
        for role in rls:
            rl.append(role.id)
        form.roles.data = rl
    return render_template('edit_profile.html', title=_('Edit user'), form=form)
