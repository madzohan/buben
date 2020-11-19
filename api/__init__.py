import logging
import logging.config

from flask import Flask

from api.resources import cache


def create_app(app_config):
    app = Flask(__name__)
    cache.init_app(app)

    # Configurations
    app.config.from_object(app_config)
    logging_config = app.config.get("LOGGING")
    if logging_config:
        logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
    logger.info(dict(action="create_app"))

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
