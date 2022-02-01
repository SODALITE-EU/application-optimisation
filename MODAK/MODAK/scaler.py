from typing import List, Optional, Tuple, cast

from sqlalchemy import select

from .db import ScalingModel
from .driver import Driver
from .mapper import Mapper
from .model import Application, Optimisation
from .model.scaling import ApplicationScalingModel


class Scaler:
    def __init__(self, driver: Driver):
        self._driver = driver

    async def scale(
        self, app: Application, optimisation: Optional[Optimisation] = None
    ):

        # TODO: here we dupliate the Mapper object and obtain the DSL code again
        #       to be able to lookup any model specs. The proper way would probably
        #       be for Mapper to return an object right from the start, rather than
        #       this duplicated/convoluted effort. Duplicating the mapper since
        #       get_dsl_code() changes the class' state.
        mapper = Mapper(self._driver)
        dsl_code = await mapper.get_dsl_code(app, optimisation)

        if dsl_code is None:
            return None

        models = cast(
            List[Tuple[ScalingModel]],
            await self._driver.select_sql(
                select(ScalingModel).where(ScalingModel.opt_dsl_code == dsl_code)
            ),
        )

        if not models:
            return None

        # the pydantic Model will do a dispatch based on matching type (e.g. the 'name' literal)
        appmodel = ApplicationScalingModel.from_orm(models[0][0])

        return appmodel.model.scale(app)
