import logging
from datetime import datetime
from typing import Any, List, Tuple

import sqlalchemy as sa

# from MODAK_sql import MODAK_sql
from .settings import DEFAULT_SETTINGS_DIR, Settings


class MODAK_driver:
    """This is the driver program that will drive the MODAK"""

    # dblist = []
    logging.basicConfig(
        filename=DEFAULT_SETTINGS_DIR
        / ".."
        / "log"
        / f"MODAK{datetime.now().strftime('%b_%d_%Y_%H_%M_%S')}.log",
        filemode="w",
        level=logging.DEBUG,
    )
    logging.getLogger("py4j").setLevel(logging.ERROR)

    def __init__(self, conf_file=DEFAULT_SETTINGS_DIR / "iac-model.ini", install=False):
        logging.info("Initialising driver")
        Settings.initialise(conf_file)

        logging.info("Connecting to model repo using DB dialect: {Settings.DB_DIALECT}")
        assert Settings.DB_DIALECT == "sqlite", "only SQLite is currently supported"

        self._engine = sa.create_engine(f"sqlite:///{Settings.DB_PATH}")
        logging.info("Successfully initialised driver")

    def selectSQL(self, stmt: str) -> List[Tuple[Any, ...]]:
        logging.info(f"Selecting : {stmt}")
        with sa.orm.Session(self._engine, future=True) as session:
            result = session.execute(stmt).all()
            logging.info("Successfully selected SQL")

        return result

    def updateSQL(self, stmt: str):
        with sa.orm.Session(self._engine, future=True) as session:
            session.execute(stmt)
            session.commit()
            logging.info("Successfully updated SQL")
