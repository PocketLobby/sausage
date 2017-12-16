import configparser
import os

os.environ.setdefault("ENV", "test")
class Configurator:
    "Config the app, TODO: move this out to be shared by all modules"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('sausage_config.conf')
        # TODO: set the env through an env variable
        self.config = self.config[os.environ.get("ENV", "DEFAULT")]