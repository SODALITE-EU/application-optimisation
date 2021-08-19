#!/usr/bin/python3
import getopt
import json
import logging
import pathlib
import sys
import re
import jinja2
from datetime import datetime
from typing import NamedTuple

from enforcer import Enforcer
from jobfile_generator import JobfileGenerator
from mapper import Mapper
from MODAK_driver import MODAK_driver
from MODAK_gcloud import TransferData
from copy import deepcopy
from opt_dsl_reader import OptDSLReader
from settings import DEFAULT_SETTINGS_DIR, Settings

JobScripts = NamedTuple("JobScripts", [("jobscript", str), ("buildscript",str)])

class MODAK:
    def __init__(
        self,
        conf_file: pathlib.Path = DEFAULT_SETTINGS_DIR / "iac-model.ini",
        upload=False,
    ):
        """General MODAK class."""
        logging.info("Intialising MODAK")
        self._driver = MODAK_driver(conf_file)
        self._map = Mapper(self._driver)
        self._enf = Enforcer(self._driver)
        self._job_link = ""
        self._upload = upload
        if self._upload:
            self._drop = TransferData()
        logging.info("Successfully intialised MODAK")

    def optimise(self, job_json_data):
        logging.info("Processing job data" + str(job_json_data))
        logging.info("Mapping to optimal container")
        new_container = self._map.map_container(job_json_data)
        logging.info(f"Optimal container: {new_container}")

        if new_container is not None:
            application = job_json_data.get("job").get("application")
            application["container_runtime"] = new_container
            logging.info("Successfully updated container runtime")

        job_name = job_json_data.get("job").get("job_options").get("job_name")
        if job_name is None:
            job_name = job_json_data.get("job").get("application").get("app_tag", "job")
        # job_json_data.get('job').get('application').get('container_runtime')

        logging.info("Generating job file header")
        job_file = "{}/{}_{}.sh".format(
            Settings.OUT_DIR, job_name, datetime.now().strftime("%Y%m%d%H%M%S")
        )
        gen_t = JobfileGenerator(job_json_data, job_file, "torque")

        logging.info('Generating build file')
        buildjob = self.get_buildjob(job_json_data)
        build_file = "{}/{}_{}.sh".format(
            Settings.OUT_DIR, f"{job_name}_build", datetime.now().strftime("%Y%m%d%H%M%S")
        )
        with open(build_file, 'w') as f:
            f.write(buildjob)

        logging.info("Adding autotuning scripts")
        gen_t.add_tuner(upload=self._upload)

        logging.info("Applying optimisations " + str(self._map.get_opts()))
        opts = self._enf.enforce_opt(self._map.get_opts())
        if opts:
            for i in range(0, opts.shape[0]):
                gen_t.add_optscript(opts["script_name"][i], opts["script_loc"][i])

        logging.info("Adding application run")
        gen_t.add_apprun()

        if self._upload:
            file_to = f"/modak/{job_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.sh"
            build_file_to = f"/modak/build_{job_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.sh"
            self._job_link = self._drop.upload_file(file_from=job_file, file_to=file_to)
            self._build_link = self._drop.upload_file(file_from=build_file, file_to=build_file_to)
        else:
            self._job_link = job_file
            self._build_link = build_file
        logging.info("Job script link: " + self._job_link)
        logging.info("Build script link: " + self._build_link)
        return JobScripts(self._job_link, self._build_link)

    def job_header(self, job_json_data):
        logging.info("Generating job file header")
        logging.info("Processing job data" + str(job_json_data))
        job_name = job_json_data.get("job").get("job_options").get("job_name")
        if job_name is None:
            job_name = "job"
        job_file = "{}/{}_{}.sh".format(
            Settings.OUT_DIR, job_name, datetime.now().strftime("%Y%m%d%H%M%S")
        )
        JobfileGenerator(job_json_data, job_file, "torque")

        file_to = f"/modak/{job_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.sh"
        if self._upload:
            self._job_link = self._drop.upload_file(file_from=job_file, file_to=file_to)
        logging.info("Job script link: " + self._job_link)
        return self._job_link

    def opt_container_runtime(self, job_json_data):
        logging.info("Mapping optimal container for job data")
        logging.info("Processing job data" + str(job_json_data))
        new_container = self._map.map_container(job_json_data)
        logging.info(f"Optimal container: {new_container}")

        if new_container is not None:
            application = job_json_data.get("job").get("application")
            application["container_runtime"] = new_container
        return new_container

    def get_opt_container_runtime(self, job_json_data):
        logging.info("Mapping optimal container for job data")
        logging.info("Processing job data" + str(job_json_data))
        opt_reader = OptDSLReader(job_json_data["job"])
        new_container = ""
        if opt_reader.optimisations_exist():
            new_container = self._map.map_container(job_json_data)
        logging.info(f"Optimal container: {new_container}")
        return new_container if new_container else ""
    
    def get_buildjob(self, job_json_data):
        logging.info('Creating build script for job')
        logging.info(f"Processing build data: {job_json_data}")

        # patch in the build job as the job task
        # First, figure out what we're patching in:
        if "job" not in job_json_data:
            logging.info("No job section in request, returning empty resposne")
            return ""
        if "application" not in job_json_data["job"]:
            logging.info("No job.application.build section in request, returning empty resposne")
            return ""
        if "build" not in job_json_data["job"]["application"]:
            logging.info("No job.application.build section in request, returning empty resposne")
            return ""
        if "src" not in job_json_data["job"]["application"]["build"]:
            logging.info("No job.application.build section in request, returning empty resposne")
            return ""
        if "build_command" not in job_json_data["job"]["application"]["build"]:
            logging.info("No job.application.build section in request, returning empty resposne")
            return ""
        buildsrc = job_json_data["job"]["application"]["build"]["src"]
        buildcmd = job_json_data["job"]["application"]["build"]["build_command"]
        final_build = ""
        if buildsrc[-4:] == ".git":
            final_build = f"git clone {buildsrc}\n"
        else:
            final_build = f"wget --no-check-certificate {buildsrc}\n"
        
        process_per_node=1
        try:
            process_per_node = job_json_data["job"]["application"]["build"]["build_parallelism"]
        except KeyError:
            pass
        t = jinja2.Template(buildcmd)
        final_build += t.render(BUILD_PARALLELISM=process_per_node)
        stdoutfile = job_json_data["job"]["job_options"]["standard_output_file"]
        stderrfile = job_json_data["job"]["job_options"]["standard_error_file"]

        mod_jobdata = deepcopy(job_json_data)
        mod_jobdata["job"]["job_options"]["job_name"] = job_json_data["job"]["job_options"]["job_name"] + "_build"
        mod_jobdata["job"]["job_options"]["node_count"] = 1
        mod_jobdata["job"]["job_options"]["process_count_per_node"] = process_per_node
        mod_jobdata["job"]["job_options"]["standard_output_file"] = f"build-{stdoutfile}"
        mod_jobdata["job"]["job_options"]["standard_error_file"] = f"build-{stderrfile}"
        mod_jobdata["job"]["application"]["executable"] = final_build
        
        return self.get_optimisation(mod_jobdata)[1]

    def get_optimisation(self, job_json_data):
        if not job_json_data.get("job").get("application"):
            raise RuntimeError("Application must be defined")

        # if mapper finds an optimised container based on requested optimisation,
        # update the container runtime of application
        new_container = self.get_opt_container_runtime(job_json_data)
        if new_container:
            application = job_json_data.get("job").get("application")
            application["container_runtime"] = new_container
            logging.info("Successfully updated container runtime")

        job_name = (
            job_json_data.get("job").get("job_options", {}).get("job_name", "job")
        )
        if job_name is None:
            job_name = (
                job_json_data.get("job").get("application", {}).get("app_tag", "job")
            )

        logging.info("Generating job file header")
        job_file = "{}/{}_{}.sh".format(
            Settings.OUT_DIR, job_name, datetime.now().strftime("%Y%m%d%H%M%S")
        )
        gen_t = JobfileGenerator(job_json_data, job_file)

        logging.info("Adding job header")
        gen_t.add_job_header()

        opt_reader = OptDSLReader(job_json_data["job"])

        # TODO: support for autotuning
        if opt_reader.enable_autotuning():
            logging.info("Adding autotuning scripts")
            gen_t.add_tuner(self._upload)

        logging.info(
            "Applying optimisations " + str(self._map.get_decoded_opts(job_json_data))
        )
        opts = self._enf.enforce_opt(self._map.get_decoded_opts(job_json_data))
        for opt in opts:
            for i in range(0, opt.shape[0]):
                gen_t.add_optscript(opt["script_name"][i], opt["script_loc"][i])

        logging.info("Adding application run")
        gen_t.add_apprun()

        f = open(job_file, "r")
        job_script_content = f.read()

        logging.info("Job script content: " + job_script_content)
        return (new_container, job_script_content)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("MODAK.py -i <inputfile> -o <outputfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("MODAK.py -i <inputfile> -o <outputfile>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print('Input file is "', inputfile)
    print('Output file is "', outputfile)

    m = MODAK("../conf/iac-model.ini")
    # dsl_file = "../test/input/tf_snow.json"
    # dsl_file = "../test/input/mpi_solver.json"
    with open(inputfile) as json_file:
        job_data = json.load(json_file)
        link = m.optimise(job_data)

    print(link)
    job_data["job"].update({"job_script": link[0], "build_script": link[1]})
    with open(outputfile, "w") as fp:
        json.dump(job_data, fp)


if __name__ == "__main__":
    main(sys.argv[1:])
