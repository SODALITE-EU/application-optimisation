import unittest
from MODAK import MODAK
import json
import wget
import ssl
import io

class test_MODAK(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_modak_hpc(self):
        print('Test MODAK')
        m = MODAK()
        ssl._create_default_https_context = ssl._create_unverified_context
        dsl_file = "../test/input/mpi_solver.json"
        with open(dsl_file) as json_file:
            job_link = m.optimise(json.load(json_file))
        filename = wget.download(job_link, out='../test/input/')
        mylist = list(io.open('../test/input/solver.sh'))
        testlist = list(io.open(filename))
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if '2020' not in mylist[i]:
                self.assertEqual(mylist[i], testlist[i])


    def test_modak_ai(self):
        print('Test MODAK')
        m = MODAK()
        dsl_file = "../test/input/tf_snow.json"
        # dsl_file = "../test/input/mpi_solver.json"
        with open(dsl_file) as json_file:
            job_link = m.optimise(json.load(json_file))

        ssl._create_default_https_context = ssl._create_unverified_context
        filename = wget.download(job_link, out='../test/input/')
        mylist = list(io.open('../test/input/skyline-extraction-training.sh'))
        testlist = list(io.open(filename))
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0,(len(mylist))):
            if '2020' not in mylist[i]:
                self.assertEqual(mylist[i], testlist[i])



if __name__ == '__main__':
    unittest.main()
