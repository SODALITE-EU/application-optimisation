from typing import List, Union

import sqlalchemy as sa
from loguru import logger
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .settings import Settings


class Driver:
    """This is the driver program that will drive the MODAK"""

    def __init__(self, engine=None):
        logger.info("Initialising driver")

        if engine:
            self._engine = engine
        else:
            logger.info(
                "Connecting to model repo using DB dialect: {Settings.db_dialect}"
            )
            assert Settings.db_dialect == "sqlite", "only SQLite is currently supported"

            self._engine = create_async_engine(
                f"sqlite+aiosqlite:///{Settings.db_path}", future=True
            )

        self._session = sessionmaker(
            self._engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

        logger.info("Successfully initialised driver")

    async def select_sql(self, stmt: sa.sql.Select) -> List[Row]:
        logger.info(f"Selecting : {stmt}")
        async with self._session() as session:
            result = await session.execute(stmt)
            logger.info("Successfully selected SQL")

        return result.all()

    async def update_sql(
        self, stmt: Union[sa.sql.Delete, sa.sql.Update, sa.sql.Insert]
    ):
        async with self._session() as session:
            await session.execute(stmt)
            await session.commit()
            logger.info("Successfully updated SQL")

    @property
    def session(self):
        return self._session
