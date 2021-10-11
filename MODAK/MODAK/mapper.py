import logging
from typing import List, Mapping, Optional, cast

from .MODAK_driver import MODAK_driver
from .model import (
    AppTypeAITraining,
    AppTypeHPC,
    Job,
    Optimisation,
    OptimisationBuild,
    Target,
)
from .settings import Settings


def _mapping2list(map: Mapping):
    """Converts a mapping to a list of k1.lower():v1.lower(), k2:v2, ..."""
    return [f"{str(key).lower()}:{str(value).lower()}" for key, value in map.items()]


class Mapper:
    def __init__(self, driver: MODAK_driver):
        logging.info("Initialised MODAK mapper")
        self._driver = driver
        self._opts: List[str] = []

    def map_container(self, job: Job) -> Optional[str]:
        """Get an URI for an optimal container for the given job."""

        logging.info("Mapping to optimal container")
        self._opts = []

        assert job.optimisation is not None, "Optimisation data required for mapping"

        logging.info(str(job.optimisation))
        dsl_code = None

        try:
            self._opts.append(
                f"{cast(str, cast(Target, job.target).name).strip()}:true"
            )
        except AttributeError:
            pass

        if job.optimisation.app_type == "ai_training":
            logging.info("Decoding AI training application")
            dsl_code = self.decode_ai_training_opt(cast(Optimisation, job.optimisation))
        elif job.optimisation.app_type == "hpc":
            logging.info("Decoding HPC application")
            dsl_code = self.decode_hpc_opt(cast(Optimisation, job.optimisation))
        else:
            raise AssertionError(f"app_type {job.optimisation.app_type} not supported")

        if not dsl_code:
            logging.warning("No valid DSL code found for given job")
            return None

        logging.info(f"Decoded opt code: {dsl_code}")

        return self.get_container(dsl_code)

    def add_optcontainer(self, map_obj):
        logging.info(f"Adding optimal container {map_obj}")
        self.add_optimisation(
            map_obj.get("name"),
            map_obj.get("app_name"),
            map_obj.get("build"),
            map_obj.get("optimisation"),
        )
        self.add_container(
            map_obj.get("name"),
            map_obj.get("container_file"),
            map_obj.get("image_hub"),
            map_obj.get("image_type"),
            map_obj.get("src"),
        )

    def add_container(
        self,
        opt_dsl_code: str,
        container_file: str,
        image_hub: str = "docker",
        image_type: str = "docker",
        src: str = "",
    ):
        logging.info("Adding container to mapper ")
        stmt = """
            INSERT INTO `mapper`
             (`map_id`, `opt_dsl_code`, `container_file`, `image_type`, `image_hub`, `src`)
             VALUES
             (NULL, %(opt_dsl_code)s, %(container_file)s,
              %(image_type)s, %(image_hub)s, %(src)s)
            """

        logging.info(
            stmt
            % {
                "opt_dsl_code": opt_dsl_code,
                "container_file": container_file,
                "image_type": image_type,
                "image_hub": image_hub,
                "src": src,
            }
        )
        self._driver.updateSQL(
            stmt,
            {
                "opt_dsl_code": opt_dsl_code,
                "container_file": container_file,
                "image_type": image_type,
                "image_hub": image_hub,
                "src": src,
            },
        )
        return True

    def add_optimisation(
        self, opt_dsl_code: str, app_name: str, target: Mapping, optimisation: Mapping
    ):
        logging.info("Adding DSL code to Optimisation ")

        target_str = ",".join(_mapping2list(target))
        opt_str = ",".join(_mapping2list(optimisation))

        logging.info(f"Target string: '{target_str}'")
        logging.info(f"Opt string: '{opt_str}'")

        stmt = """
            INSERT INTO `optimisation`
              (`opt_dsl_code`, `app_name`, `target`, `optimisation`, `version`)
            VALUES
              (%(opt_dsl_code)s, %(app_name)s, %(target)s, %(optimisation)s, %(version)s)
            """

        logging.info(
            stmt.format(
                opt_dsl_code=opt_dsl_code,
                app_name=app_name,
                target=target_str,
                optimisation=opt_str,
                version="",
            )
        )
        self._driver.updateSQL(
            stmt,
            {
                "opt_dsl_code": opt_dsl_code,
                "app_name": app_name,
                "target": target_str,
                "optimisation": opt_str,
                "version": "",
            },
        )
        return True

    def get_container(self, opt_dsl_code: str) -> Optional[str]:
        """Given a DSL code, return a container URI if found"""

        logging.info(f"Get container for opt code: {opt_dsl_code}")

        stmt = (
            "SELECT container_file, image_type, image_hub FROM mapper"
            " WHERE opt_dsl_code=%s ORDER BY map_id desc limit 1"
        )
        df = self._driver.applySQL(stmt, (opt_dsl_code,))

        if df.size > 0:
            container_file = df["container_file"][0]
            image_hub = df["image_hub"][0]

            # replace the image hub with the alias if available
            image_hub = Settings.IMAGE_HUB_ALIASES.get(image_hub, image_hub)

            container_link = f"{image_hub}://{container_file}"
            logging.info(f"Container link: {container_link}")
            return container_link

        logging.warning("No optimal container found")
        return None

    def decode_hpc_opt(self, opt: Optimisation) -> Optional[str]:
        logging.info("Decoding HPC optimisation")

        assert opt.app_type == "hpc"

        # the model ensures that for a given config/parallelisation
        # there is a parallelisation-* submodel
        optimisations = getattr(
            opt.app_type_hpc,
            f"parallelisation_{cast(AppTypeHPC, opt.app_type_hpc).config.parallelisation}",
        )

        sqlstr = "SELECT opt_dsl_code FROM optimisation WHERE app_name = %(app_name)s"

        if opt.enable_opt_build:
            target_nodes = _mapping2list(cast(OptimisationBuild, opt.opt_build).dict())
            for node in target_nodes:
                targetstr = f" AND target LIKE '%{node}%'"
                sqlstr += targetstr
                logging.info(f"Adding target query '{targetstr}'")

            opt_nodes = _mapping2list(
                {k: v for k, v in optimisations.dict().items() if k != "library"}
            )
            for node in opt_nodes:
                optstr = f" AND optimisation LIKE '%{node}%'"
                sqlstr += optstr
                logging.info(f"Adding opt query '{optstr}'")
                self._opts.append(node)

            sqlstr += " AND target LIKE '%enable_opt_build:true%'"
        else:
            sqlstr += " AND target LIKE '%enable_opt_build:false%'"

        df = self._driver.selectSQL(sqlstr, {"app_name": optimisations.library})
        if df.size > 0:
            dsl_code = df["opt_dsl_code"][0]
            logging.info(f"Decoded DSL code: {dsl_code}")
            return dsl_code

        logging.warning("Failed to find a matching DSL code")
        return None

    def decode_ai_training_opt(self, opt: Optimisation):
        logging.info("Decoding AI training optimisation")

        assert opt.app_type == "ai_training"

        app_name = cast(AppTypeAITraining, opt.app_type_ai_training).config.ai_framework

        sqlstr = "SELECT opt_dsl_code FROM optimisation WHERE app_name = %(app_name)s"

        if opt.enable_opt_build:
            target_nodes = _mapping2list(cast(OptimisationBuild, opt.opt_build).dict())
            for node in target_nodes:
                targetstr = f" AND target LIKE '%{node}%'"
                sqlstr += targetstr
                logging.info(f"Adding target query '{targetstr}'")

            optimisations = getattr(
                opt.app_type_ai_training, f"ai_framework_{app_name}"
            )
            opt_nodes = _mapping2list(optimisations.dict())
            logging.info(f"Optimisations: '{opt_nodes}'")
            for node in opt_nodes:
                optstr = f" AND optimisation LIKE '%{node}%'"
                sqlstr += optstr
                logging.info(f"Adding opt query '{optstr}'")
                self._opts.append(node)

            sqlstr += " AND target LIKE '%enable_opt_build:true%'"
        else:
            sqlstr += " AND target LIKE '%enable_opt_build:false%'"

        df = self._driver.selectSQL(sqlstr, {"app_name": app_name})
        if df.size > 0:
            dsl_code = df["opt_dsl_code"][0]
        else:
            dsl_code = None
        logging.info(f"Decoded dsl code '{dsl_code}'")
        return dsl_code

    def get_opts(self):
        return self._opts

    def get_decoded_opts(self, job: Job):
        opts = []

        if job.target:
            opts.append(f"{job.target.name}:true")

        opt = job.optimisation

        if opt and opt.opt_build:
            if opt.app_type == "ai_training":
                app_name_ai = cast(
                    AppTypeAITraining, opt.app_type_ai_training
                ).config.ai_framework
                optimisations = getattr(
                    opt.app_type_ai_training,
                    f"ai_framework_{app_name_ai}",
                )
            elif opt.app_type == "hpc":
                app_name_hpc = cast(AppTypeHPC, opt.app_type_hpc).config.parallelisation
                optimisations = getattr(
                    opt.app_type_hpc,
                    f"parallelisation_{app_name_hpc}",
                )
            else:
                raise AssertionError(f"app_type {opt.app_type} not supported")

            opts += _mapping2list(optimisations.dict())

        return opts
