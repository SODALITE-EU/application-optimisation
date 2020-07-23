import os,errno
from MODAK_driver import MODAK_driver
import logging
import json
from opt_dsl_reader import opt_dsl_reader

class mapper():

    def __init__(self, driver:MODAK_driver):
        logging.info("Initialised MODAK mapper")
        self.driver = driver
        self.opts = []

    def map_container(self, opt_json_obj):
        print(opt_json_obj.get('job').get('optimisation'))
        reader = opt_dsl_reader(opt_json_obj['job'])
        dsl_code = self.decode_ai_training_opt(reader)
        return self.get_container(dsl_code)

    def add_container(self, opt_dsl_code:str, container_file:str, image_hub:str='docker', image_type:str='docker', src: str=''):

        stmt = "INSERT INTO `mapper`(`map_id`,`opt_dsl_code`,`container_file`,`image_type`,`image_hub`,`src`) VALUES" \
               "(NULL,'{opt_dsl_code}','{container_file}','{image_type}','{image_hub}','{src}')"
        print(stmt.format( opt_dsl_code=opt_dsl_code, container_file=container_file,
                           image_type=image_type, image_hub=image_hub, src=src))
        self.driver.updateSQL(stmt.format( opt_dsl_code=opt_dsl_code, container_file=container_file,
                                          image_type=image_type, image_hub=image_hub, src=src))
        return True

    def add_optimisation(self, opt_dsl_code: str, app_name: str,  target: dict, optimisation: dict):
        target_str = ""
        for key in target:
            target_str = target_str + str(key).lower() + ":" + str(target[key]).lower() + ","
        opt_str = ""
        for key in optimisation:
            opt_str = opt_str + str(key).lower() + ":" + str(optimisation[key]).lower() + ","

        print(target_str)
        print(opt_str)
        stmt = "INSERT INTO `optimisation`(`opt_dsl_code`,`app_name`,`target`,`optimisation`,`version`) VALUES " \
               "('{opt_dsl_code}','{app_name}','{target}','{optimisation}','{version}')"

        print(stmt.format(opt_dsl_code=opt_dsl_code, app_name=app_name,
                          target=target_str, optimisation=opt_str, version=''))
        self.driver.updateSQL(stmt.format(opt_dsl_code=opt_dsl_code, app_name=app_name,
                                         target=target_str, optimisation=opt_str, version=''))
        return True

    def get_container(self, opt_dsl_code:str):
        stmt = "select container_file, image_type, image_hub from mapper \
                where opt_dsl_code='{}' order by map_id desc limit 1"
        print(stmt.format(opt_dsl_code))
        df = self.driver.applySQL(stmt.format(opt_dsl_code))
        if df.size > 0:
            container_file = df['container_file'][0]
            image_hub = df['image_hub'][0]
            return str(image_hub) + str(':')+str(container_file)
        else:
            return None

    def get_json_nodes(self,target_str: str):
        target_str = target_str.replace('{', '')
        target_str = target_str.replace('}', '')
        target_str = target_str.replace('"', '')
        target_str = target_str.replace('\'', '')
        target_str = target_str.replace('\\', '')
        target_str = target_str.replace(' ', '')
        if target_str == '':
            return ['']
        target_nodes = target_str.split(',')
        return target_nodes

    def decode_ai_training_opt(self,opt_dsl:opt_dsl_reader):
        app_type = opt_dsl.get_app_type()
        if not app_type == 'ai_training':
            return ""
        config = opt_dsl.get_app_config()
        data = opt_dsl.get_app_data()
        ai_framework = config['ai_framework']
        if opt_dsl.enable_opt_build():
            target = opt_dsl.get_opt_build()
        else:
            target = u'{"cpu_type":"none","acc_type":"none"}'
            target = u'{}'

        optimisation = opt_dsl.get_opt_list(ai_framework)

        sqlstr = "select opt_dsl_code from optimisation where app_name = '{}'".format(ai_framework)
        print(sqlstr)

        target_nodes = self.get_json_nodes(json.dumps(target))
        for t in target_nodes:
            print(t)
            targetstr = " and target like '%{}%'".format(t)
            sqlstr = sqlstr + targetstr

        if opt_dsl.enable_opt_build():
            sqlstr = sqlstr + " and target like '%enable_opt_build:true%'"
        else:
            sqlstr = sqlstr + " and target like '%enable_opt_build:false%'"

        print(str(optimisation))
        opt_nodes = self.get_json_nodes(json.dumps(optimisation))
        print(opt_nodes)
        for t in opt_nodes:
            print(t)
            optstr = " and optimisation like '%{}%'".format(t)
            sqlstr = sqlstr + optstr
            self.opts.append(t)

        print(sqlstr)
        df = self.driver.selectSQL(sqlstr)
        if df.size > 0:
            dsl_code = df['opt_dsl_code'][0]
        else:
            dsl_code = None
        return dsl_code

    def get_opts(self):
        return self.opts

def main():
    driver = MODAK_driver()
    m = mapper(driver)
    print('Test mapper main')
    # m.add_container('TF_PIP_XLA','AI/containers/tensorflow/tensorflow_pip_xla')
    # print(m.get_container('TF_PIP_XLA'))
    # target_string = u'{"cpu_type":"x86","acc_type":"nvidia"}'
    # opt_string = u'{"xla":true,"version":"1.1"}'
    # print(json.loads(target_string))
    # print(json.loads(opt_string))
    # m.add_optimisation('TF_PIP_XLA','tensorflow',json.loads(target_string),json.loads(opt_string))

    # obj = json.loads(json_string)
    # print(obj['cpu_type'])
    reader = opt_dsl_reader('../conf/tf_optimisation_dsl.json')
    dsl_code = m.decode_ai_training_opt(reader)
    print(dsl_code)

if __name__ == '__main__':
    main()