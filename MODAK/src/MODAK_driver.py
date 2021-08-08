#!/usr/bin/env python3

import logging
import re
from datetime import datetime

import mysql.connector
import pandas as pd

# from MODAK_sql import MODAK_sql
from settings import settings

print("This is the MODAK driver program")


class MODAK_driver:
    """This is the driver program that will drive the MODAK"""

    dblist = []
    tablelist = []
    db_dir = ""
    logging.basicConfig(
        filename=f"../log/MODAK{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}.log",
        filemode="w",
        level=logging.DEBUG,
    )
    logging.getLogger("py4j").setLevel(logging.ERROR)

    def __init__(self, conf_file="../conf/iac-model.ini", install=False):
        logging.info("Intialising driver")
        settings.initialise(conf_file)
        self.dbname = settings.DB_NAME
        logging.info(f"selected DB : {self.dbname}")
        # Provide your Spark-master node below
        logging.info("Connecting to model repo")
        try:
            self.cnx = mysql.connector.connect(
                user=settings.USER,
                password=settings.PASSWORD,
                host=settings.HOST,
                port=settings.PORT,
                database=settings.DB_NAME,
            )
        except mysql.connector.Error as err:
            logging.error("Error connecting to modak repo")
            logging.error(err)

        # self.__init_IaC_modelrepo(install)
        if settings.QUITE_SERVER_LOGS:
            self._quiet_logs()
        logging.info("Successfully initialised driver")

    def __del__(self):
        try:
            self.cnx.close()
        except AttributeError:
            pass

    # def __init_IaC_modelrepo(self, install=False):
    #     logging.info("Initialising IaC Model repo")
    #     if install == True:
    #         self.applySQL('create database ' + self.dbname)
    #         for table in MODAK_sql.table_create_stmt.keys():
    #             self.applySQL("drop table " + table)
    #             logging.info(MODAK_sql.table_create_stmt[table].format(settings.DB_DIR))
    #             self.applySQL(MODAK_sql.table_create_stmt[table].format(settings.DB_DIR))
    #
    #     dfdb = self.sqlContextHive.sql('show databases')
    #     dfdb.show()
    #     for record in dfdb.select('namespace').collect():
    #         self.dblist.append(record[0])
    #     logging.info("Available DBs : {}".format(self.dblist))
    #     if self.dbname in self.dblist:
    #         self.applySQL("use {}".format(self.dbname))
    #     else:
    #         self.applySQL("create database {}".format(self.dbname))
    #         self.applySQL("use {}".format(self.dbname))

    def applySQL(self, sqlstr):
        re.sub(r"\s\s+", " ", sqlstr)
        if sqlstr != "":
            try:
                logging.info(f"Executing : {sqlstr}")
                # cur = self.cnx.cursor()
                # cur.execute(sqlstr)
                # # Put it all to a data frame
                # sql_data = pd.DataFrame(data=cur.fetchall(), index=None,
                #                         columns=cur.column_names)
                sql_data = pd.read_sql(sqlstr, self.cnx)
                logging.info("Successfully executed SQL")
                return sql_data
            except AttributeError:
                logging.warning("No connected database")
                return pd.DataFrame()
            except mysql.connector.Error as err:
                logging.error("Error executing sql")
                logging.error(err)
                raise RuntimeError(err)
            except Exception as excpt:
                logging.warning(str(excpt))
                raise RuntimeError(excpt)
        else:
            logging.error("Empty or invalid sql string")
            raise ValueError("Empty or invalid SQL statement")

    def selectSQL(self, sqlstr):
        re.sub(r"\s\s+", " ", sqlstr)
        if sqlstr != "":
            try:
                logging.info(f"Selecting : {sqlstr}")
                # cur = self.cnx.cursor()
                # cur.execute(sqlstr)
                # # Put it all to a data frame
                # sql_data = pd.DataFrame(data=cur.fetchall(), index=None,
                #                         columns=cur.column_names)
                sql_data = pd.read_sql(sqlstr, self.cnx)
                logging.info("Successfully selected SQL")
                return sql_data
            except AttributeError:
                logging.warning("No connected database")
                return pd.DataFrame()
            except mysql.connector.Error as err:
                logging.error("Error executing sql")
                logging.error(err)
                raise RuntimeError(err)
            except Exception as excpt:
                logging.warning(str(excpt))
                raise RuntimeError(excpt)
        else:
            logging.error("Empty or invalid sql string")
            raise ValueError("Empty or invalid SQL statement")

    def updateSQL(self, sqlstr):
        re.sub(r"\s\s+", " ", sqlstr)
        if sqlstr != "":
            try:
                logging.info(f"Updating : {sqlstr}")
                cur = self.cnx.cursor()
                cur.execute(sqlstr)
                # # Put it all to a data frame
                self.cnx.commit()
                logging.info("Successfully updated SQL")
                return True
            except AttributeError:
                logging.warning("No connected database")
                return False
            except mysql.connector.Error as err:
                logging.error("Error executing sql")
                logging.error(err)
                raise RuntimeError(err)
            except Exception as excpt:
                logging.warning(str(excpt))
                raise RuntimeError(excpt)
        else:
            logging.error("Empty or invalid sql string")
            raise ValueError("Empty or invalid SQL statement")

    def _quiet_logs(self):
        pass


def main():
    print("Test MODAK driver")
    driver = MODAK_driver()
    df = driver.applySQL("select * from optimisation")
    print(df["app_name"])


if __name__ == "__main__":
    main()
