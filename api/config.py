import os

# Statements for switching dev/prod environments
SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "").lower() == "true"  # False
DEBUG = os.getenv("DEBUG", "").lower() == "true"  # False
ENV = os.getenv("ENV", "production")

# Disable Signalling Support http://flask-sqlalchemy.pocoo.org/dev/signals/
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
POSTGRES_DB = os.environ.get("POSTGRES_DB")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "0.0.0.0")

SQLALCHEMY_DATABASE_URI = "postgresql://{user}:{password}@{host}/{dbname}?client_encoding=utf8".format(
    user=POSTGRES_USER, password=POSTGRES_PASSWORD, host=POSTGRES_HOST, dbname=POSTGRES_DB
)
