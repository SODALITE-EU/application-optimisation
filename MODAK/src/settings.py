import configparser
import logging
import os
import pathlib
import re
from configparser import ConfigParser
from types import SimpleNamespace

DEFAULT_SETTINGS_DIR = pathlib.Path(__file__).parent.resolve().parent / "conf"


class SettingsNamespace(SimpleNamespace):
    """All settings required for MODAK will be stored in an instance of this."""

    def initialise(
        self, conf_file: pathlib.Path = DEFAULT_SETTINGS_DIR / "iac-model.ini"
    ):
        my_conf_file = os.environ.get("MODAK_CONFIG", conf_file)
        db_uri = os.environ.get("MODAK_DATABASE_URI")

        logging.info(f"Reading ini file : {my_conf_file}")
        try:
            config = ConfigParser()
            config.read(my_conf_file)
            self.MODE = config.get("modak", "mode")
            self.QUITE_SERVER_LOGS = False
            if config.get("modak", "quite_server_log") == "true":
                self.QUITE_SERVER_LOGS = True
            self.PRODUCTION = self.MODE == "prod"

            section = self.MODE
            logging.info(f"Reading section {section} of ini file ")
            self.DB_URI = db_uri if db_uri else config.get(section, "db_uri")

            match = re.match(
                r"(?P<dialect>mysql|sqlite)://"
                r"(?P<path>(?:(?P<username>[^@:]+)(?::(?P<password>[^@]+))?@)?"
                r"(?P<hostname>[^@/:]+)?(?::(?P<port>\d+))?/"
                r"(?P<dbname>.+))",
                Settings.DB_URI,
            )

            if not match:
                raise ValueError(f"Unable to parse db_uri '{Settings.DB_URI}'")

            self.DB_DIALECT = match["dialect"]

            if self.DB_DIALECT == "mysql":
                self.DB_USER = match["username"]
                self.DB_PASSWORD = match["password"] if match["password"] else ""
                self.DB_HOST = match["host"]
                self.DB_PORT = int(match["port"]) if match["port"] else 3306
                self.DB_NAME = match["dbname"]
            elif self.DB_DIALECT == "sqlite":
                # relative directories are taken as relative to the configuration file,
                # absolute dirs are maintained as such
                self.DB_PATH = conf_file.parent / match["path"]
            else:
                raise AssertionError(f"Invalid dialect: {match['dialect']}")

            self.OUT_DIR = pathlib.Path(config.get(section, "out_dir"))
            logging.info("out dir : {self.OUT_DIR}")

        except configparser.Error as exc:
            logging.exception(exc)
            raise


# The default settings
Settings = SettingsNamespace()
