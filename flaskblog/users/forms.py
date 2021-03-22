from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp

from flaskblog.models import User, Role


class RegistrationForm(FlaskForm):  # for registraion form input
    username = StringField('Username', validators = [DataRequired(), Length(min = 2, max = 20)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    country = SelectField('Select your country', validate_choice = True)
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # for validating if username already exists in database
    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()  # checks if username is in database
        if user:
            raise ValidationError('That username is taken. Please choose a different one')

    # for validating if email already exists in database
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')


class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min = 2, max = 20)])
    name = StringField('Full name', validators = [Length(0, 64)])
    email = StringField('Email', validators = [DataRequired(), Email()])
    country = SelectField('Country', validate_choice = True)
    about_me = TextAreaField('About me')
    picture = FileField('Update Profile Picture', validators = [FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    # for validating if username already exists in database
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username = username.data).first()  # checks if username is in database
            if user:
                raise ValidationError('That username is taken. Please choose a different one')

    # for validating if email already exists in database
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    # for validating if email is for a registered user
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must first register.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Length(1, 64),
                                               Email()])
    username = StringField('Username', validators = [
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Usernames must have only letters, '
                                              'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce = int)
    name = StringField('Full name', validators = [Length(0, 64)])
    country = SelectField('Country', validate_choice = True)
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email = field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username = field.data).first():
            raise ValidationError('Username already in use.')
