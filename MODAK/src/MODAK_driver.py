#! /bin/python
print("This is the MODAK driver program")
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
from settings import settings
from MODAK_sql import MODAK_sql
import logging
import re


class MODAK_driver():
    """This is the driver program that will drive the MODAK """
    dblist = []
    tablelist = []
    db_dir = ""
    logging.basicConfig(filename='../log/MODAK{}.log'.format(datetime.now().strftime("%b_%d_%Y_%H_%M_%S")), \
                        filemode='w', level=logging.DEBUG)
    logging.getLogger("py4j").setLevel(logging.ERROR)


    def __init__(self, conf_file='../conf/iac-model.ini', install=False):
        settings.initialise(conf_file)
        self.dbname = settings.DB_NAME
        logging.info("selected DB : {}".format(self.dbname))
        # Provide your Spark-master node below
        self.cnx = mysql.connector.connect(user=settings.USER, password=settings.PASSWORD,
                                       host='localhost',
                                       database=settings.DB_NAME)
        # self.__init_IaC_modelrepo(install)
        if settings.QUITE_SERVER_LOGS:
            self._quiet_logs()

    def __del__(self):
        self.cnx.close()

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
        re.sub("\s\s+", " ", sqlstr)
        if sqlstr != "":
            try:
                logging.info("Executing : {}".format(sqlstr))
                # cur = self.cnx.cursor()
                # cur.execute(sqlstr)
                # # Put it all to a data frame
                # sql_data = pd.DataFrame(data=cur.fetchall(), index=None, columns=cur.column_names)
                sql_data = pd.read_sql(sqlstr, self.cnx)
                return sql_data

            except Exception as excpt:
                logging.warning(str(excpt))
        else:
            logging.error("Empty or invalid sql string")
            raise ValueError("Empty or invalid SQL statement")

    def selectSQL(self, sqlstr):
        re.sub("\s\s+", " ", sqlstr)
        if sqlstr != "":
            try:
                logging.info("Executing : {}".format(sqlstr))
                # cur = self.cnx.cursor()
                # cur.execute(sqlstr)
                # # Put it all to a data frame
                # sql_data = pd.DataFrame(data=cur.fetchall(), index=None, columns=cur.column_names)
                sql_data = pd.read_sql(sqlstr, self.cnx)
                return sql_data

            except Exception as excpt:
                logging.warning(str(excpt))
        else:
            logging.error("Empty or invalid sql string")
            raise ValueError("Empty or invalid SQL statement")

    def updateSQL(self, sqlstr):
        re.sub("\s\s+", " ", sqlstr)
        if sqlstr != "":
            try:
                logging.info("Executing : {}".format(sqlstr))
                cur = self.cnx.cursor()
                cur.execute(sqlstr)
                # # Put it all to a data frame
                self.cnx.commit()
                return True
            except Exception as excpt:
                logging.warning(str(excpt))
        else:
            logging.error("Empty or invalid sql string")
            raise ValueError("Empty or invalid SQL statement")

    def _quiet_logs(self):
        pass

def main():
    print('Test MODAK driver')
    driver = MODAK_driver()
    df = driver.applySQL("select * from optimisation")
    print(df['app_name'])

if __name__ == '__main__':
    main()