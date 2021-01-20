# Refer to https://flask.palletsprojects.com/en/1.1.x/config/ for more information.
import os

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ['SECRET_KEY']
    POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
    POSTGRES_USERNAME = os.environ['POSTGRES_USERNAME']
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_DATABASE_NAME = os.environ['POSTGRES_DATABASE_NAME']


    @property
    def DATABASE_URI(self):
        return 'postgresql://%s:%s@%s:%s/%s' % (
            self.POSTGRES_USERNAME, 
            self.POSTGRES_PASSWORD, 
            self.POSTGRES_HOST,
            str(self.POSTGRES_PORT), 
            self.POSTGRES_DATABASE_NAME
        )


class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DEBUG = True