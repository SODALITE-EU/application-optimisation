import json
import os
import urllib.request
import logging
import pathlib
from typing import Optional

from tuner import Tuner


"""Constant to represent the scheduler to use is SLURM"""
SCHEDULER_SLURM="slurm"
"""Constant to represent the scheduler to use is PBS Torque"""
SCHEDULER_TORQUE="torque"

class ArgumentConverter():
        # Define which options are vaild of each of the schedulers
    VAILD_TORQUE=['a','b','e', 'f'] # abort, begin, end
    VALID_SLURM=["BEGIN", "END", "FAIL", "REQUEUE", "ALL",
        "INVALID_DEPEND", "STAGE_OUT", "TIME_LIMIT", "TIME_LIMIT_90", 
        "TIME_LIMIT_80", "TIME_LIMIT_50", "ARRAY_TASKS"]
    SLURM_TO_TORQUE={
        "NONE": "n",
        "BEGIN": "b", 
        "END": "e", 
        "FAIL": "f",
        "REQUEUE": "",
        "ALL": "abef",
        "INVALID_DEPEND": "a",
        "STAGE_OUT": "",
        "TIME_LIMIT": "a",
        "TIME_LIMIT_90": "", 
        "TIME_LIMIT_80": "",
        "TIME_LIMIT_50": "",
        "ARRAY_TASKS": ""
    }
    TORQUE_TO_SLURM={
        "a": "FAIL,INVALID_DEPEND,TIME_LIMIT",
        "b": "BEGIN",
        "e": "END",
        "f": "FAIL",
        "n": "FAIL",
        "p": "NONE"
    }

    def _slurm_to_torque(self, options):
        # For each option in the slurm options, look it up in the 
        # SLURM_TO_TORQUE dict. Then concatenate all the returned values
        res = "".join([self.SLURM_TO_TORQUE[opt] for opt in options.split(",")])
        if res == "":
            return "abef"
        return res

    def _torque_to_slurm(self, options):
        # For each character in the torque options, look it up in the
        # TORQUE_TO_SLURM dict. Then concatenate all the returned vaules,
        # separating them with commas 
        return ",".join([self.TORQUE_TO_SLURM[opt] for opt in options])

    def _is_slurm_options(self, options):
        # Split the options string on commas, then check each part is a valid
        # option. Return true if all are; false otherwise.
        if options=="":
            return False # cannot be empty
        if options=="NONE":
            return True #None must stand alone
        return all(opt in self.VALID_SLURM for opt in options.split(","))
    
    def _is_torque_options(self, options):
        # For each character in the options, check if it is a valid torque
        # option. If all are, return true, otherwise, false
        if options=="":
            return False # cannot be empty
        if options == "n" or options=="p":
            return True # n and p must be alone
        return all(opt in self.VAILD_TORQUE for opt in options)

    def convert_notifications(self, scheduler, notifications):    
        # Check if the options we have match the scheduler we have
        if scheduler==SCHEDULER_SLURM and self._is_torque_options(notifications):
            # Scheduler is slurm, but notifications are torque.
            # convert then return
            return self._torque_to_slurm(notifications)
        elif scheduler==SCHEDULER_TORQUE and self._is_slurm_options(notifications):
            # Scheduler is torque, notifications are slurm.
            # convert, then return
            return self._slurm_to_torque(notifications)
        elif scheduler==SCHEDULER_SLURM and not self._is_slurm_options(notifications):
            # Options passed are invalid; use a default
            return "ALL"
        elif scheduler==SCHEDULER_TORQUE and not self._is_torque_options(notifications):
            return "abe"
        # Scheduler and options match; return the original notification options
        # (Also, if notifications are invalid this leaves them intact/unmodified)
        return notifications

class JobfileGenerator:
    def __init__(
            self, job_json_obj, batch_file:str, scheduler:str = None
    ):
        """Generates the job files, e.g. PBS and SLURM."""
        logging.info("Initialising job file generator")
        self._batch_file = batch_file
        self._job_json_obj = job_json_obj
        self._job_data = job_json_obj.get("job").get("job_options", {})
        self._app_data = job_json_obj.get("job").get("application", {})
        self._opt_data = job_json_obj.get("job").get("optimisation", {})
        self._singularity_exec = "singularity exec"
        self._current_dir = "./"
        self.ac = ArgumentConverter()
        # TODO: scheduler type should be derived based on the infrastructure target name
        # TODO: there shall be an entry in the database where scheduler type
        #       is specified in the infrastructure target

        self._target_name = (
            self._job_json_obj.get("job", {}).get("target", {}).get("name")
        )

        # use an explicitly given scheduler, if provided, otherwise determine from DSL
        if scheduler is not None:
            self._scheduler = scheduler
        else:
            self._scheduler = (
                self._job_json_obj.get("job", {})
                .get("target", {})
                .get("job_scheduler_type")
            )

        # override for certain (test) target names for now:
        if self._target_name == "egi":
            self._scheduler = SCHEDULER_SLURM
        elif self._target_name == "hlrs_testbed":
            self._scheduler = SCHEDULER_TORQUE

    # Based on https://kb.northwestern.edu/page.php?id=89454

    def _generate_torque_header(self):
        logging.info("Generating torque header")
        DIRECTIVE = "#PBS"
        with self._batch_file.open("w") as fhandle:
            fhandle.write(f"{DIRECTIVE} -S /bin/bash\n")
            fhandle.write("## START OF HEADER ##\n")
            if "job_name" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -N {self._job_data['job_name']}\n")
            if "account" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -A {self._job_data['account']}\n")
            if "queue" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -q {self._job_data['queue']}\n")
            if "wall_time_limit" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} -l walltime={self._job_data['wall_time_limit']}\n"
                )
            if "node_count" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -l nodes={self._job_data['node_count']}")
                if "process_count_per_node" in self._job_data:
                    fhandle.write(f":ppn={self._job_data['process_count_per_node']}")
                if "request_gpus" in self._job_data:
                    fhandle.write(f":gpus={self._job_data['request_gpus']}")
                    self._singularity_exec = self._singularity_exec + " --nv "
                # specific to torque with default scheduler
                if "queue" in self._job_data:
                    fhandle.write(f":{self._job_data['queue']}")
                fhandle.write("\n")
            if "core_count" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -l procs={self._job_data['core_count']}\n")
            if "core_count_per_process" in self._job_data:
                pass
            if "memory_limit" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -l mem={self._job_data['memory_limit']}\n")
            if "minimum_memory_per_processor" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} -l pmem={self._job_data['minimum_memory_per_processor']}\n"
                )
            if "request_specific_nodes" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} -l nodes={self._job_data['request_specific_nodes']}\n"
                )
            if "job_array" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -t {self._job_data['job_array']}\n")
            if "standard_output_file" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} -o {self._job_data['standard_output_file']}\n"
                )
            if "standard_error_file" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} -e {self._job_data['standard_error_file']}\n"
                )
            if "combine_stdout_stderr" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -j oe\n")
            if "architecture_constraint" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} -l partition={self._job_data['architecture_constraint']}\n"
                )
            if "copy_environment" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -V\n")
            if "copy_environment_variable" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} -v {self._job_data['copy_environment_variable']}\n"
                )
            if "job_dependency" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -W {self._job_data['job_dependency']}\n")
            if "request_event_notification" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} -m {self._job_data['request_event_notification']}\n"
                )
            if "email_address" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -M {self._job_data['email_address']}\n")
            if "defer_job" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -a {self._job_data['defer_job']}\n")
            if "node_exclusive" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -l naccesspolicy=singlejob\n")

            fhandle.write("## END OF HEADER ##\n")
            fhandle.write("cd $PBS_O_WORKDIR\n")
            self._current_dir = "$PBS_O_WORKDIR/"
            fhandle.write("export PATH=$PBS_O_WORKDIR:$PATH\n")

    def _generate_slurm_header(self):
        logging.info("Generating slurm header")
        filename = self._batch_file
        DIRECTIVE = '#SBATCH'
        with open(filename, 'w') as f:
            f.write('#!/bin/bash')
            f.write('\n')
            f.write('## START OF HEADER ##')
            f.write('\n')
            if "job_name" in self._job_data:
                f.write(DIRECTIVE + ' -J ' + self._job_data['job_name'])
                f.write('\n')
            if "account" in self._job_data:
                f.write(DIRECTIVE + ' -A ' + self._job_data['account'])
                f.write('\n')
            if "queue" in self._job_data:
                f.write(DIRECTIVE + ' --partition=' + self._job_data['queue'])
                f.write('\n')
            if "wall_time_limit" in self._job_data:
                f.write(DIRECTIVE + ' --time=' + self._job_data['wall_time_limit'])
                f.write('\n')
            if "node_count" in self._job_data:
                f.write(DIRECTIVE + ' -N ' + str(self._job_data['node_count']))
                f.write('\n')
            if "core_count" in self._job_data:
                f.write(DIRECTIVE + ' -n ' + str(self._job_data['core_count']))
                f.write('\n')
            if "process_count_per_node" in self._job_data:
                f.write(DIRECTIVE + ' --ntasks-per-node=' + str(self._job_data['process_count_per_node']))
                f.write('\n')
            if "core_count_per_process" in self._job_data:
                f.write(DIRECTIVE + ' ----cpus-per-task=' + str(self._job_data['core_count_per_process']))
                f.write('\n')
            if "memory_limit" in self._job_data:
                f.write(DIRECTIVE + ' --mem=' + self._job_data['memory_limit'])
                f.write('\n')
            if "minimum_memory_per_processor" in self._job_data:
                f.write(DIRECTIVE + ' --mem-per-cpu=' + self._job_data['minimum_memory_per_processor'])
                f.write('\n')
            if "request_gpus" in self._job_data:
                f.write(DIRECTIVE + ' --gres=gpu:' + str(self._job_data['request_gpus']))
                f.write('\n')
                self._singularity_exec = self._singularity_exec + ' --nv '
            if "request_specific_nodes" in self._job_data:
                f.write(DIRECTIVE + ' --nodelist=' + self._job_data['request_specific_nodes'])
                f.write('\n')
            if "job_array" in self._job_data:
                f.write(DIRECTIVE + ' -a ' + self._job_data['job_array'])
                f.write('\n')
            if "standard_output_file" in self._job_data:
                f.write(DIRECTIVE + ' --output=' + self._job_data['standard_output_file'])
                f.write('\n')
            if "standard_error_file" in self._job_data:
                f.write(DIRECTIVE + ' --error=' + self._job_data['standard_error_file'])
                f.write('\n')
            if "combine_stdout_stderr" in self._job_data:
                pass
            if "architecture_constraint" in self._job_data:
                f.write(DIRECTIVE + ' -C ' + self._job_data['architecture_constraint'])
                f.write('\n')
            if "copy_environment" in self._job_data:
                f.write(DIRECTIVE + ' --export=ALL ')
                f.write('\n')
            if "copy_environment_variable" in self._job_data:
                f.write(DIRECTIVE + ' --export=' + self._job_data['copy_environment_variable'])
                f.write('\n')
            if "job_dependency" in self._job_data:
                f.write(DIRECTIVE + ' --dependency=' + self._job_data['job_dependency'])
                f.write('\n')
            if "request_event_notification" in self._job_data:
                f.write(DIRECTIVE + ' --mail-type=' + 
                    self.ac.convert_notifications(SCHEDULER_SLURM, self._job_data['request_event_notification']))
                f.write('\n')
            if "email_address" in self._job_data:
                f.write(DIRECTIVE + ' --mail-user=' + self._job_data['email_address'])
                f.write('\n')
            if "defer_job" in self._job_data:
                f.write(DIRECTIVE + ' --begin=' + self._job_data['defer_job'])
                f.write('\n')
            if "node_exclusive" in self._job_data:
                f.write(DIRECTIVE + ' --exclusive')
                f.write('\n')

        with self._batch_file.open("w") as fhandle:
            fhandle.write("#!/bin/bash\n")
            fhandle.write("## START OF HEADER ##\n")
            if "job_name" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -J {self._job_data['job_name']}\n")
            if "account" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -A {self._job_data['account']}\n")
            if "queue" in self._job_data:
                fhandle.write(f"{DIRECTIVE} --partition={self._job_data['queue']}\n")
            if "wall_time_limit" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} --time={self._job_data['wall_time_limit']}\n"
                )
            if "node_count" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -N {self._job_data['node_count']}\n")
            if "core_count" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -n {self._job_data['core_count']}\n")
            if "process_count_per_node" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE}"
                    f" --ntasks-per-node={self._job_data['process_count_per_node']}\n"
                )
            if "core_count_per_process" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} --cpus-per-task={self._job_data['core_count_per_process']}\n"
                )
            if "memory_limit" in self._job_data:
                fhandle.write(f"{DIRECTIVE} --mem={self._job_data['memory_limit']}\n")
            if "minimum_memory_per_processor" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE}"
                    f" --mem-per-cpu={self._job_data['minimum_memory_per_processor']}\n"
                )
            if "request_gpus" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} --gres=gpu:{self._job_data['request_gpus']}\n"
                )
                self._singularity_exec = self._singularity_exec + " --nv "
            if "request_specific_nodes" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} --nodelist={self._job_data['request_specific_nodes']}\n"
                )
            if "job_array" in self._job_data:
                fhandle.write(f"{DIRECTIVE} -a {self._job_data['job_array']}\n")
            if "standard_output_file" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} --output={self._job_data['standard_output_file']}\n"
                )
            if "standard_error_file" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} -error={self._job_data['standard_error_file']}\n"
                )
            if "combine_stdout_stderr" in self._job_data:
                pass
            if "architecture_constraint" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} -C {self._job_data['architecture_constraint']}\n"
                )
            if "copy_environment" in self._job_data:
                fhandle.write(f"{DIRECTIVE} --export=ALL\n")
            if "copy_environment_variable" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} --export={self._job_data['copy_environment_variable']}\n"
                )
            if "job_dependency" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} --dependency={self._job_data['job_dependency']}\n"
                )
            if "request_event_notification" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} --mail-type={self._job_data['request_event_notification']}\n"
                )
            if "email_address" in self._job_data:
                fhandle.write(
                    f"{DIRECTIVE} --mail-user={self._job_data['email_address']}\n"
                )
            if "defer_job" in self._job_data:
                fhandle.write(f"{DIRECTIVE} --begin={self._job_data['defer_job']}\n")
            if "node_exclusive" in self._job_data:
                fhandle.write(f"{DIRECTIVE} --exclusive\n")

            fhandle.write("## END OF HEADER ##\n")
            fhandle.write("cd $SLURM_SUBMIT_DIR\n")
            self._current_dir = "$SLURM_SUBMIT_DIR/"
            fhandle.write("export PATH=$SLURM_SUBMIT_DIR:$PATH\n")

    def _generate_bash_header(self):
        logging.info("Generating bash header")
        with self._batch_file.open("w") as fhandle:
            fhandle.write("#!/bin/bash\n\n")

    def add_job_header(self):
        if self._job_data and self._scheduler == "torque":
            self._generate_torque_header()
        elif self._job_data and self._scheduler == "slurm":
            self._generate_slurm_header()
        else:
            self._generate_bash_header()

    def add_tuner(self, upload=True):
        tuner = Tuner(upload)
        res = tuner.encode_tune(self._job_json_obj, self._batch_file)
        if not res:
            logging.warning("Tuning not enabled or Encoding tuner failed")
            return None

        logging.info("Adding tuner" + str(tuner))
        with self._batch_file.open("a") as fhandle:
            fhandle.write("\n")
            fhandle.write("## START OF TUNER ##\n")
            fhandle.write(f"file={tuner.get_tune_filename()}\n")
            fhandle.write('[ -f $file ] && rm "$file"\n')
            fhandle.write(f"wget --no-check-certificate '{tuner.get_tune_link()}'\n")
            fhandle.write(f"chmod 755 '{tuner.get_tune_filename()}'\n")
            if "container_runtime" in self._app_data:
                cont = self._app_data["container_runtime"]
                fhandle.write(
                    f"\n{self._singularity_exec} "
                    f'"{self.get_sif_filename(cont)}" "{tuner.get_tune_filename()}"'
                )
                fhandle.write("\n")
            else:
                fhandle.write(f"source '{tuner.get_tune_filename()}'\n")
            fhandle.write("## END OF TUNER ##\n")
            logging.info("Successfully added tuner")

    def add_optscript(self, scriptfile, scriptlink):
        logging.info("Adding optimisations " + scriptfile)
        with open(self._batch_file, "a") as f:
            f.seek(0, os.SEEK_END)
            scriptcontents = None
            try:
                scriptcontents = urllib.request.urlopen(scriptlink)
            except Exception as e:
                logging.info("Couldn't inline optscript: %s" % e)
            if scriptcontents is not None:
                f.write(scriptcontents.read().decode("UTF-8"))
            else:
                f.write(str.format("""
file={scriptfile}
if [ -f $file ] ; then rm $file; fi
wget --no-check-certificate '{scriptlink}'
chmod 755 {scriptfile}
source {scriptfile}
""", scriptfile=scriptfile, scriptlink=scriptlink))
        logging.info("Successfully added optimisation")

    def add_apprun(self):
        logging.info("Adding app run")
        with self._batch_file.open("a") as fhandle:
            exe = (
                f"{self._app_data.get('executable', '')}"
                f" {self._app_data.get('arguments', '')}"
            )

            cont_exec_command = ""
            cont = self._app_data.get("container_runtime", "")
            if cont:
                cont_exec_command = (
                    f'{self._singularity_exec} "{self.get_sif_filename(cont)}"'
                )

            app_type = self._app_data.get("app_type")

            if "build" in self._app_data:
                src = self._app_data["build"].get("src")
                build_command = self._app_data["build"].get("build_command")
                if src[-4:] == ".git":
                    fhandle.write(f"\ngit clone {src}\n")
                else:
                    fhandle.write(f"\nwget --no-check-certificate {src}\n")
                fhandle.write(f"\n{cont_exec_command} {build_command}\n")

            if app_type == "mpi" or app_type == "hpc":
                mpi_ranks = self._app_data.get("mpi_ranks", 1)
                threads = self._app_data.get("threads", 1)
                fhandle.write(f"\nexport OMP_NUM_THREADS={threads}\n")
                if self._scheduler == "torque" and "openmpi:1.10" in cont:
                    fhandle.write(f"{cont_exec_command} mpirun -np {mpi_ranks} {exe}\n")
                elif self._scheduler == "torque":
                    fhandle.write(f"mpirun -np {mpi_ranks} {cont_exec_command} {exe}\n")
                elif self._scheduler == "slurm":
                    fhandle.write(f"srun -n {mpi_ranks} {cont_exec_command} {exe}\n")
                else:
                    fhandle.write(f"mpirun -np {mpi_ranks} {cont_exec_command} {exe}\n")
            else:  # other app types, e.g. python
                fhandle.write(f"{cont_exec_command} {exe}\n")

            logging.info("Successfully added app run")

    def get_sif_filename(self, container: str):
        words = container.split("/")
        return f"$SINGULARITY_DIR/{words[-1].replace(':', '_')}.sif"


def main():
    dsl_file = pathlib.Path("../test/input/tf_snow.json")
    with dsl_file.open() as json_file:
        obj = json.load(json_file)

    gen_t = JobfileGenerator(obj, pathlib.Path("../test/torque.pbs"), SCHEDULER_TORQUE)
    gen_t.add_job_header()
    gen_t.add_apprun()

    gen_s = JobfileGenerator(obj, pathlib.Path("../test/slurm.batch"), SCHEDULER_SLURM)
    gen_s.add_job_header()
    gen_s.add_apprun()

    print(gen_t.get_sif_filename("shub://sodalite-hpe/modak:pytorch-1.5-cpu-pi"))


if __name__ == "__main__":
    main()
