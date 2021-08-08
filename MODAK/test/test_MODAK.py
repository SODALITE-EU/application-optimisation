import json
import pathlib
import ssl
import unittest

import wget

from MODAK import MODAK

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


class test_MODAK(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_modak_hpc(self):
        print("Test MODAK")
        m = MODAK()
        ssl._create_default_https_context = ssl._create_unverified_context
        dsl_file = SCRIPT_DIR / "input" / "mpi_solver.json"
        with dsl_file.open() as json_file:
            job_link = m.optimise(json.load(json_file))
        filename = wget.download(job_link, out="/tmp")
        with SCRIPT_DIR.joinpath("input/solver.sh").open() as fhandle:
            mylist = list(fhandle)
        with open(filename) as fhandle:
            testlist = list(fhandle)
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if "2020" not in mylist[i] and "##" not in mylist[i]:
                self.assertEqual(mylist[i].strip(), testlist[i].strip())

    def test_modak_ai(self):
        print("Test MODAK")
        m = MODAK()
        dsl_file = SCRIPT_DIR / "input" / "tf_snow.json"
        # dsl_file = "../test/input/mpi_solver.json"
        with dsl_file.open() as json_file:
            job_link = m.optimise(json.load(json_file))

        ssl._create_default_https_context = ssl._create_unverified_context
        filename = wget.download(job_link, out="/tmp")
        with SCRIPT_DIR.joinpath("input/skyline-extraction-training.sh") as fhandle:
            mylist = list(fhandle)
        with open(filename) as fhandle:
            testlist = list(fhandle)
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if "2020" not in mylist[i] and "##" not in mylist[i]:
                self.assertEqual(mylist[i].strip(), testlist[i].strip())

    def test_modak_resnet(self):
        print("Test MODAK")
        m = MODAK()
        dsl_file = SCRIPT_DIR / "input" / "tf_resnet.json"
        with dsl_file.open() as json_file:
            job_link = m.optimise(json.load(json_file))

        ssl._create_default_https_context = ssl._create_unverified_context
        filename = wget.download(job_link, out="/tmp")
        with SCRIPT_DIR.joinpath("input/resnet.sh") as fhandle:
            mylist = list(fhandle)
        with open(filename) as fhandle:
            testlist = list(fhandle)
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if "2020" not in mylist[i] and "##" not in mylist[i]:
                self.assertEqual(mylist[i].strip(), testlist[i].strip())

    def test_modak_xthi(self):
        print("Test MODAK")
        m = MODAK()
        dsl_file = SCRIPT_DIR / "input" / "mpi_test.json"
        with dsl_file.open() as json_file:
            job_link = m.optimise(json.load(json_file))

        ssl._create_default_https_context = ssl._create_unverified_context
        filename = wget.download(job_link, out="/tmp")
        with SCRIPT_DIR.joinpath("input/mpi_test.sh") as fhandle:
            mylist = list(fhandle)
        with open(filename) as fhandle:
            testlist = list(fhandle)
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if "2020" not in mylist[i] and "##" not in mylist[i]:
                self.assertEqual(mylist[i].strip(), testlist[i].strip())

    def test_modak_egi_xthi(self):
        print("Test MODAK")
        m = MODAK()
        dsl_file = SCRIPT_DIR / "input" / "mpi_test_egi.json"
        with dsl_file.open() as json_file:
            job_link = m.optimise(json.load(json_file))

        ssl._create_default_https_context = ssl._create_unverified_context
        filename = wget.download(job_link, out="/tmp")
        with SCRIPT_DIR.joinpath("input/mpi_test_egi.sh") as fhandle:
            mylist = list(fhandle)
        with open(filename) as fhandle:
            testlist = list(fhandle)
        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if "2020" not in mylist[i] and "##" not in mylist[i]:
                self.assertEqual(mylist[i].strip(), testlist[i].strip())


if __name__ == "__main__":
    unittest.main()
