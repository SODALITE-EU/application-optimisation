import json
import os
import urllib.request
import logging
import os

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

class JobfileGenerator():
    def __init__(self, job_json_obj, batch_file:str, scheduler:str = None):
        """Generates the job files, e.g. PBS and SLURM."""
        logging.info("Initialising job file generator")
        self.batch_file = batch_file
        self.job_json_obj = job_json_obj
        self.job_data = job_json_obj.get("job").get("job_options", {})
        self.app_data = job_json_obj.get("job").get("application", {})
        self.opt_data = job_json_obj.get("job").get("optimisation", {})
        self.singularity_exec = "singularity exec"
        self.current_dir = "./"
        self.ac = ArgumentConverter()
        # TODO: scheduler type should be derived based on the infrastructure target name
        # TODO: there shall be an entry in the database where scheduler type
        #       is specified in the infrastructure target
        self.scheduler = (
            scheduler
            if scheduler
            else self.job_json_obj.get("job", {})
            .get("target", {})
            .get("job_scheduler_type")
        )
        self.target_name = (
            self.job_json_obj.get("job", {}).get("target", {}).get("name")
        )
        if self.target_name == "egi":
            self.scheduler = SCHEDULER_SLURM
        elif self.target_name == "hlrs_testbed":
            self.scheduler = SCHEDULER_TORQUE    

    # Based on https://kb.northwestern.edu/page.php?id=89454

    def _generate_torque_header(self):
        logging.info("Generating torque header")
        filename = self.batch_file
        DIRECTIVE = "#PBS"
        with open(filename, "w") as fhandle:
            fhandle.write(f"{DIRECTIVE} -S /bin/bash\n")
            fhandle.write("## START OF HEADER ##\n")
            if "job_name" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -N {self.job_data['job_name']}\n")
            if "account" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -A {self.job_data['account']}\n")
            if "queue" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -q {self.job_data['queue']}\n")
            if "wall_time_limit" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} -l walltime={self.job_data['wall_time_limit']}\n"
                )
            if "node_count" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -l nodes={self.job_data['node_count']}")
                if "process_count_per_node" in self.job_data:
                    fhandle.write(f":ppn={self.job_data['process_count_per_node']}")
                if "request_gpus" in self.job_data:
                    fhandle.write(f":gpus={self.job_data['request_gpus']}")
                    self.singularity_exec = self.singularity_exec + " --nv "
                # secific to torque with default scheduler
                if "queue" in self.job_data:
                    fhandle.write(f":{self.job_data['queue']}")
                fhandle.write("\n")
            if "core_count" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -l procs={self.job_data['core_count']}")
            if "core_count_per_process" in self.job_data:
                pass
            if "memory_limit" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -l mem={self.job_data['memory_limit']}\n")
            if "minimum_memory_per_processor" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} -l pmem={self.job_data['minimum_memory_per_processor']}\n"
                )
            if "request_specific_nodes" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} -l nodes={self.job_data['request_specific_nodes']}\n"
                )
            if "job_array" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -t {self.job_data['job_array']}\n")
            if "standard_output_file" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} -o {self.job_data['standard_output_file']}\n"
                )
            if "standard_error_file" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} -e {self.job_data['standard_error_file']}\n"
                )
            if "combine_stdout_stderr" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -j oe\n")
            if "architecture_constraint" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} -l partition={self.job_data['architecture_constraint']}\n"
                )
            if "copy_environment" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -V\n")
            if "copy_environment_variable" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} -v {self.job_data['copy_environment_variable']}\n"
                )
            if "job_dependency" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -W {self.job_data['job_dependency']}\n")
            if "request_event_notification" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} -m {self.job_data['request_event_notification']}\n"
                )
            if "email_address" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -M {self.job_data['email_address']}\n")
            if "defer_job" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -a {self.job_data['defer_job']}\n")
            if "node_exclusive" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -l naccesspolicy=singlejob\n")

            fhandle.write("## END OF HEADER ##\n")
            fhandle.write("cd $PBS_O_WORKDIR\n")
            self.current_dir = "$PBS_O_WORKDIR/"
            fhandle.write("export PATH=$PBS_O_WORKDIR:$PATH\n")

    def _generate_slurm_header(self):
        logging.info("Generating slurm header")
        filename = self.batch_file
        DIRECTIVE = '#SBATCH'
        f = open(filename, 'w')
        f.write('#!/bin/bash')
        f.write('\n')
        f.write('## START OF HEADER ##')
        f.write('\n')
        if "job_name" in self.job_data:
            f.write(DIRECTIVE + ' -J ' + self.job_data['job_name'])
            f.write('\n')
        if "account" in self.job_data:
            f.write(DIRECTIVE + ' -A ' + self.job_data['account'])
            f.write('\n')
        if "queue" in self.job_data:
            f.write(DIRECTIVE + ' --partition=' + self.job_data['queue'])
            f.write('\n')
        if "wall_time_limit" in self.job_data:
            f.write(DIRECTIVE + ' --time=' + self.job_data['wall_time_limit'])
            f.write('\n')
        if "node_count" in self.job_data:
            f.write(DIRECTIVE + ' -N ' + str(self.job_data['node_count']))
            f.write('\n')
        if "core_count" in self.job_data:
            f.write(DIRECTIVE + ' -n ' + str(self.job_data['core_count']))
            f.write('\n')
        if "process_count_per_node" in self.job_data:
            f.write(DIRECTIVE + ' --ntasks-per-node=' + str(self.job_data['process_count_per_node']))
            f.write('\n')
        if "core_count_per_process" in self.job_data:
            f.write(DIRECTIVE + ' ----cpus-per-task=' + str(self.job_data['core_count_per_process']))
            f.write('\n')
        if "memory_limit" in self.job_data:
            f.write(DIRECTIVE + ' --mem=' + self.job_data['memory_limit'])
            f.write('\n')
        if "minimum_memory_per_processor" in self.job_data:
            f.write(DIRECTIVE + ' --mem-per-cpu=' + self.job_data['minimum_memory_per_processor'])
            f.write('\n')
        if "request_gpus" in self.job_data:
            f.write(DIRECTIVE + ' --gres=gpu:' + str(self.job_data['request_gpus']))
            f.write('\n')
            self.singularity_exec = self.singularity_exec + ' --nv '
        if "request_specific_nodes" in self.job_data:
            f.write(DIRECTIVE + ' --nodelist=' + self.job_data['request_specific_nodes'])
            f.write('\n')
        if "job_array" in self.job_data:
            f.write(DIRECTIVE + ' -a ' + self.job_data['job_array'])
            f.write('\n')
        if "standard_output_file" in self.job_data:
            f.write(DIRECTIVE + ' --output=' + self.job_data['standard_output_file'])
            f.write('\n')
        if "standard_error_file" in self.job_data:
            f.write(DIRECTIVE + ' --error=' + self.job_data['standard_error_file'])
            f.write('\n')
        if "combine_stdout_stderr" in self.job_data:
            pass
        if "architecture_constraint" in self.job_data:
            f.write(DIRECTIVE + ' -C ' + self.job_data['architecture_constraint'])
            f.write('\n')
        if "copy_environment" in self.job_data:
            f.write(DIRECTIVE + ' --export=ALL ')
            f.write('\n')
        if "copy_environment_variable" in self.job_data:
            f.write(DIRECTIVE + ' --export=' + self.job_data['copy_environment_variable'])
            f.write('\n')
        if "job_dependency" in self.job_data:
            f.write(DIRECTIVE + ' --dependency=' + self.job_data['job_dependency'])
            f.write('\n')
        if "request_event_notification" in self.job_data:
            f.write(DIRECTIVE + ' --mail-type=' + 
                self.ac.convert_notifications(SCHEDULER_SLURM, self.job_data['request_event_notification']))
            f.write('\n')
        if "email_address" in self.job_data:
            f.write(DIRECTIVE + ' --mail-user=' + self.job_data['email_address'])
            f.write('\n')
        if "defer_job" in self.job_data:
            f.write(DIRECTIVE + ' --begin=' + self.job_data['defer_job'])
            f.write('\n')
        if "node_exclusive" in self.job_data:
            f.write(DIRECTIVE + ' --exclusive')
            f.write('\n')

        with open(filename, "w") as fhandle:
            fhandle.write("#!/bin/bash\n")
            fhandle.write("## START OF HEADER ##\n")
            if "job_name" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -J {self.job_data['job_name']}\n")
            if "account" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -A {self.job_data['account']}\n")
            if "queue" in self.job_data:
                fhandle.write(f"{DIRECTIVE} --partition={self.job_data['queue']}\n")
            if "wall_time_limit" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} --time={self.job_data['wall_time_limit']}\n"
                )
            if "node_count" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -N {self.job_data['node_count']}\n")
            if "core_count" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -n {self.job_data['core_count']}\n")
            if "process_count_per_node" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} --ntasks-per-node={self.job_data['process_count_per_node']}\n"
                )
            if "core_count_per_process" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} --cpus-per-task={self.job_data['core_count_per_process']}\n"
                )
            if "memory_limit" in self.job_data:
                fhandle.write(f"{DIRECTIVE} --mem={self.job_data['memory_limit']}\n")
            if "minimum_memory_per_processor" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE}"
                    f" --mem-per-cpu={self.job_data['minimum_memory_per_processor']}\n"
                )
            if "request_gpus" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} --gres=gpu:{self.job_data['request_gpus']}\n"
                )
                self.singularity_exec = self.singularity_exec + " --nv "
            if "request_specific_nodes" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} --nodelist={self.job_data['request_specific_nodes']}\n"
                )
            if "job_array" in self.job_data:
                fhandle.write(f"{DIRECTIVE} -a {self.job_data['job_array']}\n")
            if "standard_output_file" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} --output={self.job_data['standard_output_file']}\n"
                )
            if "standard_error_file" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} -error={self.job_data['standard_error_file']}\n"
                )
            if "combine_stdout_stderr" in self.job_data:
                pass
            if "architecture_constraint" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} -C {self.job_data['architecture_constraint']}\n"
                )
            if "copy_environment" in self.job_data:
                fhandle.write(f"{DIRECTIVE} --export=ALL\n")
            if "copy_environment_variable" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} --export={self.job_data['copy_environment_variable']}\n"
                )
            if "job_dependency" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} --dependency={self.job_data['job_dependency']}\n"
                )
            if "request_event_notification" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} --mail-type={self.job_data['request_event_notification']}\n"
                )
            if "email_address" in self.job_data:
                fhandle.write(
                    f"{DIRECTIVE} --mail-user={self.job_data['email_address']}\n"
                )
            if "defer_job" in self.job_data:
                fhandle.write(f"{DIRECTIVE} --begin={self.job_data['defer_job']}\n")
            if "node_exclusive" in self.job_data:
                fhandle.write(f"{DIRECTIVE} --exclusive\n")

            fhandle.write("## END OF HEADER ##\n")
            fhandle.write("cd $SLURM_SUBMIT_DIR\n")
            self.current_dir = "$SLURM_SUBMIT_DIR/"
            fhandle.write("export PATH=$SLURM_SUBMIT_DIR:$PATH\n")

    def _generate_bash_header(self):
        logging.info("Generating bash header")
        filename = self.batch_file
        with open(filename, "w") as fhandle:
            fhandle.write("#!/bin/bash\n\n")

    def add_job_header(self):
        if self.job_data and self.scheduler == "torque":
            self._generate_torque_header()
        elif self.job_data and self.scheduler == "slurm":
            self._generate_slurm_header()
        else:
            self._generate_bash_header()

    def add_tuner(self, upload=True):
        tuner = Tuner(upload)
        res = tuner.encode_tune(self.job_json_obj, self.batch_file)
        if not res:
            logging.warning("Tuning not enabled or Encoding tuner failed")
            return None

        logging.info("Adding tuner" + str(tuner))
        with open(self.batch_file, "a") as f:
            f.seek(0, os.SEEK_END)
            f.write("\n")
            f.write("## START OF TUNER ##")
            f.write("\n")
            f.write("file=" + tuner.get_tune_filename())
            f.write("\n")
            f.write("if [ -f $file ] ; then rm $file; fi")
            f.write("\n")
            f.write("wget --no-check-certificate " + tuner.get_tune_link())
            f.write("\n")
            f.write("chmod 755 " + tuner.get_tune_filename())
            f.write("\n")
            if "container_runtime" in self.app_data:
                cont = self.app_data["container_runtime"]
                f.write(
                    "\n{} {} {}".format(
                        self.singularity_exec,
                        self.get_sif_filename(cont),
                        tuner.get_tune_filename(),
                    )
                )
                f.write("\n")
            else:
                f.write("source " + tuner.get_tune_filename())
                f.write("\n")
            f.write("## END OF TUNER ##")
            f.write("\n")
            f.close()
            logging.info("Successfully added tuner")

    def add_optscript(self, scriptfile, scriptlink):
        logging.info("Adding optimisations " + scriptfile)
        with open(self.batch_file, "a") as f:
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
wget --no-check-certificate {scriptlink}
chmod 755 {scriptfile}
source {scriptfile}
""", scriptfile=scriptfile, scriptlink=scriptlink))
        logging.info("Successfully added optimisation")

    def add_apprun(self):
        logging.info("Adding app run")
        with open(self.batch_file, "a") as f:
            f.seek(0, os.SEEK_END)
            exe = "{} {}".format(
                self.app_data.get("executable", ""), self.app_data.get("arguments", "")
            )
            cont = self.app_data.get("container_runtime", "")
            cont_exec_command = (
                f"{self.singularity_exec} {self.get_sif_filename(cont)} "
                if cont
                else ""
            )
            app_type = self.app_data.get("app_type")

            if app_type == "mpi" or app_type == "hpc":
                mpi_ranks = self.app_data.get("mpi_ranks", 1)
                threads = self.app_data.get("threads", 1)
                f.write("\nexport OMP_NUM_THREADS={}\n".format(threads))
                if self.scheduler == "torque" and "openmpi:1.10" in cont:
                    f.write("{} mpirun -np {} {}\n".format(cont_exec_command, mpi_ranks, exe))
                elif self.scheduler == "torque":
                    f.write("mpirun -np {} {} {}\n".format(mpi_ranks, cont_exec_command, exe))
                elif self.scheduler == "slurm":
                    f.write("mpirun -np {} {} {}\n".format(mpi_ranks, cont_exec_command, exe))
                else:
                    f.write(f"mpirun -np {mpi_ranks} {cont_exec_command} {exe}\n")
            else:  # other app types, e.g. python
                f.write(f"{cont_exec_command} {exe}\n")

            f.close()
            logging.info("Successfully added app run")

    def get_sif_filename(self, container: str):
        words = container.split("/")
        return "$SINGULARITY_DIR/" + words[-1].replace(":", "_") + ".sif"


def main():
    dsl_file = "../test/input/tf_snow.json"
    with open(dsl_file) as json_file:
        obj = json.load(json_file)
        gen_t = JobfileGenerator(obj, "../test/torque.pbs", SCHEDULER_TORQUE)
        gen_s = JobfileGenerator(obj, "../test/slurm.batch", SCHEDULER_SLURM)
        gen_t.add_apprun()
        gen_s.add_apprun()

    print(gen_t.get_sif_filename("shub://sodalite-hpe/modak:pytorch-1.5-cpu-pi"))


if __name__ == "__main__":
    main()
