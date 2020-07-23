import unittest
from MODAK import MODAK
import io
import json
import filecmp

class test_MODAK(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_modak(self):
        print('Test MODAK')
        m = MODAK()
        dsl_file = "../test/input/tf_snow.json"
        # dsl_file = "../test/input/mpi_solver.json"
        with open(dsl_file) as json_file:
            job_link = m.optimise(json.load(json_file))

        # self.assertListEqual(
        #      list(io.open('../output/skyline-extraction-training_job.sh')),
        #      list(io.open('../test/test_skyline-extraction-training_job.sh')))

        # self.assertTrue(filecmp.cmp('../test/skyline-extraction-training_job.sh', '../test/torque.pbs', shallow=False))


if __name__ == '__main__':
    unittest.main()
