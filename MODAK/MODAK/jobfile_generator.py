import json
import logging
import pathlib
import urllib.request
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader

from .tuner import Tuner

"""Constant to represent the scheduler to use is SLURM"""
SCHEDULER_SLURM = "slurm"
"""Constant to represent the scheduler to use is PBS Torque"""
SCHEDULER_TORQUE = "torque"


class ArgumentConverter:
    # Define which options are vaild of each of the schedulers
    VAILD_TORQUE = ["a", "b", "e", "f"]  # abort, begin, end
    VALID_SLURM = [
        "BEGIN",
        "END",
        "FAIL",
        "REQUEUE",
        "ALL",
        "INVALID_DEPEND",
        "STAGE_OUT",
        "TIME_LIMIT",
        "TIME_LIMIT_90",
        "TIME_LIMIT_80",
        "TIME_LIMIT_50",
        "ARRAY_TASKS",
    ]
    SLURM_TO_TORQUE = {
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
        "ARRAY_TASKS": "",
    }
    TORQUE_TO_SLURM = {
        "a": "FAIL,INVALID_DEPEND,TIME_LIMIT",
        "b": "BEGIN",
        "e": "END",
        "f": "FAIL",
        "n": "FAIL",
        "p": "NONE",
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
        if options == "":
            return False  # cannot be empty
        if options == "NONE":
            return True  # None must stand alone
        return all(opt in self.VALID_SLURM for opt in options.split(","))

    def _is_torque_options(self, options):
        # For each character in the options, check if it is a valid torque
        # option. If all are, return true, otherwise, false
        if options == "":
            return False  # cannot be empty
        if options == "n" or options == "p":
            return True  # n and p must be alone
        return all(opt in self.VAILD_TORQUE for opt in options)

    def convert_notifications(self, scheduler, notifications):
        # Check if the options we have match the scheduler we have
        if scheduler == SCHEDULER_SLURM and self._is_torque_options(notifications):
            # Scheduler is slurm, but notifications are torque.
            # convert then return
            return self._torque_to_slurm(notifications)
        elif scheduler == SCHEDULER_TORQUE and self._is_slurm_options(notifications):
            # Scheduler is torque, notifications are slurm.
            # convert, then return
            return self._slurm_to_torque(notifications)
        elif scheduler == SCHEDULER_SLURM and not self._is_slurm_options(notifications):
            # Options passed are invalid; use a default
            return "ALL"
        elif scheduler == SCHEDULER_TORQUE and not self._is_torque_options(
            notifications
        ):
            return "abe"
        # Scheduler and options match; return the original notification options
        # (Also, if notifications are invalid this leaves them intact/unmodified)
        return notifications


class JobfileGenerator:
    def __init__(self, job_json_obj, batch_file: str, scheduler: str = None):
        """Generates the job files, e.g. PBS and SLURM."""
        logging.info("Initialising job file generator")
        self._batch_file = batch_file
        self._job_json_obj = job_json_obj
        self._job_data = job_json_obj.get("job").get("job_options", {})
        self._app_data = job_json_obj.get("job").get("application", {})
        self._opt_data = job_json_obj.get("job").get("optimisation", {})
        self._singularity_exec = "singularity exec"
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

        self._env = Environment(
            loader=FileSystemLoader(
                pathlib.Path(__file__).parent.resolve() / "templates"
            ),
            trim_blocks=True,
        )

    # Based on https://kb.northwestern.edu/page.php?id=89454

    def _generate_torque_header(self):
        logging.info("Generating torque header")
        template = self._env.get_template("torque.header")
        with self._batch_file.open("w") as fhandle:
            fhandle.write(template.render(job_data=self._job_data))

        if "node_count" in self._job_data and "request_gpus" in self._job_data:
            self._singularity_exec = self._singularity_exec + " --nv"

    def _generate_slurm_header(self):
        logging.info("Generating slurm header")
        template = self._env.get_template("slurm.header")
        with self._batch_file.open("w") as fhandle:
            fhandle.write(template.render(job_data=self._job_data))

        if "request_gpus" in self._job_data:
            self._singularity_exec = self._singularity_exec + " --nv"

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
            return

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
        with open(self._batch_file, "a") as fhandle:
            parsed_url = urlparse(scriptlink)

            if parsed_url.scheme == "file":
                source_path = pathlib.Path(parsed_url.path)

                if parsed_url.netloc == "modak-builtin":
                    source_path = (
                        pathlib.Path(__file__).parent.resolve()
                        / "scripts"
                        / source_path.relative_to("/")
                    )

                fhandle.write(source_path.read_text())

            elif parsed_url.scheme in ("http", "https"):
                try:
                    scriptcontents = urllib.request.urlopen(scriptlink)
                    fhandle.write(scriptcontents.read().decode("UTF-8"))
                except Exception as e:
                    logging.info(f"Could not inline optscript: {e}")
                    fhandle.write(
                        f"""
file={scriptfile}
if [ -f $file ] ; then rm "$file"; fi
wget --no-check-certificate '{scriptlink}'
chmod 755 "{scriptfile}"
source "{scriptfile}"
"""
                    )
            else:
                raise AssertionError(
                    f"Unsupported protocol '{parsed_url.scheme}' in script link '{scriptlink}'"
                )

        logging.info("Successfully added optimisation")

    def add_apprun(self):
        logging.info("Adding app run")
        with self._batch_file.open("a") as fhandle:
            exe = self._app_data.get("executable", "")
            args = self._app_data.get("arguments", "")
            if args:
                exe += f" {args}"

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
