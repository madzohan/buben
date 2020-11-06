from flask import Flask


def create_app(app_config):
    app = Flask(__name__)

    # Configurations
    app.config.from_object(app_config)
    from api.models import db, ma, migrate
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    from api.resources import api_bp
    app.register_blueprint(api_bp)

    return app
