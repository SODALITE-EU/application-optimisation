import logging
from datetime import datetime
from typing import Any, List, Tuple, Union

import sqlalchemy as sa

from .settings import DEFAULT_SETTINGS_DIR, Settings


class Driver:
    """This is the driver program that will drive the MODAK"""

    logging.basicConfig(
        filename=DEFAULT_SETTINGS_DIR
        / ".."
        / "log"
        / f"MODAK{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}.log",
        filemode="w",
        level=logging.DEBUG,
    )
    logging.getLogger("py4j").setLevel(logging.ERROR)

    def __init__(self, engine=None):
        logging.info("Initialising driver")

        logging.info("Connecting to model repo using DB dialect: {Settings.db_dialect}")
        assert Settings.db_dialect == "sqlite", "only SQLite is currently supported"

        if engine:
            self._engine = engine
        else:
            self._engine = sa.create_engine(
                f"sqlite:///{Settings.db_path}", future=True
            )

        logging.info("Successfully initialised driver")

    def select_sql(self, stmt: sa.sql.Select) -> List[Tuple[Any, ...]]:
        logging.info(f"Selecting : {stmt}")
        with sa.orm.Session(self._engine, future=True) as session:
            result = session.execute(stmt).all()
            logging.info("Successfully selected SQL")

        return result

    def update_sql(self, stmt: Union[sa.sql.Delete, sa.sql.Update, sa.sql.Insert]):
        with sa.orm.Session(self._engine, future=True) as session:
            session.execute(stmt)
            session.commit()
            logging.info("Successfully updated SQL")
