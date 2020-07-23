from configparser import ConfigParser
import logging
import sys
from datetime import datetime, timedelta
from IaC_model_sql import IaC_model_sql

class IaC_model():

    def __init__(self, modeA = 'test', iniFileA = './conf/iac-model.ini'):
        self.mode = modeA
        self.iniFile = iniFileA
        logging.basicConfig(filename='../log/iac-model{}.log'.format(datetime.now().strftime("%b_%d_%Y_%H_%M_%S")), \
                        filemode='w', level=logging.DEBUG)
        logging.getLogger("py4j").setLevel(logging.ERROR)
        logging.info("Reading ini file".format(self.mode))
        config = ConfigParser()
        config.read(self.iniFile)
        logging.info(dict(config.items(self.mode)))
        self.database = config.get(self.mode, "DB_NAME")
        self.sql = IaC_model_sql(self.database)

    def add_infra(self, name, num_nodes, description):
        # stmt = "INSERT INTO infrastructure(\"infra_id\", \"name\", \"num_nodes\", \"is_active\", \"description\") \
        #         VALUES (1, 'TES', 1, 1, 'vsdvs');"
        df = self.sql.select_stmt("select max(infra_id) as infra_id from infrastructure")
        infra_id = -1
        if df.shape[0] == 1:
            infra_id = df['infra_id'].values[0] + 1

        stmt = 'INSERT INTO infrastructure (infra_id, name, num_nodes, is_active, description) \
               VALUES (' + str(infra_id) + ',' + strstr(name) + ',' + str(num_nodes) + ', 1 , ' + strstr(description) + ')'
        print(stmt)
        self.sql.insert_stmt(stmt)

    def add_queue(self, name,  description, node_spec, num_nodes, infra_name):
        df = self.sql.select_stmt("select infra_id from infrastructure where name = " + strstr(infra_name))
        infra_id = -1
        print(df.shape[0])
        if df.shape[0] == 1:
            infra_id = df['infra_id'].values[0]
        else:
            logging.error("NO or More than one infrastructure found ")
            print("NO infrastructure found ")
            return
        df = self.sql.select_stmt("select max(queue_id) as queue_id from queue")
        queue_id = -1
        if df.shape[0] == 1:
            queue_id = df['queue_id'].values[0] + 1
        print(queue_id)
        stmt = 'INSERT INTO queue(queue_id, name, description, node_spec, num_nodes, infra_id) \
                VALUES (' + str(queue_id) + ',' + strstr(name) + ',' + strstr(description) + \
               ',' + strstr(node_spec) + ',' + str(num_nodes) + ',' + str(infra_id) + ')'
        print(stmt)
        self.sql.insert_stmt(stmt)


def strstr(str):
    return '\'' + str + '\''

if __name__ == '__main__':
    model = IaC_model()
    #model.add_infra("TEST",2,"TEST")
    model.add_queue("TEST","TEST DESC", "GPU", 2, "TEST" )