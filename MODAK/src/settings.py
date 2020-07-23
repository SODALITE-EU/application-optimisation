from configparser import ConfigParser
import logging
class settings:
    """All setting for MODAK will be stored here. Change it make it tasty"""

    @classmethod
    def initialise(cls, conf_file: str = '../conf/iac-model.ini'):
        logging.info("Reading ini file : {}".format(conf_file))
        config = ConfigParser()
        config.read(conf_file)
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
        cls.PORT = config.get(section, "port")
        logging.info("port :" + cls.PORT)
        cls.USER = config.get(section, "user")
        logging.info("user :" + cls.USER)
        cls.PASSWORD = config.get(section, "password")
        logging.info("password : **** " )



