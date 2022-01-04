from typing import List, Union

import sqlalchemy as sa
from loguru import logger
from sqlalchemy.engine import Row

from .settings import Settings


class Driver:
    """This is the driver program that will drive the MODAK"""

    def __init__(self, engine=None):
        logger.info("Initialising driver")

        logger.info("Connecting to model repo using DB dialect: {Settings.db_dialect}")
        assert Settings.db_dialect == "sqlite", "only SQLite is currently supported"

        if engine:
            self._engine = engine
        else:
            self._engine = sa.create_engine(
                f"sqlite:///{Settings.db_path}", future=True
            )

        logger.info("Successfully initialised driver")

    def select_sql(self, stmt: sa.sql.Select) -> List[Row]:
        logger.info(f"Selecting : {stmt}")
        with sa.orm.Session(self._engine, future=True) as session:
            result = session.execute(stmt).all()
            logger.info("Successfully selected SQL")

        return result

    def update_sql(self, stmt: Union[sa.sql.Delete, sa.sql.Update, sa.sql.Insert]):
        with sa.orm.Session(self._engine, future=True) as session:
            session.execute(stmt)
            session.commit()
            logger.info("Successfully updated SQL")
