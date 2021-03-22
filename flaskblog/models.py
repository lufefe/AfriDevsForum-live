import re
from datetime import datetime

import bleach
from flask import current_app
from flask_admin import expose, AdminIndexView, Admin
from flask_admin.contrib.sqla import ModelView
# UserMixin is a class that we inherit from the required methods & attributes used in managing login sessions
from flask_login import UserMixin, AnonymousUserMixin
from flask_login import current_user
# Serializer will be used for generating tokens for 'Forgot Password'
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown

from flaskblog import db, login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTRATOR = 0x80


class Role(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref = 'role', lazy = 'dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name = r).first()
            if role is None:
                role = Role(name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class User(db.Model, UserMixin):  # this class is used for creating the database table User
    id = db.Column(db.Integer, primary_key = True)  # id attribute/column that is an integer and primary key
    name = db.Column(db.String(64))
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    country = db.Column(db.String(20), nullable = False)
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime, default = datetime.utcnow)
    image_file = db.Column(db.String(20), nullable = False, default = 'default.jpg')
    password = db.Column(db.String(60), nullable = True)
    confirmed = db.Column(db.Boolean, default = False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    posts = db.relationship('Post', backref = 'author',
                            lazy = True)  # defining a relationship between user(author) & post
    comments = db.relationship('Comment', backref = 'author', lazy = 'dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name = 'Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)

    def generate_confirmation_token(self, expiration = 3600):  # email confirmation
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    # author is a back reference which gives us access to the entire User model and the attributes
    # the posts variable will then be used in routes and views

    def get_reset_token(self, expires_sec = 1800):  # generates a token that will expire in 30 mins (1800 secs)
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)  # creates a serializer
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod  # tells python that this method won't have the 'self' object - it's a static method
    def verify_reset_token(token):  # verifies if token hasn't expired
        s = Serializer(current_app.config['SECRET_KEY'])  # creates a serializer
        try:
            user_id = s.loads(token)['user_id']  # tries to load the token to user_id
        except:
            return None  # returns None if token has expired
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader  # decorator used for reloading the user based on the user id stored in the session
def load_user(user_id):  # this function gets the user id
    return User.query.get(int(user_id))


post_tag = db.Table('post_tag',
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
                    )


class Post(db.Model):
    __searchable__ = ['title', 'content']
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    date_posted = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    content = db.Column(db.Text, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)  # a foreign key
    tag = db.relationship('Tag', secondary = post_tag, backref = 'post', lazy = 'dynamic')
    comments = db.relationship('Comment', backref = 'post', lazy = 'dynamic')

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


def slugify_tag(s):
    return re.sub('[^\w]+', '-', s).lower()


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    slug = db.Column(db.String(64), unique = False)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.slug = slugify_tag(self.name)

    def __repr__(self):
        return '<Tag %s>' % self.name


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul', 's',
                        'pre', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format = 'html'),
                                                       tags = allowed_tags, strip = True))

    def __repr__(self):
        return f"Comment('{self.body}', '{self.timestamp}')"


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


# Admin site setup
class MyAdminHome(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_authenticated and current_user.can(Permission.ADMINISTRATOR):
            return self.render('admin/index.html')
        else:
            return self.render('errors/403.html')


admin = Admin(app = current_app, name = 'Afri Devs Forum', template_mode = 'bootstrap3', index_view = MyAdminHome())

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ModelView(Comment, db.session))
admin.add_view(ModelView(Role, db.session))
