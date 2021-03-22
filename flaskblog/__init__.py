from flask import Flask
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from flaskblog.config import DevelopmentConfig

db = SQLAlchemy()  # new instance of a database
migrate = Migrate()  # migrate tracks db changes just like git
bcrypt = Bcrypt()  # new instance of bcrypt encryption for password on register
login_manager = LoginManager()  # new instance of LoginManager lib for handling user login sessions
login_manager.session_protection = 'strong'
login_manager.login_view = 'users.login'  # telling the extension where the login view is
login_manager.login_message_category = 'info'
mail = Mail()
ckeditor = CKEditor()
bootstrap = Bootstrap()
moment = Moment()  # for formatting dates


# admin = Admin(name = 'Afri Devs Forum', template_mode = 'bootstrap3')


def create_app():
    app = Flask(__name__)
    with app.app_context():
        # TODO : Change config class to Production for deployment
        app.config.from_object(DevelopmentConfig)
        initialize_extensions(app)
        register_blueprints(app)
    return app


def initialize_extensions(app):
    # admin.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    from flaskblog.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()


def register_blueprints(app):
    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.error_handler.handlers import errors

    app.register_blueprint(users)  # users is the Blueprint variable
    app.register_blueprint(posts)  # posts is the Blueprint variable
    app.register_blueprint(main)  # main is the Blueprint variable
    app.register_blueprint(errors)
