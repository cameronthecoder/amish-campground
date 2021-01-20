from quart import Quart
from werkzeug.utils import import_string
from quart_cors import cors
from databases import Database
from project import config
import os

def create_app(testing=False):
    app = Quart(__name__)
    app = cors(app)

    quart_env = os.getenv("QUART_ENV", None)

    if testing:
        cfg = import_string('project.config.TestingConfig')()
    elif quart_env == "development":
        cfg = import_string('project.config.DevelopmentConfig')()
    elif quart_env == "testing":
        cfg = import_string('project.config.TestingConfig')()
    else:
        cfg = import_string('project.config.ProductionConfig')()
    app.config.from_object(cfg)


    database = Database(app.config['DATABASE_URI'], sslmode='require')

    @app.before_serving
    async def create_db_pool():
        await database.connect()
        app.db = database
        await app.db.execute("""
        CREATE TABLE IF NOT EXISTS "site" 
            (id SERIAL NOT NULL PRIMARY KEY,
            name CHAR(30) NOT NULL
            )
        """)
        await app.db.execute("""
        CREATE TABLE IF NOT EXISTS "reservation" (
            id SERIAL NOT NULL PRIMARY KEY,
            first_name CHAR(60) NOT NULL,
            last_name CHAR(60) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            site_id	INTEGER,
            FOREIGN KEY(site_id) REFERENCES site(id)
        )
        """)
        # GET db table information from SHOW CREATE TABLE

    @app.after_serving
    async def disconnect_db():
        await database.disconnect()

    from project.views import view
    from project.api import api
    from project.admin import admin

    # Blueprints
    app.register_blueprint(view)
    app.register_blueprint(api)
    app.register_blueprint(admin)

    return app