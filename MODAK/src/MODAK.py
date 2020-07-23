from MODAK_driver import MODAK_driver
from settings import settings
from jobfile_generator import jobfile_generator
from mapper import mapper
from MODAK_dropbox import TransferData
from datetime import datetime
from enforcer import enforcer

import json

class MODAK():

    def __init__(self, conf_file:str = '../conf/prod-iac-model.ini'):
        self.__driver = MODAK_driver(conf_file)
        self.__map = mapper(self.__driver)
        self.__enf = enforcer(self.__driver)
        self.__drop = TransferData()
        self.__job_link = ''

    def optimise(self, job_json_data):
        print(job_json_data)
        new_container = self.__map.map_container(job_json_data)
        print(new_container)

        if new_container is not None:
            application = job_json_data.get('job').get('application')
            application['container_runtime'] = new_container

        job_name = job_json_data.get('job').get('job_options').get('job_name')
        if job_name is None:
            job_name = job_json_data.get('job').get('application')
        job_json_data.get('job').get('application').get('container_runtime')

        job_file = "{}/{}_{}.sh".format(settings.OUT_DIR,job_name,datetime.now().strftime('%Y%m%d%H%M%S'))
        gen_t = jobfile_generator(job_json_data, job_file, "torque")

        gen_t.add_tuner()

        print(self.__map.get_opts())
        opts = self.__enf.enforce_opt(self.__map.get_opts())
        if opts is not None:
            for i in range(0, opts.shape[0]):
                gen_t.add_optscript(opts['script_name'][i], opts['script_loc'][i])

        gen_t.add_apprun()

        file_to = "{}/{}_{}.sh".format('/modak',job_name,datetime.now().strftime('%Y%m%d%H%M%S'))
        self.__job_link = self.__drop.upload_file(file_from=job_file, file_to=file_to)
        print(self.__job_link)
        return self.__job_link

def main():
    print('Test MODAK')
    m = MODAK()
    dsl_file = "../test/input/tf_snow.json"
    # dsl_file = "../test/input/mpi_solver.json"
    with open(dsl_file) as json_file:
        m.optimise(json.load(json_file))

if __name__ == '__main__':
    main()
