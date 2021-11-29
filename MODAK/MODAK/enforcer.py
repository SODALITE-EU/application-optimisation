import logging
from typing import List

from sqlalchemy import JSON, select
from sqlalchemy.sql.expression import Select

from . import db
from .MODAK_driver import MODAK_driver
from .model import Script, Target


class Enforcer:
    def __init__(self, driver: MODAK_driver):
        logging.info("Initialised MODAK enforcer")
        self._driver = driver

    @staticmethod
    def _opts2stmts(basestmt: Select, opts: List[str]) -> List[Select]:
        stmts = []

        for opt in opts:
            if "version" in opt:
                logging.info("Ignore version as a optimisation")
                continue

            opt_key, opt_value = opt.split(":")

            # "unparse" the options again to be able to use them to query
            # directly the features in Script
            if opt_value.lower() == "true":
                stmts.append(
                    basestmt.filter(
                        db.Script.conditions["application"]["feature"][
                            opt_key
                        ].as_boolean()
                        == True  # noqa: E712
                    )
                )
            elif opt_value.lower() == "false":
                stmts.append(
                    basestmt.filter(
                        db.Script.conditions["application"]["feature"][
                            opt_key
                        ].as_boolean()
                        == False  # noqa: E712
                    )
                )
            else:
                try:
                    stmts.append(
                        basestmt.filter(
                            db.Script.conditions["application"]["feature"][
                                opt_key
                            ].as_integer()
                            == int(opt_value)
                        )
                    )
                except ValueError:
                    stmts.append(
                        basestmt.filter(
                            db.Script.conditions["application"]["feature"][
                                opt_key
                            ].as_string()
                            == opt_value
                        )
                    )

        return stmts

    def _target2stmts(self, basestmt: Select, target: Target) -> List[Select]:
        """Return a list of selection statements for the different infrastructure queries."""

        basestmts: List[Select] = []

        if not target.name:
            return basestmts

        # the first scripts we need are the ones matching only the infrastructure,
        # but which do not contain any storage_class condition
        basestmts += [
            basestmt.filter(
                db.Script.conditions["infrastructure"]["name"].as_string()
                == target.name
            ).filter(
                db.Script.conditions["infrastructure"]["storage_class"] == JSON.NULL
            )
        ]

        # Now we need a lookup for the given infrastructure.
        # If not found or no storage spec (atm still possible unfortunately), we're done
        try:
            istorage = self._driver.selectSQL(
                select(db.Infrastructure.configuration)
                .filter(db.Infrastructure.name == target.name)
                .filter(db.Infrastructure.configuration["storage"] != JSON.NULL)
            )[0][0]["storage"]
        except IndexError:
            return basestmts

        # now extract the available storage class definitions and build other queries matching them
        storage_classes = [config["storage_class"] for _, config in istorage.items()]

        basestmts.append(
            basestmt.filter(
                db.Script.conditions["infrastructure"]["name"] == JSON.NULL
            ).filter(
                db.Script.conditions["infrastructure"]["storage_class"]
                .as_string()
                .in_(storage_classes)
            )
        )

        basestmts.append(
            basestmt.filter(
                db.Script.conditions["infrastructure"]["name"].as_string()
                == target.name
            ).filter(
                db.Script.conditions["infrastructure"]["storage_class"] == JSON.NULL
            )
        )

        basestmts.append(
            basestmt.filter(
                db.Script.conditions["infrastructure"]["name"].as_string()
                == target.name
            ).filter(
                db.Script.conditions["infrastructure"]["storage_class"]
                .as_string()
                .in_(storage_classes)
            )
        )

        return basestmts

    def enforce_opt(
        self, app_name: str, target: Target, opts: List[str]
    ) -> List[Script]:
        logging.info(f"Enforcing opts {opts}")

        stmts = []

        basestmt = select(db.Script)

        infrastmts = self._target2stmts(basestmt, target)

        # 1. look for pure-infra scripts (e.g. conditions matching the infra but NO specific application)
        stmts += [
            s.filter(db.Script.conditions["application"] == JSON.NULL)
            for s in infrastmts
        ]

        # 2. look for application-only conditions, first the ones without any feature restrictions,
        #    then the ones with feature restrictions
        stmts += [
            basestmt.filter(
                db.Script.conditions["application"]["name"].as_string() == app_name
            ).filter(db.Script.conditions["application"]["filter"] == JSON.NULL)
        ]
        stmts += self._opts2stmts(
            basestmt.filter(
                db.Script.conditions["application"]["name"].as_string() == app_name
            ),
            opts,
        )

        # 3. repeat 2. for all infra-restricted stmts
        stmts += [
            infrastmt.filter(
                db.Script.conditions["application"]["name"].as_string() == app_name
            ).filter(db.Script.conditions["application"]["filter"] == JSON.NULL)
            for infrastmt in infrastmts
        ]
        stmts += [
            optstmt
            for infrastmt in infrastmts
            for optstmt in self._opts2stmts(
                infrastmt.filter(
                    db.Script.conditions["application"]["name"].as_string() == app_name
                ),
                opts,
            )
        ]

        # build a dict out of all scripts to automatically dedup while preserving order
        scripts = {
            script[0].id: Script.from_orm(script[0])
            for stmt in stmts
            for script in self._driver.selectSQL(stmt)
        }
        return list(scripts.values())
