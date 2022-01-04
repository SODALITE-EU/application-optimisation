from typing import Any, Dict, List, Tuple

from loguru import logger
from sqlalchemy import JSON, select
from sqlalchemy.sql.expression import Select

from . import db
from .driver import Driver
from .model import Job, Script, Target
from .model.infrastructure import InfrastructureConfiguration
from .model.storage import DefaultStorageClass


class Enforcer:
    def __init__(self, driver: Driver):
        logger.info("Initialised MODAK enforcer")
        self._driver = driver

    @staticmethod
    def _opts2stmts(basestmt: Select, opts: List[str]) -> List[Select]:
        stmts = []

        for opt in opts:
            if "version" in opt:
                logger.info("Ignore version as a optimisation")
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
            istorage = self._driver.select_sql(
                select(db.Infrastructure.configuration)
                .filter(db.Infrastructure.name == target.name)
                .filter(db.Infrastructure.configuration["storage"].isnot({}))
            )[0][0]["storage"]
        except (KeyError, IndexError):
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
        self, app_name: str, job: Job, opts: List[str]
    ) -> Tuple[List[Script], Dict[str, Any]]:
        logger.info(f"Enforcing opts {opts}")

        assert job.target, "Target must be defined"

        tenv: Dict[str, Any] = {
            "preferred_storage_location": None,
        }

        try:
            iconf = InfrastructureConfiguration(
                **self._driver.select_sql(
                    select(db.Infrastructure.configuration).filter(
                        db.Infrastructure.name == job.target.name
                    )
                )[0][0]
            )
        except IndexError:
            logger.warning(
                f"Specified infrastructure {job.target.name} not found, preferred_storage_location will be undefined"
            )
        else:
            if job.application.storage_class_pref:
                try:
                    tenv["preferred_storage_location"] = next(
                        k
                        for k, v in iconf.storage.items()
                        if v.storage_class == job.application.storage_class_pref
                    )
                except StopIteration:
                    logger.info(
                        f"Specified storage_class {job.application.storage_class_pref}"
                        f" does not exist on infrafstructure {job.target.name}, ignoring..."
                    )

            if not tenv["preferred_storage_location"]:
                try:
                    tenv["preferred_storage_location"] = next(
                        k
                        for k, _ in sorted(
                            iconf.storage.items(),
                            key=lambda pair: DefaultStorageClass(pair[1].storage_class),
                        )
                    )
                except StopIteration:
                    logger.info(
                        f"No preferred storage location found for infrastructure {job.target.name}..."
                    )

        stmts = []

        basestmt = select(db.Script)

        infrastmts = self._target2stmts(basestmt, job.target)

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
            ).filter(db.Script.conditions["application"]["feature"].is_({}))
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
            ).filter(db.Script.conditions["application"]["feature"].is_({}))
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
            for script in self._driver.select_sql(stmt)
        }

        return list(scripts.values()), tenv
