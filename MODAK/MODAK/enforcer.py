import logging
from typing import List

from sqlalchemy import JSON, select

from . import db
from .MODAK_driver import MODAK_driver
from .model import Script, Target


class Enforcer:
    def __init__(self, driver: MODAK_driver):
        logging.info("Initialised MODAK enforcer")
        self._driver = driver

    def enforce_opt(
        self, app_name: str, target: Target, opts: List[str]
    ) -> List[Script]:
        logging.info(f"Enforcing opts {opts}")
        # TODO: do we enforce only one optimisation?
        # TODO: redo if it is the case
        scripts = []

        basestmt = select(db.Script).filter(
            db.Script.conditions["application"]["name"].as_string() == app_name
        )
        basestmts = []

        # TODO: at the moment the target name is optional
        if target.name:
            basestmts.append(
                basestmt.filter(
                    db.Script.conditions["infrastructure"]["name"].as_string()
                    == target.name
                )
            )

        basestmts.append(
            basestmt.filter(db.Script.conditions["infrastructure"] == JSON.NULL)
        )

        # Logic:
        #   1. Look for feature-conditional scripts for a given app
        #      and infra (if infra is defined)
        #   2. Look for feature-unconditional scripts for a given app
        #      and infra (if infra is defined)
        #   3. Repeat 1. & 2. without restriction for
        #      non-infra-restricted scripts
        for basestmt in basestmts:
            # TODO: currently we do an OR for each option,
            #       while we probably should be doing an AND
            for opt in opts:
                if "version" in opt:
                    logging.info("Ignore version as a optimisation")
                    continue

                opt_key, opt_value = opt.split(":")

                # "unparse" the options again to be able to use them to query
                # directly the features in Script
                if opt_value.lower() == "true":
                    stmt = basestmt.filter(
                        db.Script.conditions["application"]["feature"][
                            opt_key
                        ].as_boolean()
                        == True  # noqa: E712
                    )
                elif opt_value.lower() == "false":
                    stmt = basestmt.filter(
                        db.Script.conditions["application"]["feature"][
                            opt_key
                        ].as_boolean()
                        == False  # noqa: E712
                    )
                else:
                    try:
                        stmt = basestmt.filter(
                            db.Script.conditions["application"]["feature"][
                                opt_key
                            ].as_integer()
                            == int(opt_value)
                        )
                    except ValueError:
                        stmt = basestmt.filter(
                            db.Script.conditions["application"]["feature"][
                                opt_key
                            ].as_string()
                            == opt_value
                        )

                scripts += self._driver.selectSQL(stmt)

            # now run the stmt alone to grab all generic infra- or app-only scripts
            scripts += self._driver.selectSQL(basestmt)

        # remove duplicates while preserving order, use UUID as hashable key
        # ... and convert to model
        return list({o[0].id: Script.from_orm(o[0]) for o in scripts}.values())
