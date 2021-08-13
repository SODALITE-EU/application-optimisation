import json
import logging
import pathlib
from typing import Optional

from tuner import Tuner


class JobfileGenerator:
    def __init__(
        self, job_json_obj, batch_file: pathlib.Path, scheduler: Optional[str] = None
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
            self._scheduler = "torque"
        elif self._target_name == "hlrs_testbed":
            self._scheduler = "torque"

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
        DIRECTIVE = "#SBATCH"

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
        with self._batch_file.open("a") as fhandle:
            fhandle.write("\n")
            fhandle.write(f"file={scriptfile}\n")
            fhandle.write('[ -f ${file} ] && rm "$file"\n')
            fhandle.write(f"wget --no-check-certificate '{scriptlink}'\n")
            fhandle.write(f"chmod 755 '{scriptfile}'\n")
            fhandle.write(f"source '{scriptfile}'\n")
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

    gen_t = JobfileGenerator(obj, pathlib.Path("../test/torque.pbs"), "torque")
    gen_t.add_job_header()
    gen_t.add_apprun()

    gen_s = JobfileGenerator(obj, pathlib.Path("../test/slurm.batch"), "slurm")
    gen_s.add_job_header()
    gen_s.add_apprun()

    print(gen_t.get_sif_filename("shub://sodalite-hpe/modak:pytorch-1.5-cpu-pi"))


if __name__ == "__main__":
    main()
