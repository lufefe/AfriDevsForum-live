import json

import requests
from flask import render_template, url_for, flash, redirect, request, abort, current_app, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.decorators import admin_required
from flaskblog.models import User, Post, Role
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm, EditProfileAdminForm)
from flaskblog.users.utils import save_picture, send_reset_email, send_confirmation_email

app = current_app._get_current_object()

users = Blueprint('users', __name__)

try:
    r = requests.get('https://restcountries.eu/rest/v2/region/africa')
    countries = r.json()
except ValueError:
    with open('flaskblog\static\json\countries.json') as json_file:
        countries = json.load(json_file)


@users.before_app_request
def before_request():
    # user = Comment.query.get(2)
    # db.session.delete(user)
    # db.session.commit()
    if current_user.is_authenticated:
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'users' \
                and request.endpoint != 'static':
            return redirect(url_for('users.unconfirmed'))


@users.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.home'))
    return render_template('unconfirmed.html')


def subscribe_user(email, user_group, api_key):
    resp = requests.post(f"https://api.eu.mailgun.net/v3/lists/{user_group}/members",
                         auth = ("api", api_key),
                         data = {"subscribed": True, "address": email})

    print(resp.status_code)


@users.route("/register", methods = ['GET', 'POST'])
def register():
    user_count = db.session.query(User).count()

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    form.country.choices = [(i['name'], i['name']) for i in countries]

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, country = form.country.data,
                    password = hashed_password)
        db.session.add(user)
        db.session.commit()
        send_confirmation_email(user)
        flash('A confirmation email has been sent to you by email.', 'info')
        # flash('Your account has been created! You are now able to log in',
        #     'success')  # messages that pop up, 'success' is used for bootstrap
        subscribe_user(user.email, "devs@app.afridevsforum.com", app.config['MAIL_API_KEY'])
        return redirect(url_for('users.login'))
    return render_template('register.html', title = 'Register', form = form, user_count = user_count)


@users.route("/login", methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')  # gets the 'next 'parameter(s) from url if it exists
            return redirect(next_page) if next_page else redirect(
                url_for('main.home'))  # ternary condition for next_page
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title = 'Login', form = form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/user-profile/<string:username>")
def user_profile(username):
    page = request.args.get('page', 1, type = int)
    user = User.query.filter_by(username = username).first_or_404()
    image_file = url_for('static', filename = 'profile_pics/' + user.image_file)
    posts = Post.query.filter_by(author = user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page = page, per_page = current_app.config['FLASKY_POSTS_PER_PAGE'])
    if user and posts is None:
        abort(404)
    return render_template('user_profile.html', user = user, image_file = image_file, posts = posts)


@users.route("/account", methods = ['GET', 'POST'])
@login_required  # decorator to tell the user must be logged in in order to access the account page/view
def account():
    form = UpdateAccountForm()
    form.country.choices = [(i['name'], i['name']) for i in countries]

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data  # update the current user's username with the one if form
        current_user.email = form.email.data
        current_user.country = form.country.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.country.data = current_user.country
        form.about_me.data = current_user.about_me
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title = 'Account', image_file = image_file, form = form)


# admin profile
@users.route('/edit-profile/<int:id>', methods = ['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user = user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username = user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.country.data = user.country
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form = form, user = user)


@users.route("/reset_password", methods = ['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title = 'Reset Password', form = form)


@users.route("/reset_password/<token>", methods = ['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in',
              'success')  # messages that pop up, 'suucess' is used for bootstrap
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title = 'Reset Password', form = form)


@users.route("/confirm/<token>", methods = ['GET', 'POST'])
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'warning')
    return redirect(url_for('main.home'))


@users.route('/confirm')
@login_required
def resend_confirmation():
    send_confirmation_email(current_user)
    flash('A new confirmation email has been sent to you by email.', 'success')
    return redirect(url_for('users.login'))
