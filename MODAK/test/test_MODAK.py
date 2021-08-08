import io
import json
import ssl
import unittest

import wget

from MODAK import MODAK


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
        filename = wget.download(job_link, out='/tmp')
        mylist = list(io.open('../test/input/solver.sh'))
        testlist = list(io.open(filename))
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if '2020' not in mylist[i] and '##' not in mylist[i]:
                self.assertEqual(mylist[i].strip(), testlist[i].strip())

    def test_modak_ai(self):
        print('Test MODAK')
        m = MODAK()
        dsl_file = "../test/input/tf_snow.json"
        # dsl_file = "../test/input/mpi_solver.json"
        with open(dsl_file) as json_file:
            job_link = m.optimise(json.load(json_file))

        ssl._create_default_https_context = ssl._create_unverified_context
        filename = wget.download(job_link, out='/tmp')
        mylist = list(io.open('../test/input/skyline-extraction-training.sh'))
        testlist = list(io.open(filename))
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if '2020' not in mylist[i] and '##' not in mylist[i]:
                self.assertEqual(mylist[i].strip(), testlist[i].strip())

    def test_modak_resnet(self):
        print('Test MODAK')
        m = MODAK()
        dsl_file = "../test/input/tf_resnet.json"
        with open(dsl_file) as json_file:
            job_link = m.optimise(json.load(json_file))

        ssl._create_default_https_context = ssl._create_unverified_context
        filename = wget.download(job_link, out='/tmp')
        mylist = list(io.open('../test/input/resnet.sh'))
        testlist = list(io.open(filename))
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if '2020' not in mylist[i] and '##' not in mylist[i]:
                self.assertEqual(mylist[i].strip(), testlist[i].strip())

    def test_modak_xthi(self):
        print('Test MODAK')
        m = MODAK()
        dsl_file = "../test/input/mpi_test.json"
        with open(dsl_file) as json_file:
            job_link = m.optimise(json.load(json_file))

        ssl._create_default_https_context = ssl._create_unverified_context
        filename = wget.download(job_link, out='/tmp')
        mylist = list(io.open('../test/input/mpi_test.sh'))
        testlist = list(io.open(filename))
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if '2020' not in mylist[i] and '##' not in mylist[i]:
                self.assertEqual(mylist[i].strip(), testlist[i].strip())

    def test_modak_egi_xthi(self):
        print('Test MODAK')
        m = MODAK()
        dsl_file = "../test/input/mpi_test_egi.json"
        with open(dsl_file) as json_file:
            job_link = m.optimise(json.load(json_file))

        ssl._create_default_https_context = ssl._create_unverified_context
        filename = wget.download(job_link, out='/tmp')
        mylist = list(io.open('../test/input/mpi_test_egi.sh'))
        testlist = list(io.open(filename))
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if '2020' not in mylist[i] and '##' not in mylist[i]:
                self.assertEqual(mylist[i].strip(), testlist[i].strip())


if __name__ == '__main__':
    unittest.main()
