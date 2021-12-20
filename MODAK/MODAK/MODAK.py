import io
import logging
from copy import deepcopy
from datetime import datetime
from typing import IO, NamedTuple, Optional

import jinja2
from sqlalchemy import select

from . import db
from .driver import Driver
from .enforcer import Enforcer
from .jobfile_generator import JobfileGenerator
from .mapper import Mapper
from .model import Application, Job, JobOptions, Target
from .model.infrastructure import Infrastructure
from .scaler import Scaler
from .settings import Settings

JobScripts = NamedTuple("JobScripts", [("jobscript", str), ("buildscript", str)])


class InvalidConfigurationError(Exception):
    pass


class MODAK:
    def __init__(self, upload=False):
        """General MODAK class."""
        logging.info("Intialising MODAK")

        self._driver = Driver()
        self._map = Mapper(self._driver)
        self._scaler = Scaler(self._driver)
        self._enf = Enforcer(self._driver)

        self._upload = upload
        if self._upload:
            from MODAK_gcloud import TransferData

            self._drop = TransferData()

        logging.info("Successfully intialised MODAK")

    def optimise(self, job: Job) -> JobScripts:
        logging.info(f"Processing job data {job}")

        job_file = (
            Settings.out_dir
            / f"{job.job_options.job_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.sh"
        )
        with job_file.open("w") as job_fhandle:
            self._get_optimisation(job, job_fhandle)

        build_file = (
            Settings.out_dir
            / f"{job.job_options.job_name}_build_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        with build_file.open("w") as fhandle:
            self._get_buildjob(job, fhandle)

        if self._upload:
            file_to = (
                f"/modak/{job.job_options.job_name}"
                f"_{datetime.now().strftime('%Y%m%d%H%M%S')}.sh"
            )
            build_file_to = (
                f"/modak/build_{job.job_options.job_name}"
                f"_{datetime.now().strftime('%Y%m%d%H%M%S')}.sh"
            )
            job_link = self._drop.upload_file(file_from=job_file, file_to=file_to)
            build_link = self._drop.upload_file(
                file_from=build_file, file_to=build_file_to
            )
        else:
            job_link = job_file
            build_link = build_file

        logging.info(f"Job script link: {job_link}")
        logging.info(f"Build script link: {build_link}")
        return JobScripts(str(job_link), str(build_link))

    def get_opt_container_runtime(self, job: Job) -> Optional[str]:
        logging.info("Mapping to optimal container for job data")

        new_container = None

        if job.optimisation:
            new_container = self._map.map_container(job.application, job.optimisation)

        logging.info(f"Optimal container found: {new_container}")
        return new_container

    def get_buildjob(self, job: Job) -> str:
        job_fhandle = io.StringIO()
        self._get_buildjob(job, job_fhandle)
        return job_fhandle.getvalue()

    def _get_buildjob(self, job: Job, job_fhandle: IO[str]) -> None:
        logging.info("Creating build script for job")
        logging.info(f"Processing build data: {job}")

        if not job.application.build:
            logging.info(
                "No job.application.build section in request, returning empty resposne"
            )
            return

        build = job.application.build

        final_build = ""
        if build.src[-4:] == ".git":
            final_build = f"git clone {build.src}\n"
        else:
            final_build = f"wget --no-check-certificate '{build.src}'\n"

        process_per_node = build.build_parallelism

        t = jinja2.Template(build.build_command)
        final_build += t.render(BUILD_PARALLELISM=process_per_node)

        build_job = deepcopy(job)
        build_job.job_options.job_name += "_build"
        build_job.job_options.node_count = 1
        build_job.job_options.process_count_per_node = process_per_node
        build_job.job_options.standard_output_file = (
            f"build-{job.job_options.standard_output_file}"
        )
        build_job.job_options.standard_error_file = (
            f"build-{job.job_options.standard_error_file}"
        )
        build_job.application.executable = final_build

        self._get_optimisation(build_job, job_fhandle)

    def get_optimisation(self, job: Job) -> str:
        job_file = io.StringIO()
        self._get_optimisation(job, job_file)
        return job_file.getvalue()

    def _get_optimisation(self, job: Job, job_fhandle: IO[str]) -> None:

        # if mapper finds an optimised container based on requested optimisation,
        # update the container runtime of application
        new_container = self.get_opt_container_runtime(job)
        if new_container:
            job.application.container_runtime = new_container
            logging.info("Successfully updated container runtime")

        if job.target:
            self._target_completion(job.target)

        self._scaler.scale(job.application, job.optimisation)

        if job.target:
            # needs to run after the scaler since nranks/nthreads may have been updated
            self._job_completion(job.target, job.job_options, job.application)

        logging.info("Generating job file header")
        gen_t = JobfileGenerator(
            job.application,
            job.job_options,
            batch_fhandle=job_fhandle,
            scheduler=str(job.target.job_scheduler_type) if job.target else "",
        )

        logging.info("Adding job header")
        gen_t.add_job_header()

        if job.optimisation and job.optimisation.enable_autotuning:
            logging.info("Adding autotuning scripts")
            gen_t.add_tuner(self._upload)

        decoded_opts = self._map.get_decoded_opts(job.optimisation)
        logging.info(f"Applying optimisations {decoded_opts}")

        scripts, tenv = self._enf.enforce_opt(self._map.app_name, job, decoded_opts)

        for script in scripts:
            if script.data.stage == "pre":
                gen_t.add_optscript(script, tenv)

        logging.info("Adding application run")
        gen_t.add_apprun()

        for script in scripts:
            if script.data.stage == "post":
                gen_t.add_optscript(script, tenv)

    def _target_completion(self, target: Target) -> None:
        """Verify that all required attributes in a given Target are filled"""

        if target.job_scheduler_type:
            return

        dbinfra = self._driver.select_sql(
            select(db.Infrastructure).filter(db.Infrastructure.name == target.name)
        )
        if not dbinfra:
            raise InvalidConfigurationError(
                f"Target scheduler not specified and infrastructure '{target.name}' not found."
            )

        iconf = Infrastructure.from_orm(dbinfra[0][0]).configuration
        target.job_scheduler_type = iconf.scheduler

    def _job_completion(
        self, target: Target, jobopts: JobOptions, app: Application
    ) -> None:
        """Fill in job/scheduler attributes based on the given infrastructure"""

        if target.job_scheduler_type == "none" or not target.name:
            # Without a scheduler we don't have to complete job options
            return

        dbinfra = self._driver.select_sql(
            select(db.Infrastructure).filter(db.Infrastructure.name == target.name)
        )
        if (
            not dbinfra
        ):  # if there is no matching infra, there is nothing we can complete here
            return

        iconf = Infrastructure.from_orm(dbinfra[0][0]).configuration

        if jobopts.partition is None:
            # if there's only one partition in the infra we don't have much choice, otherwise use the default, if available
            if len(iconf.partitions) == 1:
                partition = next(iter(iconf.partitions.values()))
            else:
                try:
                    partition = next(p for p in iconf.partitions.values() if p.default)
                except StopIteration:
                    logging.error(
                        f"The target infrastructure '{target.name}' has more than one partition but no default partition"
                    )
                    return
        else:
            try:
                partition = iconf.partitions[jobopts.partition]
            except KeyError:
                raise InvalidConfigurationError(
                    f"Partition '{jobopts.partition}' found in infrastructure '{target.name}'"
                ) from None

        nnodes = jobopts.node_count

        if not nnodes:
            nnodes = -(
                -app.mpi_ranks // (partition.node.ncpus * partition.node.cpu.ncores)
            )

        if nnodes > partition.nnodes:
            raise InvalidConfigurationError(
                f"The required number of nodes is bigger than the available number of nodes: {nnodes} > {partition.nnodes}"
            )

        jobopts.node_count = nnodes
