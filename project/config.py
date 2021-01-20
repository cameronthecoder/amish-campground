# Refer to https://flask.palletsprojects.com/en/1.1.x/config/ for more information.

class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:///db.db'

class ProductionConfig(Config):
    #DATABASE_URI = 'mysql://user@localhost/foo'
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True