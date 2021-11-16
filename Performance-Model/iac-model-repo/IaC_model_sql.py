import sqlite3
from sqlite3 import Error
import logging
import pandas as pd


class IaC_model_sql():


    tables = ['application',
              'application_type',
              'benchmark',
              'infrastructure',
              'opt_map',
              'queue',
              'audit_logs',
              'features',
              'model',
              'optimisation',]

    def __init__(self,  file='./conf/iac-model.db'):
        self.db_file = file
        try:
            self.conn = sqlite3.connect(self.db_file)
            logging.info("Successfuly connected to file:" + self.db_file)
        except Error as e:
            logging.error(e)

    def create_table(self, create_table_sql):
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            logging.error(e)

    def select_stmt(self, statement_sql):
        try:
            c = self.conn.cursor()
            query = c.execute(statement_sql)
            cols = [column[0] for column in query.description]
            results = pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
            return results
        except Error as e:
            logging.error(e)

    def insert_stmt(self, statement_sql):
        try:
            c = self.conn.cursor()
            c.execute(statement_sql)
            c.execute("commit;")
        except Error as e:
            logging.error(e)

    def drop_table(self, table_name):
        try:
            drop_table_sql = "drop table " + table_name
            c = self.conn.cursor()
            c.execute(drop_table_sql)
        except Error as e:
            logging.error(e)