from os import environ
import json


class Config(object):
    # Config basics
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Email config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_USE_TLS = True
    MAIL_PORT = 587

    # Blog parameters
    FLASKY_COMMENTS_PER_PAGE = 4
    FLASKY_POSTS_PER_PAGE = 7
    FLASKY_ADMIN = environ.get('FLASKY_ADMIN')
    MAX_SEARCH_RESULTS = 50


class ProductionConfig(Config):
    DEBUG = False
    # TESTING = False
    # FLASK_ENV = 'production'
    #
    # with open('/etc/config.json') as config_file:
    #     config = json.load(config_file)
    #     SECRET_KEY = config.get('SECRET_KEY')
    #     SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    #     MAIL_API_KEY = config.get('MAIL_API_KEY')
    #     MAIL_USERNAME = config.get('MAIL_USER')
    #     MAIL_PASSWORD = config.get('MAIL_PASS')
    #     FLASKY_ADMIN = config.get('FLASKY_ADMIN')


class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = False
    SECRET_KEY = environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_TEST_DATABASE_URI')
    MAIL_USERNAME = environ.get('MAIL_USER')
    MAIL_PASSWORD = environ.get('MAIL_PASS')
    MAIL_API_KEY = environ.get('MAIL_API_KEY')
