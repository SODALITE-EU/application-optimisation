import logging
import os
from typing import IO

from .model import Optimisation


class Tuner:
    def __init__(self, upload=True):
        """Tuner class."""
        logging.info("Initialised MODAK tuner")
        self._tune_input_file = ""
        self._tune_script_file = ""
        self._tune_input_link = ""
        self._tune_script_link = ""
        self._upload = upload
        if self._upload:
            from MODAK_gcloud import TransferData

            self._drop = TransferData()

    def encode_tune(self, optimisation: Optimisation, jobfile: IO[str]):
        logging.warning("Tuning not yet supported")
        return False

    #        logging.info("Encoding tuner")
    #        reader = OptDSLReader(opt_json_obj['job'])
    #        if not reader.enable_autotuning() or reader.enable_autotuning() is None:
    #            logging.info("Disabled tuning")
    #            return False
    #
    #        tuner = reader.get_tuner()
    #        tuner_input = reader.get_tuner_input()
    #        logging.info(tuner)
    #        logging.info(tuner_input)
    #
    #        if tuner == 'cresta':
    #            jobname = jobfile.split('.')
    #            self._tune_input_file = jobname[0] + '.tune'
    #            basename = os.path.basename(self._tune_input_file)
    #            with open(self._tune_input_file, 'w') as t:
    #                t.write(tuner_input)
    #                t.close()
    #
    #            tune_file_to = "{}/{}".format('/modak', basename)
    #            self._tune_input_link = self._drop.upload_file(
    #                file_from=self._tune_input_file, file_to=tune_file_to)
    #
    #            self._tune_script_file = jobname[0] + '_tune.sh'
    #            basescript = os.path.basename(self._tune_script_file)
    #            with open(self._tune_script_file, 'w') as f:
    #                f.write('#!/bin/bash')
    #                f.write('\n')
    #                f.write('\n')
    #                f.write('## START OF TUNER ##')
    #                f.write('\n')
    #                f.write('wget --no-check-certificate'
    #                        'https://www.dropbox.com/s/iaivd8wujhctpl5/cresta.tar.gz')
    #                f.write('\n')
    #                f.write('tar -xvf cresta.tar.gz')
    #                f.write('\n')
    #                f.write('export PATH=$PATH:$(pwd)/cresta')
    #                f.write('\n')
    #                f.write('wget --no-check-certificate ' + self._tune_input_link)
    #                f.write('\n')
    #                f.write('tune ' + basename)
    #                f.write('\n')
    #                f.write('## END OF TUNER ##')
    #                f.write('\n')
    #                f.close()
    #
    #            tune_script_to = "{}/{}".format('/modak', basescript)
    #            self._tune_script_link = self._drop.upload_file(
    #                file_from=self._tune_script_file, file_to=tune_script_to)
    #            logging.info("Successfully encoded tuner")
    #            return True
    #        else:
    #            logging.warning('unsupported tuning framework')
    #            return False

    def get_tune_link(self):
        return self._tune_script_link

    def get_tune_file(self):
        return self._tune_script_file

    def get_tune_filename(self):
        return os.path.basename(self._tune_script_file)
