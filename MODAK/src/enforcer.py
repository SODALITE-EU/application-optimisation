import os,errno
import logging
from MODAK_driver import MODAK_driver
import json
from opt_dsl_reader import opt_dsl_reader

class enforcer():

    def __init__(self, __driver):
        logging.info("Initialised MODAK enforcer")
        self.driver = __driver

    def enforce_opt(self, opts):
        logging.info('Enforcing opts ' + str(opts))
        # TODO: do we enforce only one optimisation?
        # TODO: redo if it is the case
        dfs = []
        for opt in opts:
            if 'version' in opt:
                logging.info("Ignore version as a optimisation")
            else:
                opt_code = opt.split(':')
                if 'true' in opt_code[1]:
                    df = self.driver.applySQL("select script_name, script_loc, stage from optscript "
                                         "where opt_code = '{}' ". format(opt_code[0]))
                    dfs.append(df)
        return dfs



def main():
    driver = MODAK_driver()
    e = enforcer(driver)
    print('Test enforcer main')
    opts = ['version:2.1', 'xla:true']
    df = {}
    df = e.enforce_opt(opts)
    print(df.shape[0])
    for i in range(0, df.shape[0]):
        print(df['script_name'][i])
        print(df['script_loc'][i])

if __name__ == '__main__':
    main()
