import logging
import pathlib
from typing import IO, Any, Dict, List

from jinja2 import Environment, FileSystemLoader, Template

from .model import Application, ApplicationBuild, JobOptions, Optimisation, Script
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
    def __init__(
        self,
        application: Application,
        job_options: JobOptions,
        batch_fhandle: IO[str],
        scheduler: str,
    ):
        """Generates the job files, e.g. PBS and SLURM."""
        logging.info("Initialising job file generator")
        self._batch_fhandle = batch_fhandle
        self._job_options = job_options
        self._application = application
        self._scheduler = scheduler

        self._singularity_args: List[str] = []
        self.ac = ArgumentConverter()
        # TODO: scheduler type should be derived based on the infrastructure target name
        # TODO: there shall be an entry in the database where scheduler type
        #       is specified in the infrastructure target

        # use an explicitly given scheduler, if provided, otherwise determine from DSL

        self._env = Environment(  # NOSONAR
            loader=FileSystemLoader(
                pathlib.Path(__file__).parent.resolve() / "templates"
            ),
            trim_blocks=True,
        )

    # Based on https://kb.northwestern.edu/page.php?id=89454

    def _generate_torque_header(self):
        logging.info("Generating torque header")
        template = self._env.get_template("torque.header")
        self._batch_fhandle.write(template.render(job_data=self._job_options))

        if self._job_options.node_count and self._job_options.request_gpus:
            self._singularity_args.append("--nv")

    def _generate_slurm_header(self):
        logging.info("Generating slurm header")
        template = self._env.get_template("slurm.header")
        self._batch_fhandle.write(template.render(job_data=self._job_options))

        if self._job_options.request_gpus:
            self._singularity_args.append("--nv")

    def _generate_bash_header(self):
        logging.info("Generating bash header")
        self._batch_fhandle.write("#!/bin/bash\n\n")

    def add_job_header(self):
        if self._scheduler == "torque":
            self._generate_torque_header()
        elif self._scheduler == "slurm":
            self._generate_slurm_header()
        else:
            self._generate_bash_header()

    def _singularity_args_str(self):
        if self._singularity_args:
            return " " + " ".join(f'"{a}"' for a in self._singularity_args)
        return ""

    def add_tuner(self, optimisation: Optimisation, upload=True):
        tuner = Tuner(upload)
        res = tuner.encode_tune(optimisation, self._batch_fhandle)
        if not res:
            logging.warning("Tuning not enabled or Encoding tuner failed")
            return

        logging.info("Adding tuner" + str(tuner))
        self._batch_fhandle.write(
            f"""
## START OF TUNER ##
file={tuner.get_tune_filename()}
[ -f $file ] && rm "$file"
wget --no-check-certificate '{tuner.get_tune_link()}'
chmod 755 '{tuner.get_tune_filename()}'
"""
        )
        if self._application.container_runtime:
            cont = self._application.container_runtime
            self._batch_fhandle.write(
                f"\nsingularity exec{self._singularity_args_str()}"
                f' "{self.get_sif_filename(cont)}" "{tuner.get_tune_filename()}"'
            )
            self._batch_fhandle.write("\n")
        else:
            self._batch_fhandle.write(f"source '{tuner.get_tune_filename()}'\n")
        self._batch_fhandle.write("## END OF TUNER ##\n")
        logging.info("Successfully added tuner")

    def add_optscript(self, script: Script, tenv: Dict[str, Any]):
        logging.info(f"Adding optimisation script: {script.id} ({script.description})")
        if script.data.raw:
            self._batch_fhandle.write(f"# MODAK: Start Script<id={script.id}>\n")
            template = Template(script.data.raw)
            self._batch_fhandle.write(template.render(**tenv))
            self._batch_fhandle.write(f"\n# MODAK: End   Script<id={script.id}>\n")
        else:
            raise AssertionError(
                f"No data found in script {script.id} and no other methods implemented"
            )
        logging.info("Successfully added optimisation")

    @staticmethod
    def _write_apprun_build(
        fhandle: IO[str], build: ApplicationBuild, container_exec_cmd: str
    ):
        if build.src[-4:] == ".git":
            fhandle.write(f"\ngit clone {build.src}\n")
        else:
            fhandle.write(f"\nwget --no-check-certificate {build.src}\n")
        fhandle.write(f"\n{container_exec_cmd} {build.build_command}\n")

    def _write_apprun_hpc(self, fhandle: IO[str], container_exec_cmd: str, exe: str):
        mpi_ranks = self._application.mpi_ranks
        threads = self._application.threads
        fhandle.write(f"\nexport OMP_NUM_THREADS={threads}\n")

        if self._scheduler == "slurm":
            fhandle.write(f"srun -n {mpi_ranks} {container_exec_cmd} {exe}\n")
        else:
            fhandle.write(f"mpirun -np {mpi_ranks} {container_exec_cmd} {exe}\n")

    def add_apprun(self):
        logging.info("Adding app run")

        exe = self._application.executable
        cont = self._application.container_runtime

        if not exe and not cont:
            raise ValueError(
                "Neither the executable nor a container is set, can not run anything"
            )

        cont_exec_command = ""
        if cont:
            cont_exec_command = "singularity exec" if exe else "singularity run"
            cont_exec_command += (
                f'{self._singularity_args_str()} "{self.get_sif_filename(cont)}"'
            )

        args = self._application.arguments
        if args:
            exe += f" {args}"

        if self._application.build:
            self._write_apprun_build(
                self._batch_fhandle, self._application.build, cont_exec_command
            )

        if self._application.app_type in ("mpi", "hpc"):
            self._write_apprun_hpc(self._batch_fhandle, cont_exec_command, exe)
        else:  # other app types, e.g. python
            self._batch_fhandle.write(f"{cont_exec_command} {exe}\n")

        logging.info("Successfully added app run")

    def get_sif_filename(self, container: str):
        words = container.split("/")
        return f"$SINGULARITY_DIR/{words[-1].replace(':', '_')}.sif"
