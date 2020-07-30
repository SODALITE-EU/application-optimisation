import unittest
from MODAK_driver import MODAK_driver
from mapper import mapper
from opt_dsl_reader import opt_dsl_reader
import json

class test_mapper(unittest.TestCase):
    def setUp(self):
        self.driver = MODAK_driver()
        self.m = mapper(self.driver)

    def tearDown(self):
        pass

    def test_add_opt(self):
        target_string = u'{"cpu_type":"x86","acc_type":"nvidia"}'
        opt_string = u'{"xla":true,"version":"1.1"}'
        self.driver.updateSQL("delete from optimisation where opt_dsl_code = '{}'".format('TF_PIP_XLA'))
        self.m.add_optimisation('TF_PIP_XLA', 'tensorflow', json.loads(target_string), json.loads(opt_string))
        df = self.driver.applySQL("select app_name from optimisation where opt_dsl_code = '{}'".format('TF_PIP_XLA'))
        self.assertEqual(df.size, 1)
        print(df['app_name'][0])
        self.assertEqual(df['app_name'][0], 'tensorflow')

    def test_add_container(self):
        self.driver.updateSQL("delete from mapper where opt_dsl_code = '{}'".format('TF_PIP_XLA'))
        self.m.add_container('TF_PIP_XLA', 'AI/containers/tensorflow/tensorflow_pip_xla')
        df = self.driver.applySQL("select container_file  from mapper where opt_dsl_code = '{}'".format('TF_PIP_XLA'))
        self.assertEqual(df.size, 1)
        self.assertEqual(df['container_file'][0], 'AI/containers/tensorflow/tensorflow_pip_xla')

    def test_map_container_ai(self):
        dsl_file = "../test/input/tf_snow.json"
        # dsl_file = "../test/input/mpi_solver.json"
        with open(dsl_file) as json_file:
            opt_json_obj = json.load(json_file)
            new_container = self.m.map_container(opt_json_obj)
            self.assertEqual(new_container, 'docker://modakopt/modak:tensorflow-2.1-gpu-src')

    def test_map_container_hpc(self):
        with open('../test/input/mpi_solver.json') as json_file:
            job_data = json.load(json_file)
            reader = opt_dsl_reader(job_data['job'])
            dsl_code = self.m.decode_hpc_opt(reader)
            self.assertEqual(dsl_code, 'mpich_ub1804_cuda101_mpi314_gnugprof')

    # def test_add_container(self):
    #     map_id = self.m.add_container('TF_PIP_XLA', 'AI/containers/tensorflow/tensorflow_pip_xla')
    #     df = self.driver.applySQL("select opt_dsl_code from mapper where map_id = {}".format(str(map_id)))
    #     self.assertEqual(df.count(), 1)
    #     self.assertEqual(df.select('opt_dsl_code').collect()[0][0], 'TF_PIP_XLA')

if __name__ == '__main__':
    unittest.main()
