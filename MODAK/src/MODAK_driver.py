#!/usr/bin/env python3

import logging
import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, Union

import pandas as pd

# from MODAK_sql import MODAK_sql
from settings import DEFAULT_SETTINGS_DIR, Settings

print("This is the MODAK driver program")


class MODAK_driver:
    """This is the driver program that will drive the MODAK"""

    # dblist = []
    logging.basicConfig(
        filename=DEFAULT_SETTINGS_DIR
        / ".."
        / "log"
        / f"MODAK{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}.log",
        filemode="w",
        level=logging.DEBUG,
    )
    logging.getLogger("py4j").setLevel(logging.ERROR)

    def __init__(self, conf_file=DEFAULT_SETTINGS_DIR / "iac-model.ini", install=False):
        logging.info("Initialising driver")
        Settings.initialise(conf_file)

        logging.info("Connecting to model repo using DB dialect: {Settings.DB_DIALECT}")

        if Settings.DB_DIALECT == "mysql":
            import mysql.connector

            try:
                self.cnx = mysql.connector.connect(
                    user=Settings.DB_USER,
                    password=Settings.DB_PASSWORD,
                    host=Settings.DB_HOST,
                    port=Settings.DB_PORT,
                    database=Settings.DB_NAME,
                )
            except mysql.connector.Error:
                logging.exception(
                    f"Error connecting to MODAK repository DB '{Settings.DB_NAME}'"
                    f" on '{Settings.DB_HOST}' with user '{Settings.DB_USER}'"
                )
                raise

        elif Settings.DB_DIALECT == "sqlite":
            import sqlite3

            try:
                self.cnx = sqlite3.connect(Settings.DB_PATH)
            except Exception:
                logging.exception(
                    f"Error connecting to MODAK repository DB '{Settings.DB_PATH}'"
                )
                raise

        # self.__init_IaC_modelrepo(install)
        if Settings.QUITE_SERVER_LOGS:
            self._quiet_logs()

        logging.info("Successfully initialised driver")

    def __del__(self):
        try:
            self.cnx.close()
        except AttributeError:
            pass

    def applySQL(
        self, sqlstr: str, query_params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ):
        sqlstr = re.sub(r"\s{2,}", " ", sqlstr.replace("\n", " "))

        if Settings.DB_DIALECT == "sqlite":
            sqlstr = re.sub(r"%\((?P<key>[^\)]+)\)s", r":\g<key>", sqlstr)
            sqlstr = sqlstr.replace("%s", "?")

        if not sqlstr:
            logging.error("Empty or invalid sql string")
            raise ValueError("Empty or invalid SQL statement")

        try:
            logging.info(f"Executing : {sqlstr}")
            # cur = self.cnx.cursor()
            # cur.execute(sqlstr)
            # # Put it all to a data frame
            # sql_data = pd.DataFrame(data=cur.fetchall(), index=None,
            #                         columns=cur.column_names)
            sql_data = pd.read_sql(sqlstr, self.cnx, params=query_params)
            logging.info("Successfully executed SQL")
            return sql_data
        except AttributeError:
            logging.warning("No connected database")
            return pd.DataFrame()
        except Exception:
            logging.exception("Error executing SQL")
            raise

    def selectSQL(
        self, sqlstr: str, query_params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ):
        sqlstr = re.sub(r"\s{2,}", " ", sqlstr.replace("\n", " "))

        if Settings.DB_DIALECT == "sqlite":
            sqlstr = re.sub(r"%\((?P<key>[^\)]+)\)s", r":\g<key>", sqlstr)
            sqlstr = sqlstr.replace("%s", "?")

        if not sqlstr:
            logging.error("Empty or invalid sql string")
            raise ValueError("Empty or invalid SQL statement")

        try:
            logging.info(f"Selecting : {sqlstr}")
            # cur = self.cnx.cursor()
            # cur.execute(sqlstr)
            # # Put it all to a data frame
            # sql_data = pd.DataFrame(data=cur.fetchall(), index=None,
            #                         columns=cur.column_names)
            sql_data = pd.read_sql(sqlstr, self.cnx, params=query_params)
            logging.info("Successfully selected SQL")
            return sql_data
        except AttributeError:
            logging.warning("No connected database")
            return pd.DataFrame()
        except Exception:
            logging.exception("Error executing SQL")
            raise

    def updateSQL(
        self, sqlstr, query_params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ):
        sqlstr = re.sub(r"\s{2,}", " ", sqlstr.replace("\n", " "))

        if Settings.DB_DIALECT == "sqlite":
            sqlstr = re.sub(r"%\((?P<key>[^\)]+)\)s", r":\g<key>", sqlstr)
            sqlstr = sqlstr.replace("%s", "?")

        if not sqlstr:
            logging.error("Empty or invalid sql string")
            raise ValueError("Empty or invalid SQL statement")

        try:
            logging.info(f"Updating : {sqlstr}")
            cur = self.cnx.cursor()
            cur.execute(sqlstr, query_params)
            # # Put it all to a data frame
            self.cnx.commit()
            logging.info("Successfully updated SQL")
            return True
        except AttributeError:
            logging.warning("No connected database")
            return False
        except Exception:
            logging.exception("Error connecting to modak repo")
            raise

    def _quiet_logs(self):
        pass


def main():
    print("Test MODAK driver")
    driver = MODAK_driver()
    df = driver.applySQL("SELECT * FROM optimisation")
    print(df["app_name"])


if __name__ == "__main__":
    main()
