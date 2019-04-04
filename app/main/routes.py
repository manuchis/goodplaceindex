from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, json
import requests
from flask_login import current_user, login_required
from flask_principal import Principal, Permission, identity_loaded, RoleNeed, UserNeed
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, PostForm, SearchForm, MessageForm, PropertySearch, EditCompanyForm, CreateCompanyForm
from app.models import User, Post, Message, Notification, Company, Role, UserRoles
from app.translate import translate
from app.main import bp

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
def index():
    form = PropertySearch()
    if form.validate_on_submit():
        flash(_('You searched for a Property'))
        return redirect(url_for('main.index'))
    return render_template('index.html', title=_('Home'), form=form)
#  >>  for _dep_index.html original file >>
# form = PostForm()
#    if form.validate_on_submit():
#        language = guess_language(form.post.data)
#        if language == 'UNKNOWN' or len(language) > 5:
#            language = ''
#        post = Post(body=form.post.data, author=current_user,
#                    language=language)
#        db.session.add(post)
#        db.session.commit()
#        flash(_('Your post is now live!'))
#        return redirect(url_for('main.index'))
#    page = request.args.get('page', 1, type=int)
#    posts = current_user.followed_posts().paginate(
#        page, current_app.config['POSTS_PER_PAGE'], False)
#    next_url = url_for('main.index', page=posts.next_num) \
#        if posts.has_next else None
#    prev_url = url_for('main.index', page=posts.prev_num) \
#        if posts.has_prev else None
#    return render_template('index.html', title=_('Home'), form=form,
#                           posts=posts.items, next_url=next_url,
#                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

@bp.route('/property/<int:id>')
@login_required
def property(id):
    prop_data = requests.get(request.url_root+'static/property_example.json').json()
    return render_template('property.html', title=_('Property details'), prop_data=prop_data)

@bp.route('/company/<int:id>')
@login_required
def company(id):
    company = Company.query.filter_by(id=id).first_or_404()
    return render_template('company.html', company=company)

@bp.route('/company/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_company(id):
    company = Company.query.filter_by(id=id).first_or_404()
    form = EditCompanyForm(company.name)
    users = User.query.all()
    if current_user.id is not company.user_id:
        flash(_('You must be the company owner to edit it'))
        return redirect(url_for('main.index'));
    if form.validate_on_submit():
        company.name = form.name.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_company', id=id))
    elif request.method == 'GET':
        form.name.data = company.name
    return render_template('edit_company.html',  title=_('Edit Company'), company=company, form=form, users=users)

@bp.route('/company/<int:id>/delete')
@login_required
def delete_company(id):
    form = CreateCompanyForm()
    company = Company.query.filter_by(id=id).first_or_404()
    if current_user.id is not company.user_id:
        flash(_('You must be the company owner to edit it'))
        return redirect(url_for('main.index'));
    db.session.delete(company)
    db.session.commit()
    return render_template('new_company.html', form=form)

@bp.route('/company/new', methods=['GET', 'POST'])
@login_required
def new_company():
    form = CreateCompanyForm()
    if form.validate_on_submit():
        company = Company(name=form.name.data, user_id=current_user.id)
        db.session.add(company)
        db.session.commit()
        flash(_('Your changes have been saved.'))
        c = Company.query.filter_by(name=form.name.data).first()
        return redirect(url_for('main.edit_company', id=c.id))
    return render_template('new_company.html',  title=_('Create new Company'), form=form)

@bp.route('/company/<int:company_id>/fire/<int:user_id>')
@login_required
def company_fire(company_id, user_id):
    company = Company.query.filter_by(id=company_id).first_or_404()
    form = EditCompanyForm(company.name)
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.edit_company', title=_('Edit Company'), id=company.id, company=company, form=form))
    if user == current_user:
        flash(_('You cannot fire yourself!'))
        return redirect(url_for('main.edit_company', title=_('Edit Company'), id=company.id, company=company, form=form))
    company.fire(user)
    db.session.commit()
    flash(_('You fired %(username)s', username=user.username))
    return redirect(url_for('main.edit_company', title=_('Edit Company'), id=company.id, company=company, form=form))

@bp.route('/company/<int:company_id>/hire/<int:user_id>')
@login_required
@admin_permission.require()
def company_hire(company_id, user_id):
    company = Company.query.filter_by(id=company_id).first_or_404()
    form = EditCompanyForm(company.name)
    user = User.query.filter_by(id=user_id).first()
    ### falta la funcion !!
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.edit_company', title=_('Edit Company'), id=company.id, company=company, form=form))
    if user == current_user:
        flash(_('You cannot fire yourself!'))
        return redirect(url_for('main.edit_company', title=_('Edit Company'), id=company.id, company=company, form=form))

    company.hire(user)
    db.session.commit()
    flash(_('You added %(username)s to the company', username=user.username))
    return redirect(url_for('main.edit_company', title=_('Edit Company'), id=company.id, company=company, form=form))

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    companies = user.companies
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items, companies=companies,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_popup.html', user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash(_('An export task is currently in progress'))
    else:
        current_user.launch_task('export_posts', _('Exporting posts...'))
        db.session.commit()
    return redirect(url_for('main.user', username=current_user.username))


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])
