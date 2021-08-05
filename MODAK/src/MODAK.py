#!/usr/bin/python3
import sys, getopt
from MODAK_driver import MODAK_driver
from settings import settings
from jobfile_generator import jobfile_generator
from mapper import mapper
from MODAK_gcloud import TransferData
from datetime import datetime
from enforcer import enforcer
from opt_dsl_reader import opt_dsl_reader
import logging
import json

class MODAK():
    def __init__(self, conf_file:str = '../conf/iac-model.ini', upload=False):
        """General MODAK class."""
        logging.info('Intialising MODAK')
        self.__driver = MODAK_driver(conf_file)
        self.__map = mapper(self.__driver)
        self.__enf = enforcer(self.__driver)
        self.__job_link = ''
        self.__upload = upload
        if self.__upload:
            self.__drop = TransferData()
        logging.info('Successfully intialised MODAK')

    def optimise(self, job_json_data):
        logging.info('Processing job data' + str(job_json_data))
        logging.info('Mapping to optimal container')
        new_container = self.__map.map_container(job_json_data)
        logging.info('Optimal container: {}'.format(new_container))

        if new_container is not None:
            application = job_json_data.get('job').get('application')
            application['container_runtime'] = new_container
            logging.info('Successfully updated container runtime')

        job_name = job_json_data.get('job').get('job_options').get('job_name')
        if job_name is None:
            job_name = job_json_data.get('job').get('application').get('app_tag', "job")
        # job_json_data.get('job').get('application').get('container_runtime')

        logging.info('Generating job file header')
        job_file = "{}/{}_{}.sh".format(settings.OUT_DIR,job_name,datetime.now().strftime('%Y%m%d%H%M%S'))
        gen_t = jobfile_generator(job_json_data, job_file, "torque")

        logging.info('Adding autotuning scripts')
        gen_t.add_tuner(upload=self.__upload)

        logging.info('Applying optimisations ' + str(self.__map.get_opts()))
        opts = self.__enf.enforce_opt(self.__map.get_opts())
        if opts:
            for i in range(0, opts.shape[0]):
                gen_t.add_optscript(opts['script_name'][i], opts['script_loc'][i])

        logging.info('Adding application run')
        gen_t.add_apprun()

        if self.__upload:
            file_to = "{}/{}_{}.sh".format('/modak',job_name,datetime.now().strftime('%Y%m%d%H%M%S'))
            self.__job_link = self.__drop.upload_file(file_from=job_file, file_to=file_to)
        else:
            self.__job_link = job_file
        logging.info('Job script link: ' + self.__job_link)
        return self.__job_link

    def job_header(self, job_json_data):
        logging.info('Generating job file header')
        logging.info('Processing job data' + str(job_json_data))
        job_name = job_json_data.get('job').get('job_options').get('job_name')
        if job_name is None:
            job_name = 'job'
        job_file = "{}/{}_{}.sh".format(settings.OUT_DIR, job_name, datetime.now().strftime('%Y%m%d%H%M%S'))
        gen_t = jobfile_generator(job_json_data, job_file, "torque")

        file_to = "{}/{}_{}.sh".format('/modak', job_name, datetime.now().strftime('%Y%m%d%H%M%S'))
        if self.__upload:
            self.__job_link = self.__drop.upload_file(file_from=job_file, file_to=file_to)
        logging.info('Job script link: ' + self.__job_link)
        return self.__job_link

    def opt_container_runtime(self, job_json_data):
        logging.info('Mapping optimal container for job data' )
        logging.info('Processing job data' + str(job_json_data))
        new_container = self.__map.map_container(job_json_data)
        logging.info('Optimal container: {}'.format(new_container))

        if new_container is not None:
            application = job_json_data.get('job').get('application')
            application['container_runtime'] = new_container
        return new_container

    def get_opt_container_runtime(self, job_json_data):
        logging.info('Mapping optimal container for job data')
        logging.info('Processing job data' + str(job_json_data))
        opt_reader = opt_dsl_reader(job_json_data["job"])
        new_container = ""
        if opt_reader.optimisations_exist():
            new_container = self.__map.map_container(job_json_data)
        logging.info('Optimal container: {}'.format(new_container))
        return new_container if new_container else ""

    def get_optimisation(self, job_json_data):
        if not job_json_data.get('job').get('application'):
            raise RuntimeError("Application must be defined")

        # if mapper finds an optimised container based on requested optimisation,
        # update the container runtime of application
        new_container = self.get_opt_container_runtime(job_json_data)
        if new_container:
            application = job_json_data.get('job').get('application')
            application['container_runtime'] = new_container
            logging.info('Successfully updated container runtime')

        job_name = job_json_data.get('job').get('job_options', {}).get('job_name', "job")
        if job_name is None:
            job_name = job_json_data.get('job').get('application', {}).get('app_tag', "job")

        logging.info('Generating job file header')
        job_file = "{}/{}_{}.sh".format(settings.OUT_DIR,job_name,datetime.now().strftime('%Y%m%d%H%M%S'))
        gen_t = jobfile_generator(job_json_data, job_file)

        logging.info('Adding job header')
        gen_t.add_job_header()

        opt_reader = opt_dsl_reader(job_json_data["job"])

        # TODO: support for autotuning
        if opt_reader.enable_autotuning():
            logging.info('Adding autotuning scripts')
            gen_t.add_tuner(self.__upload)

        logging.info('Applying optimisations ' + str(self.__map.get_decoded_opts(job_json_data)))
        opts = self.__enf.enforce_opt(self.__map.get_decoded_opts(job_json_data))
        for opt in opts:
            for i in range(0, opt.shape[0]):
                gen_t.add_optscript(opt['script_name'][i], opt['script_loc'][i])

        logging.info('Adding application run')
        gen_t.add_apprun()

        f = open(job_file, "r")
        job_script_content = f.read()

        logging.info('Job script content: ' + job_script_content)
        return ( new_container, job_script_content )

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('MODAK.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('MODAK.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print('Input file is "', inputfile)
    print('Output file is "', outputfile)

    m = MODAK('../conf/iac-model.ini')
    # dsl_file = "../test/input/tf_snow.json"
    # dsl_file = "../test/input/mpi_solver.json"
    with open(inputfile) as json_file:
        job_data = json.load(json_file)
        link = m.optimise(job_data)

    print(link)
    job_data['job'].update({'job_script': link})
    with open(outputfile, 'w') as fp:
        json.dump(job_data, fp)

if __name__ == '__main__':
    main(sys.argv[1:])
