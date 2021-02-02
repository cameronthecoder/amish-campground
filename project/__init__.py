from flask.globals import current_app
from quart import Quart
from werkzeug.utils import import_string
from quart_cors import cors
from databases import Database
from async_sender import Mail
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
    mail = Mail(hostname=app.config['MAIL_SERVER'], port=app.config['MAIL_PORT'], use_tls=True, username=app.config['MAIL_USERNAME'], password=app.config['MAIL_PASSWORD'])
    database = Database(app.config['DATABASE_URI'])

    app.mail = mail

    @app.before_serving
    async def create_db_pool():
        try:
            await database.connect()
            app.logger.info(f'Connected to database {app.config["POSTGRES_DATABASE_NAME"]} on port {app.config["POSTGRES_PORT"]}')
        except Exception as e:
            app.logger.error(e)
        if database.is_connected:
            app.db = database
            # TODO: Add site created_at, image_url, and price_per_night fields
            # TODO: Add reservation payment_intent_id, email, created_at, and updated_at fields
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

    @app.after_serving
    async def disconnect_db():
        if database.is_connected:
            await database.disconnect()

    from project.views import view
    from project.api import api
    from project.admin import admin

    # Blueprints
    app.register_blueprint(view)
    app.register_blueprint(api)
    app.register_blueprint(admin)

    return app