from api import create_app
from api import config as app_config_obj

app = create_app(app_config_obj)
