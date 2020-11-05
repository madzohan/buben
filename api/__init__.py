from flask import Flask


def create_app(app_config):
    app = Flask(__name__)

    # Configurations
    app.config.from_object(app_config)
    from api.resources import api
    from api.models import db, ma, migrate
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)

    return app
