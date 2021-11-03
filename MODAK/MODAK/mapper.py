import logging
from typing import List, Mapping, Optional, cast

from sqlalchemy import insert, select

from .db import Map
from .db import Optimisation as OptimisationDB
from .MODAK_driver import MODAK_driver
from .model import (
    AppTypeAITraining,
    AppTypeHPC,
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

    def map_container(
        self, optimisation: Optimisation, target: Optional[Target] = None
    ) -> Optional[str]:
        """Get an URI for an optimal container for the given job."""

        logging.info("Mapping to optimal container")
        self._opts = []

        logging.info(str(optimisation))
        dsl_code = None

        if optimisation.app_type == "ai_training":
            logging.info("Decoding AI training application")
            dsl_code = self.decode_ai_training_opt(optimisation)
        elif optimisation.app_type == "hpc":
            logging.info("Decoding HPC application")
            dsl_code = self.decode_hpc_opt(optimisation)
        else:
            raise AssertionError(f"app_type {optimisation.app_type} not supported")

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

        stmt = insert(Map).values(
            opt_dsl_code=opt_dsl_code,
            container_file=container_file,
            image_type=image_type,
            image_hub=image_hub,
            src=src,
        )
        self._driver.updateSQL(stmt)

        return True

    def add_optimisation(
        self, opt_dsl_code: str, app_name: str, target: Mapping, optimisation: Mapping
    ):
        logging.info("Adding DSL code to Optimisation ")

        target_str = ",".join(_mapping2list(target))
        opt_str = ",".join(_mapping2list(optimisation))

        logging.info(f"Target string: '{target_str}'")
        logging.info(f"Opt string: '{opt_str}'")

        stmt = insert(OptimisationDB).values(
            opt_dsl_code=opt_dsl_code,
            app_name=app_name,
            target=target_str,
            optimisation=opt_str,
            version="",
        )

        self._driver.updateSQL(stmt)
        return True

    def get_container(self, opt_dsl_code: str) -> Optional[str]:
        """Given a DSL code, return a container URI if found"""

        logging.info(f"Get container for opt code: {opt_dsl_code}")

        stmt = (
            select(Map.container_file, Map.image_type, Map.image_hub)
            .where(Map.opt_dsl_code == opt_dsl_code)
            .order_by(Map.map_id.desc())
            .limit(1)
        )
        data = self._driver.selectSQL(stmt)

        if data:
            container_file = data[0][0]
            image_hub = data[0][2]

            # replace the image hub with the alias if available
            image_hub = Settings.image_hub_aliases.get(image_hub, image_hub)

            container_link = f"{image_hub}://{container_file}"
            logging.info(f"Container link: {container_link}")
            return container_link

        logging.warning("No optimal container found")
        return None

    def decode_hpc_opt(self, opt: Optimisation) -> Optional[str]:
        """Get a DSL code for the given optimisation values for the HPC app_type"""

        logging.info("Decoding HPC optimisation")

        assert opt.app_type == "hpc"

        # the model ensures that for a given config/parallelisation
        # there is a parallelisation-* submodel
        optimisations = getattr(
            opt.app_type_hpc,
            f"parallelisation_{cast(AppTypeHPC, opt.app_type_hpc).config.parallelisation}",
        )
        app_name = optimisations.library
        return self._decode_opts(
            app_name,
            opt,
            {k: v for k, v in optimisations.dict().items() if k not in ("library",)},
        )

    def decode_ai_training_opt(self, opt: Optimisation) -> Optional[str]:
        """Get a DSL code for the given optimisation values for the ai_training app_type"""

        logging.info("Decoding AI training optimisation")

        assert opt.app_type == "ai_training"
        app_name = cast(AppTypeAITraining, opt.app_type_ai_training).config.ai_framework
        optimisations = getattr(opt.app_type_ai_training, f"ai_framework_{app_name}")
        return self._decode_opts(app_name, opt, optimisations.dict())

    def _decode_opts(self, app_name: str, opt: Optimisation, opt_dict: Mapping):
        self._app_name = app_name

        stmt = select(OptimisationDB.opt_dsl_code).where(
            OptimisationDB.app_name == app_name
        )

        if opt.enable_opt_build:
            target_nodes = _mapping2list(cast(OptimisationBuild, opt.opt_build).dict())
            for node in target_nodes:
                stmt = stmt.where(OptimisationDB.target.like(f"%{node}%"))

            opt_nodes = _mapping2list(opt_dict)
            for node in opt_nodes:
                stmt = stmt.where(OptimisationDB.optimisation.like(f"%{node}%"))
                self._opts.append(node)

            stmt = stmt.where(OptimisationDB.target.like("%enable_opt_build:true%"))
        else:
            stmt = stmt.where(OptimisationDB.target.like("%enable_opt_build:false%"))

        data = self._driver.selectSQL(stmt)
        if data:
            dsl_code = data[0][0]
            logging.info(f"Decoded DSL code: {dsl_code}")
            return dsl_code

        logging.warning("Failed to find a matching DSL code")
        return None

    def get_opts(self):
        """
        Get the list of opts ("k:v" with k:v from either config.parallelisation
        or ai_framework-*) after decoding from a request via decode_*
        """

        return self._opts

    @property
    def app_name(self):
        return self._app_name

    def get_decoded_opts(self, opt: Optional[Optimisation] = None):
        """
        Get a list of strings from the respectives optimisation type config.*
        section of keys&values.
        """
        opts = []

        if opt and opt.opt_build:
            if opt.app_type == "ai_training":
                app_name_ai = cast(
                    AppTypeAITraining, opt.app_type_ai_training
                ).config.ai_framework
                optimisations = getattr(
                    opt.app_type_ai_training,
                    f"ai_framework_{app_name_ai}",
                ).dict()
            elif opt.app_type == "hpc":
                app_name_hpc = cast(AppTypeHPC, opt.app_type_hpc).config.parallelisation
                optimisations = getattr(
                    opt.app_type_hpc,
                    f"parallelisation_{app_name_hpc}",
                ).dict()
                optimisations = {
                    k: v for k, v in optimisations.items() if k not in ("library",)
                }
            else:
                raise AssertionError(f"app_type {opt.app_type} not supported")

            opts += _mapping2list(optimisations)

        return opts
