# Refer to https://flask.palletsprojects.com/en/1.1.x/config/ for more information.
import os

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ["SECRET_KEY"]
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT", 5432)
    POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
    POSTGRES_DATABASE_NAME = os.environ.get('POSTGRES_DATABASE_NAME')
    SSL_ENABLED = False


    @property
    def DATABASE_URI(self):
        if os.environ.get("DATABASE_URL") == None:
            return 'postgresql://%s:%s@%s:%s/%s' % (
                self.POSTGRES_USER, 
                self.POSTGRES_PASSWORD, 
                self.POSTGRES_HOST,
                str(self.POSTGRES_PORT), 
                self.POSTGRES_DATABASE_NAME
            )
        else:
            print(os.environ['DATABASE_URL'] + "?sslmode=require")
            return os.environ['DATABASE_URL'] + "?min_size=1&max_size=3"

class ProductionConfig(Config):
    SSL_ENABLED = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DEBUG = True