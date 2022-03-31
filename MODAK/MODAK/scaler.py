from typing import List, Optional, Tuple, cast

from sqlalchemy import select

from .db import ScalingModel
from .driver import Driver
from .mapper import Mapper
from .model import Application, Optimisation
from .model.scaling import ApplicationScalingModel


class Scaler:
    def __init__(self, driver: Driver, mapper: Mapper):
        self._driver = driver
        self._mapper = mapper

    async def scale(
        self, app: Application, optimisation: Optional[Optimisation] = None
    ):

        dsl_code = await self._mapper.get_dsl_code(app, optimisation)

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
