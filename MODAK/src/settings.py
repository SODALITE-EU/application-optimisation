import configparser
import logging
import os
import pathlib
from configparser import ConfigParser
from types import SimpleNamespace

DEFAULT_SETTINGS_DIR = pathlib.Path(__file__).parent.resolve().parent / "conf"


class SettingsNamespace(SimpleNamespace):
    """All settings required for MODAK will be stored in an instance of this."""

    def initialise(
        self, conf_file: pathlib.Path = DEFAULT_SETTINGS_DIR / "iac-model.ini"
    ):
        my_conf_file = os.environ.get("MODAK_CONFIG", conf_file)
        database_user = os.environ.get("MODAK_DATABASE_USER")
        database_password = os.environ.get("MODAK_DATABASE_PASSWORD")
        database_host = os.environ.get("MODAK_DATABASE_HOST")
        database_port = os.environ.get("MODAK_DATABASE_PORT")

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
            self.DB_NAME = config.get(section, "db_name")
            logging.info(f"db name : {self.DB_NAME}")
            self.DB_DIR = pathlib.Path(config.get(section, "db_dir"))
            logging.info(f"db dir : {self.DB_DIR}")
            self.OUT_DIR = pathlib.Path(config.get(section, "out_dir"))
            logging.info("out dir : {self.OUT_DIR}")
            self.HOST = database_host if database_host else config.get(section, "host")
            logging.info(f"host : {self.HOST}")
            self.PORT = database_port if database_port else config.get(section, "port")
            logging.info(f"port : {self.PORT}")
            self.USER = database_user if database_user else config.get(section, "user")
            logging.info(f"user : {self.USER}")
            self.PASSWORD = (
                database_password
                if database_password
                else config.get(section, "password")
            )
            logging.info("password : **** ")

        except configparser.Error as err:
            logging.error(str(err))
            raise RuntimeError(err)


# The default settings
Settings = SettingsNamespace()
