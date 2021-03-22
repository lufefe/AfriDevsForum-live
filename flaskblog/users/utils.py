import os
import secrets
from threading import Thread

from PIL import Image  # used to resize image sizes
from flask import current_app, render_template
from flask_mail import Message

from flaskblog import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)  # used for renaming the profile picture uniquely
    _, f_ext = os.path.splitext(form_picture.filename)  # splits filename to get the file extension
    picture_fn = random_hex + f_ext  # assigns the picture with a random filename
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)  # get the path of the file

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_reset_email(user):
    app = current_app._get_current_object()
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender = ('AfriDevsForum', 'no-reply@afridevsforum.com'),
                  recipients = [user.email],
                  html = render_template('email/password_reset_email.html', user = user, token = token))

    thr = Thread(target = send_async_email, args = [app, msg])
    thr.start()


def send_confirmation_email(user):
    app = current_app._get_current_object()
    token = user.generate_confirmation_token()
    msg = Message('Email Confirmation',
                  sender = ('AfriDevsForum', 'no-reply@afridevsforum.com'),
                  recipients = [user.email],
                  html = render_template('email/confirm_user_email.html', user = user, token = token))

    thr = Thread(target = send_async_email, args = [app, msg])
    thr.start()