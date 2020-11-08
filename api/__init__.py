import logging

from flask import Flask

from api.resources import cache


def create_app(app_config):
    app = Flask(__name__)
    cache.init_app(app)

    # Configurations
    app.config.from_object(app_config)
    logging.basicConfig(level=logging.DEBUG if app.env == "development" else logging.INFO)

    from api.models import db, ma, migrate
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from api.resources import api_bp
        from api.commands import docs_bp

        app.register_blueprint(api_bp)
        app.register_blueprint(docs_bp, cli_group=None)

    return app
