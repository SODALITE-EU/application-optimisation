import json
import pathlib
import unittest

from mapper import Mapper
from MODAK_driver import MODAK_driver
from opt_dsl_reader import OptDSLReader

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
        # dsl_file = "../test/input/mpi_solver.json"
        with dsl_file.open() as json_file:
            opt_json_obj = json.load(json_file)
            new_container = self.m.map_container(opt_json_obj)
            self.assertEqual(
                new_container, "docker://modakopt/modak:tensorflow-2.1-gpu-src"
            )

    def test_map_container_hpc(self):
        with SCRIPT_DIR.joinpath("input/mpi_solver.json").open() as json_file:
            job_data = json.load(json_file)
            reader = OptDSLReader(job_data["job"])
            dsl_code = self.m.decode_hpc_opt(reader)
            self.assertEqual(dsl_code, "mpich_ub1804_cuda101_mpi314_gnugprof")

    # def test_add_container(self):
    #     map_id = self.m.add_container('TF_PIP_XLA',
    #                                   'AI/containers/tensorflow/tensorflow_pip_xla')
    #     df = self.driver.applySQL("SELECT opt_dsl_code FROM mapper WHERE map_id = %s",
    #                               (map_id, ))
    #     self.assertEqual(df.count(), 1)
    #     self.assertEqual(df.select('opt_dsl_code').collect()[0][0], 'TF_PIP_XLA')


if __name__ == "__main__":
    unittest.main()
