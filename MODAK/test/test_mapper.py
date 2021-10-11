import json
import pathlib
import unittest
from unittest.mock import patch

from MODAK.mapper import Mapper
from MODAK.MODAK_driver import MODAK_driver
from MODAK.model import JobModel
from MODAK.settings import Settings

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


class test_mapper(unittest.TestCase):
    def setUp(self):
        self.driver = MODAK_driver()
        self.m = Mapper(self.driver)

    def tearDown(self):
        pass

    def test_add_opt(self):
        target_string = '{"cpu_type":"x86","acc_type":"nvidia"}'
        opt_string = '{"xla":true,"version":"1.1"}'
        self.driver.updateSQL(
            "DELETE FROM mapper WHERE opt_dsl_code = %s", ("TF_PIP_XLA",)
        )
        self.driver.updateSQL(
            "DELETE FROM optimisation WHERE opt_dsl_code = %s", ("TF_PIP_XLA",)
        )
        self.m.add_optimisation(
            "TF_PIP_XLA",
            "tensorflow",
            json.loads(target_string),
            json.loads(opt_string),
        )
        df = self.driver.applySQL(
            "SELECT app_name FROM optimisation WHERE opt_dsl_code = %s", ("TF_PIP_XLA",)
        )
        self.assertEqual(df.size, 1)
        print(df["app_name"][0])
        self.assertEqual(df["app_name"][0], "tensorflow")

    def test_add_container(self):
        self.driver.updateSQL(
            "DELETE FROM mapper WHERE opt_dsl_code = %s", ("TF_PIP_XLA",)
        )
        self.m.add_container(
            "TF_PIP_XLA", "AI/containers/tensorflow/tensorflow_pip_xla"
        )
        df = self.driver.applySQL(
            "SELECT container_file FROM mapper WHERE opt_dsl_code = %s", ("TF_PIP_XLA",)
        )
        self.assertEqual(df.size, 1)
        self.assertEqual(
            df["container_file"][0], "AI/containers/tensorflow/tensorflow_pip_xla"
        )

    def test_map_container_ai(self):
        dsl_file = SCRIPT_DIR / "input" / "tf_snow.json"

        model = JobModel.parse_raw(dsl_file.read_text())
        new_container = self.m.map_container(model.job.optimisation, model.job.target)
        self.assertEqual(
            new_container, "docker.io://modakopt/modak:tensorflow-2.1-gpu-src"
        )

    def test_map_container_hpc(self):
        model = JobModel.parse_raw(
            SCRIPT_DIR.joinpath("input/mpi_solver.json").read_text()
        )
        assert model.job.optimisation

        dsl_code = self.m.decode_hpc_opt(model.job.optimisation)
        self.assertEqual(dsl_code, "mpich_ub1804_cuda101_mpi314_gnugprof")

    def test_map_container_aliased(self):
        dsl_file = SCRIPT_DIR / "input" / "tf_snow.json"

        with patch.object(Settings, "IMAGE_HUB_ALIASES", {"docker": "docker.invalid"}):
            model = JobModel.parse_raw(dsl_file.read_text())
            new_container = self.m.map_container(
                model.job.optimisation, model.job.target
            )
            self.assertEqual(
                new_container,
                "docker.invalid://modakopt/modak:tensorflow-2.1-gpu-src",
            )

    # def test_add_container(self):
    #     map_id = self.m.add_container('TF_PIP_XLA',
    #                                   'AI/containers/tensorflow/tensorflow_pip_xla')
    #     df = self.driver.applySQL("SELECT opt_dsl_code FROM mapper WHERE map_id = %s",
    #                               (map_id, ))
    #     self.assertEqual(df.count(), 1)
    #     self.assertEqual(df.select('opt_dsl_code').collect()[0][0], 'TF_PIP_XLA')
