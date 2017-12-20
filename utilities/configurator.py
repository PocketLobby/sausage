import configparser
import os

os.environ.setdefault("ENV", "test")
class Configurator:
    """Config the app"""

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('sausage_config.conf')
        self.config = self.config[os.environ.get("ENV", "DEFAULT")]