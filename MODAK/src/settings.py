from configparser import ConfigParser
import logging
import os
import configparser

class settings:
    """All setting for MODAK will be stored here. Change it make it tasty"""

    @classmethod
    def initialise(cls, conf_file: str = '../conf/iac-model.ini'):
        my_conf_file = os.environ.get('MODAK_CONFIG', conf_file)
        logging.info("Reading ini file : {}".format(my_conf_file))
        try:
            config = ConfigParser()
            config.read(my_conf_file)
            cls.MODE = config.get("modak", "mode")
            cls.QUITE_SERVER_LOGS = False
            if  config.get("modak", "quite_server_log") == 'true':
                cls.QUITE_SERVER_LOGS = True
            section = cls.MODE
            cls.PRODUCTION = False
            if cls.MODE == 'prod':
                cls.PRODUCTION = True
            logging.info("Reading section {} of ini file ".format(section))
            cls.DB_NAME                 = config.get(section, "db_name")
            logging.info("db name :" + cls.DB_NAME)
            cls.DB_DIR                  = config.get(section, "db_dir")
            logging.info("db dir :" + cls.DB_DIR)
            cls.OUT_DIR = config.get(section, "out_dir")
            logging.info("out dir :" + cls.OUT_DIR)
            cls.HOST = config.get(section, "host")
            logging.info("host :" + cls.HOST)
            cls.PORT = config.get(section, "port")
            logging.info("port :" + cls.PORT)
            cls.USER = config.get(section, "user")
            logging.info("user :" + cls.USER)
            cls.PASSWORD = config.get(section, "password")
            logging.info("password : **** " )
        except configparser.Error as err:
            logging.error(str(err))
            raise RuntimeError(err)




