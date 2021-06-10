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
        logging.info("Mapping to optimal container")
        logging.info(str(opt_json_obj.get('job').get('optimisation')))
        reader = opt_dsl_reader(opt_json_obj['job'])
        app_type = reader.get_app_type()
        dsl_code = None
        if opt_json_obj['job'].get('target') is not None:
            if opt_json_obj['job'].get('target').get('name') is not None:
                target_name = opt_json_obj['job'].get('target').get('name').strip()
                self.opts.append('{}:true'.format(target_name))

        # if app_type == 'ai_training':
        #     logging.info('Decoding AI training application')
        #     dsl_code = self.decode_ai_training_opt(reader)
        # if app_type == 'hpc':
        #     logging.info('Decoding HPC application')
        #     dsl_code = self.decode_hpc_opt(reader)
        # else:
        #     logging.warning('Unknown application type')
        #     dsl_code = self.decode_hpc_opt(reader)
        dsl_code = self.decode_opt(reader)
        logging.info('Decoded opt code: ' + str(dsl_code))
        return self.get_container(dsl_code)

    def add_optcontainer(self, map_obj):
        logging.info('Adding optimal container ' + str(map_obj))
        return1 = self.add_optimisation(map_obj.get('name'), map_obj.get('app_name'), map_obj.get('arch_build'),map_obj.get('app_build'), map_obj.get('version'))
        if return1:
            return1 = self.add_container(map_obj.get('name'), map_obj.get('container_file'), map_obj.get('image_hub'),
                           map_obj.get('image_type'), map_obj.get('src'))

        return return1


    def add_container(self, opt_dsl_code:str, container_file:str, image_hub:str='docker', image_type:str='docker', src: str=''):
        logging.info('Adding container to mapper ')
        stmt = "INSERT INTO `mapper`(`map_id`,`opt_dsl_code`,`container_file`,`image_type`,`image_hub`,`src`) VALUES" \
               "(NULL,'{opt_dsl_code}','{container_file}','{image_type}','{image_hub}','{src}')"
        logging.info(stmt.format( opt_dsl_code=opt_dsl_code, container_file=container_file,
                           image_type=image_type, image_hub=image_hub, src=src))
        self.driver.updateSQL(stmt.format( opt_dsl_code=opt_dsl_code, container_file=container_file,
                                          image_type=image_type, image_hub=image_hub, src=src))
        return True

    def add_optimisation(self, opt_dsl_code: str, app_name: str,  target: dict, optimisation: dict, version: str = ''):
        logging.info('Adding dsl code to Optimisation ')
        target_str = ""
        for key in target:
            target_str = target_str + str(key).lower() + ":" + str(target[key]).lower() + ","
        opt_str = ""
        for key in optimisation:
            opt_str = opt_str + str(key).lower() + ":" + str(optimisation[key]).lower() + ","

        logging.info('Target string: ' + target_str)
        logging.info('Opt string: ' + opt_str)
        stmt = "INSERT INTO `optimisation`(`opt_dsl_code`,`app_name`,`target`,`optimisation`,`version`) VALUES " \
               "('{opt_dsl_code}','{app_name}','{target}','{optimisation}','{version}')"

        logging.info((stmt.format(opt_dsl_code=opt_dsl_code, app_name=app_name,
                          target=target_str, optimisation=opt_str, version=version)))
        self.driver.updateSQL(stmt.format(opt_dsl_code=opt_dsl_code, app_name=app_name,
                                         target=target_str, optimisation=opt_str, version=version))
        return True

    def get_container(self, opt_dsl_code:str):
        logging.info('Get container for opt code: ' +  str(opt_dsl_code))
        stmt = "select container_file, image_type, image_hub from mapper \
                where opt_dsl_code='{}' order by map_id desc limit 1"
        df = self.driver.applySQL(stmt.format(opt_dsl_code))
        if df.size > 0:
            container_file = df['container_file'][0]
            image_hub = df['image_hub'][0]
            logging.info('Container link: ' + str(image_hub) + str('://')+str(container_file))
            return str(image_hub) + str('://')+str(container_file)
        else:
            logging.warning('No optimal container found')
            return None

    def get_json_nodes(self,target_str: str):
        print(target_str)
        if str == '' or str is None or str == 'null':
            return ['']
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

    def decode_opt(self, opt_dsl: opt_dsl_reader):
        logging.info('Decoding optimisation')
        app_type = opt_dsl.get_app_type()
        if opt_dsl.enable_opt_build():
            target = opt_dsl.get_opt_build()
        else:
            target = u'{"cpu_type":"none","acc_type":"none"}'
            target = u'{}'

        config = opt_dsl.get_app_config()
        opts = opt_dsl.get_opt_list()
        app_build = opt_dsl.get_app_build()
        logging.info('optimisations: ' + str(opts))
        app_name = opt_dsl.get_app_name()

        sqlstr = "select opt_dsl_code from optimisation where app_name = '{}'".format(app_name)
        if target is not None:
            target_nodes = self.get_json_nodes(json.dumps(target))
            for t in target_nodes:
                targetstr = " and target like '%{}%'".format(t)
                sqlstr = sqlstr + targetstr
                logging.info('Adding target query ' + targetstr)

        if opt_dsl.enable_opt_build():
            sqlstr = sqlstr + " and target like '%enable_opt_build:true%'"
        else:
            sqlstr = sqlstr + " and target like '%enable_opt_build:false%'"

        if app_build is not None:
            build_nodes = self.get_json_nodes(json.dumps(app_build))
            for build in build_nodes:
                optstr = " and optimisation like '%{}%'".format(build)
                sqlstr = sqlstr + optstr
                logging.info('Adding build query ' + optstr)

        if opts is not None:
            opt_nodes = self.get_json_nodes(json.dumps(opts))
            print(opt_nodes)
            for t in opt_nodes:
                optstr = " and optimisation like '%{}%'".format(t)
                sqlstr = sqlstr + optstr
                logging.info('Adding opt query ' + optstr)
                self.opts.append(t)

        df = self.driver.selectSQL(sqlstr)
        if df.size > 0:
            dsl_code = df['opt_dsl_code'][0]
        else:
            dsl_code = None
        logging.info('Decoded dsl code :  {}'.format(dsl_code))
        return dsl_code

    def decode_hpc_opt(self, opt_dsl: opt_dsl_reader):
        return 1

    def decode_ai_training_opt(self,opt_dsl:opt_dsl_reader):
        logging.info('Decoding AI training optimisation')
        return 1

    def get_opts(self):
        return self.opts

def main():
    driver = MODAK_driver()
    m = mapper(driver)
    print('Test mapper main')

    # target_string = u'{"enable_opt_build":"false","cpu_type":"x86","acc_type":"nvidia"}'
    # opt_string = u'{"version":"3.1.3","mpicc":"true","mpic++":"true","mpifort":"true"}'
    # m.add_optimisation('ethcscs_openmpi_3.1.3', 'hpc_mpi', json.loads(target_string), json.loads(opt_string))

    # m.add_container('ethcscs_openmpi_3.1.3', 'ethcscs/openmpi:3.1.3')

    dsl_file = "../test/input/map_container.json"
    with open(dsl_file) as json_file:
         map_data = json.load(json_file)
         m.add_optcontainer(map_data)

    # with open('../test/input/mpi_solver.json') as json_file:
    #     job_data = json.load(json_file)
    #     print(job_data)
    #     reader = opt_dsl_reader(job_data['job'])
    #     dsl_code = m.decode_hpc_opt(reader)
    #     print(dsl_code)

if __name__ == '__main__':
    main()