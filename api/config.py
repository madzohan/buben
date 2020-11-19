import os

# Statements for switching dev/prod environments

# creates StreamHandler which outputs to console
SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "").lower() == "true"  # False

DEBUG = os.getenv("FLASK_DEBUG", "").lower() == "true"  # False
TESTING = os.getenv("FLASK_TESTING", "").lower() == "true"  # False
ENV = os.getenv("FLASK_ENV", "production")

# Disable Signalling Support http://flask-sqlalchemy.pocoo.org/dev/signals/
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Define the database - we are working with
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "0.0.0.0")

SQLALCHEMY_DATABASE_URI = "postgresql://{user}:{password}@{host}/{dbname}?client_encoding=utf8".format(
    user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, dbname=POSTGRES_DB
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "{}": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json"
        },
    },
    "loggers": {
        "api": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": True,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
