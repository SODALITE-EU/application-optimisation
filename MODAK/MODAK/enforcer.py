import logging

from .MODAK_driver import MODAK_driver


class Enforcer:
    def __init__(self, driver: MODAK_driver):
        logging.info("Initialised MODAK enforcer")
        self._driver = driver

    def enforce_opt(self, opts):
        logging.info(f"Enforcing opts {opts}")
        # TODO: do we enforce only one optimisation?
        # TODO: redo if it is the case
        dfs = []
        for opt in opts:
            if "version" in opt:
                logging.info("Ignore version as a optimisation")
                continue

            opt_key, opt_value = opt.split(":")

            if "true" in opt_value:
                df = self._driver.applySQL(
                    "SELECT script_name, script_loc, stage FROM optscript"
                    " WHERE opt_code = %s",
                    (opt_key,),
                )
                dfs.append(df)
        return dfs
