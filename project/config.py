# Refer to https://flask.palletsprojects.com/en/1.1.x/config/ for more information.
import os

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ['SECRET_KEY']
    DATABASE_URI = 'sqlite:///db.db'

class ProductionConfig(Config):
    #DATABASE_URI = 'mysql://user@localhost/foo'
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DEBUG = True