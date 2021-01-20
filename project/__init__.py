from quart import Quart
from quart_cors import cors
from databases import Database
from project import config
import os

def create_app(testing=False):
    app = Quart(__name__)
    app = cors(app)

    quart_env = os.getenv("QUART_ENV", None)

    if testing:
        app.config.from_object(config.TestingConfig)
    elif quart_env == "development":
        app.config.from_object(config.DevelopmentConfig)
    elif quart_env == "testing":
        app.config.from_object(config.TestingConfig)
    else:
        app.config.from_object(config.ProductionConfig)

    database = Database(app.config['DATABASE_URI'])


    @app.before_serving
    async def create_db_pool():
        await database.connect()
        app.db = database
        # GET db table information from SHOW CREATE TABLE

    @app.after_serving
    async def disconnect_db():
        await database.disconnect()

    from project.views import view
    from project.api import api
    from project.admin import admin

    app.register_blueprint(view)
    app.register_blueprint(api)
    app.register_blueprint(admin)

    return app