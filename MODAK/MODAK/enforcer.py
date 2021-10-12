import logging
from collections import namedtuple
from typing import List

from .MODAK_driver import MODAK_driver

EnforcerEntry = namedtuple("EnforcerEntry", ["script_name", "script_loc", "stage"])


class Enforcer:
    def __init__(self, driver: MODAK_driver):
        logging.info("Initialised MODAK enforcer")
        self._driver = driver

    def enforce_opt(self, opts: List[str]) -> List[EnforcerEntry]:
        logging.info(f"Enforcing opts {opts}")
        # TODO: do we enforce only one optimisation?
        # TODO: redo if it is the case
        data = []
        for opt in opts:
            if "version" in opt:
                logging.info("Ignore version as a optimisation")
                continue

            opt_key, opt_value = opt.split(":")

            if "true" in opt_value:
                oneopt_data = self._driver.selectSQL(
                    "SELECT script_name, script_loc, stage FROM optscript"
                    " WHERE opt_code = %s",
                    (opt_key,),
                )
                data += [EnforcerEntry(*e) for e in oneopt_data]
        return data
