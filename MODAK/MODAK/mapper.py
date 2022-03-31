from typing import Any, Awaitable, Callable, List, Mapping, Optional, Sequence, cast

from loguru import logger
from sqlalchemy import insert, select

from .db import Map
from .db import Optimisation as OptimisationDB
from .driver import Driver
from .model import (
    Application,
    AppTypeAITraining,
    AppTypeHPC,
    Optimisation,
    OptimisationBuild,
)
from .settings import Settings


def _mapping2list(map: Mapping):
    """Converts a mapping to a list of k1.lower():v1.lower(), k2:v2, ..."""
    return [f"{str(key).lower()}:{str(value).lower()}" for key, value in map.items()]


class Mapper:
    def __init__(self, driver: Driver):
        logger.info("Initialised MODAK mapper")
        self._driver = driver
        self._opts: List[str] = []
        self._app_name: str = ""

    async def map_container(
        self,
        app: Application,
        optimisation: Optional[Optimisation] = None,
    ) -> Optional[str]:
        """Get an URI for an optimal container for the given job."""

        logger.info("Mapping to optimal container")

        dsl_code = await self.get_dsl_code(app, optimisation)
        if not dsl_code:
            return None

        return await self.get_container(dsl_code)

    async def get_dsl_code(
        self, app: Application, optimisation: Optional[Optimisation] = None
    ) -> Optional[str]:
        logger.info(str(optimisation))

        self._opts = []
        dsl_code: Optional[str] = None

        # try type-specific decodes first
        decoders: Sequence[Callable[..., Awaitable[Optional[str]]]] = (
            self._decode_ai_training_opt,
            self._decode_hpc_opt,
            self._decode_opts,
        )
        for decoder in decoders:
            dsl_code = await decoder(app.app_tag, optimisation)
            if dsl_code is not None:
                logger.info(f"Decoded opt code: {dsl_code}")
                break
        else:
            logger.warning("No valid DSL code found for given job")

        return dsl_code

    async def add_optcontainer(self, map_obj):
        logger.info(f"Adding optimal container {map_obj}")
        await self.add_optimisation(
            map_obj.get("name"),
            map_obj.get("app_name"),
            map_obj.get("build"),
            map_obj.get("optimisation"),
        )
        await self.add_container(
            map_obj.get("name"),
            map_obj.get("container_file"),
            map_obj.get("image_hub"),
            map_obj.get("image_type"),
            map_obj.get("src"),
        )

    async def add_container(
        self,
        opt_dsl_code: str,
        container_file: str,
        image_hub: str = "docker",
        image_type: str = "docker",
        src: str = "",
    ):
        logger.info("Adding container to mapper ")

        stmt = insert(Map).values(
            opt_dsl_code=opt_dsl_code,
            container_file=container_file,
            image_type=image_type,
            image_hub=image_hub,
            src=src,
        )
        await self._driver.update_sql(stmt)

        return True

    async def add_optimisation(
        self, opt_dsl_code: str, app_name: str, target: Mapping, optimisation: Mapping
    ):
        logger.info("Adding DSL code to Optimisation ")

        target_str = "|".join(_mapping2list(target))
        opt_str = "|".join(_mapping2list(optimisation))

        logger.info(f"Target string: '{target_str}'")
        logger.info(f"Opt string: '{opt_str}'")

        stmt = insert(OptimisationDB).values(
            opt_dsl_code=opt_dsl_code,
            app_name=app_name,
            target=target_str,
            optimisation=opt_str,
            version="",
        )

        await self._driver.update_sql(stmt)
        return True

    async def get_container(self, opt_dsl_code: str) -> Optional[str]:
        """Given a DSL code, return a container URI if found"""

        logger.info(f"Get container for opt code: {opt_dsl_code}")

        stmt = (
            select(Map.container_file, Map.image_type, Map.image_hub)
            .where(Map.opt_dsl_code == opt_dsl_code)
            .order_by(Map.map_id.desc())
            .limit(1)
        )
        data = await self._driver.select_sql(stmt)

        if data:
            container_file = data[0][0]
            image_hub = data[0][2]

            # replace the image hub with the alias if available
            image_hub = Settings.image_hub_aliases.get(image_hub, image_hub)

            container_link = f"{image_hub}://{container_file}"
            logger.info(f"Container link: {container_link}")
            return container_link

        logger.warning("No optimal container found")
        return None

    async def _decode_hpc_opt(
        self, app_name: Optional[str], opt: Optional[Optimisation] = None
    ) -> Optional[str]:
        """Get a DSL code for the given optimisation values for the HPC app_type"""

        logger.info("Decoding HPC optimisation")

        if not opt or opt.app_type != "hpc":
            return None

        logger.info("Decoding HPC application")

        # the model ensures that for a given config/parallelisation
        # there is a parallelisation-* submodel
        optimisations = getattr(
            opt.app_type_hpc,
            f"parallelisation_{cast(AppTypeHPC, opt.app_type_hpc).config.parallelisation}",
        )

        # if we have a specific application container (e.g. not just one with an MPI impl
        # which needs to be built during deployment) we use that one as application name.
        # Otherwise we fallback to the MPI runtime library.
        if app_name:
            opt_dict = optimisations.dict()
        else:
            app_name = optimisations.library
            # if we do the fallback to the library, the "library" keyword in the optimisation
            # should not be considered anymore as an optimization for the mapping since
            # we already expect that any optimisations wrt to the selected runtime library
            # are baked into the specific runtime library container.
            opt_dict = {k: v for k, v in optimisations.dict().items() if k != "library"}

        return await self._decode_opts(app_name, opt, opt_dict)

    async def _decode_ai_training_opt(
        self, _: Optional[str], opt: Optional[Optimisation] = None
    ) -> Optional[str]:
        """Get a DSL code for the given optimisation values for the ai_training app_type"""

        if not opt or opt.app_type != "ai_training":
            return None

        logger.info("Decoding AI training application")

        app_name = cast(AppTypeAITraining, opt.app_type_ai_training).config.ai_framework
        optimisations = getattr(opt.app_type_ai_training, f"ai_framework_{app_name}")
        return await self._decode_opts(app_name, opt, optimisations.dict())

    async def _decode_opts(
        self,
        app_name: Optional[str],
        opt: Optional[Optimisation] = None,
        opt_dict: Optional[Mapping[str, Any]] = None,
    ) -> Optional[str]:
        """
        Get a DSL code for app_name, restricted by the given optimisations
        in opt_dict and targetting arch and accelerator given in opt.
        """

        if not app_name:
            return None

        self._app_name = app_name

        stmt = select(OptimisationDB.opt_dsl_code).where(
            OptimisationDB.app_name == app_name
        )

        if opt and opt.enable_opt_build:
            target_nodes = _mapping2list(cast(OptimisationBuild, opt.opt_build).dict())
            for node in target_nodes:
                stmt = stmt.where(OptimisationDB.target.like(f"%{node}%"))

            if opt_dict:
                opt_nodes = _mapping2list(opt_dict)
                for node in opt_nodes:
                    stmt = stmt.where(OptimisationDB.optimisation.like(f"%{node}%"))
                    self._opts.append(node)

            stmt = stmt.where(OptimisationDB.target.like("%enable_opt_build:true%"))
        else:
            # treat a missing Optimisation as an implicit enable_opt_build=False
            stmt = stmt.where(OptimisationDB.target.like("%enable_opt_build:false%"))

        data = await self._driver.select_sql(stmt)
        if data:
            dsl_code = data[0][0]
            logger.info(f"Decoded DSL code: {dsl_code}")
            return dsl_code

        logger.warning("Failed to find a matching DSL code")
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
            else:
                raise AssertionError(f"app_type {opt.app_type} not supported")

            opts += _mapping2list(optimisations)

        return opts
