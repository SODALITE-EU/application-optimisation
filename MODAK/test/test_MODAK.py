from copy import deepcopy
import json
import pathlib
import unittest
from unittest.mock import patch

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
        dsl_file = SCRIPT_DIR / "input" / "mpi_solver.json"
        with dsl_file.open() as json_file:
            job_link = m.optimise(json.load(json_file))

        with SCRIPT_DIR.joinpath("input/solver.sh").open() as fhandle:
            mylist = list(fhandle)
        with open(job_link) as fhandle:
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

        with SCRIPT_DIR.joinpath(
            "input/skyline-extraction-training.sh"
        ).open() as fhandle:
            mylist = list(fhandle)
        with open(job_link[0]) as fhandle:
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

        with SCRIPT_DIR.joinpath("input/resnet.sh").open() as fhandle:
            mylist = list(fhandle)
        with open(job_link[0]) as fhandle:
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

        with SCRIPT_DIR.joinpath("input/mpi_test.sh").open() as fhandle:
            mylist = list(fhandle)
        with open(job_link) as fhandle:
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

        with SCRIPT_DIR.joinpath("input/mpi_test_egi.sh").open() as fhandle:
            mylist = list(fhandle)
        with open(job_link) as fhandle:
            testlist = list(fhandle)

        self.assertEqual(len(mylist), len(testlist))

        for i in range(0, (len(mylist))):
            if "2020" not in mylist[i] and "##" not in mylist[i]:
                self.assertEqual(mylist[i].strip(), testlist[i].strip())

class test_MODAK_get_buildjob(unittest.TestCase):
    def test_empty(self):
        """Tests an empty job being sent"""
        with patch("MODAK.MODAK.get_optimisation") as p1:
            expected_return = ""

            return_value = MODAK().get_buildjob({})

            self.assertEqual(expected_return, return_value)

    def test_minimal_no_build(self):
        """
        Tests a minimal job (with no build section)
        """
        with patch("MODAK.MODAK.get_optimisation") as p1:
            injson = {
                "job": {
                    "job_name": "test_job",
                    "node_count": 4,
                    "process_per_node": 2,
                    "standard_output_file": "test.out",
                    "standard_error_file": "test.err",
                    "combine_stdout_stderr": "true",
                }
            }
            expected_return = ""
            return_value = MODAK().get_buildjob(injson)

            self.assertEqual(expected_return, return_value)

    def test_minimal_build(self):
        """
        Tests a minimal job (with a build section)
        """
        with patch("MODAK.MODAK.get_optimisation") as p1:
            expected_return = """#! /bin/sh\n# some build script"""
            p1.return_value=(None, expected_return)
            injson = {
                "job": {
                    "job_options": {
                        "job_name": "test_job",
                        "node_count": 4,
                        "process_count_per_node": 2,
                        "standard_output_file": "test.out",
                        "standard_error_file": "test.err",
                        "combine_stdout_stderr": "true",
                    },
                    "application": {
                        "build": {
                            "build_command": "sleep 1",
                            "src": "git://example/git/repo.git"
                        }
                    }
                }
            }
            return_value = MODAK().get_buildjob(injson)

            calljson = deepcopy(injson)
            calljson["job"]["job_options"]["job_name"] = "test_job_build"
            calljson["job"]["job_options"]["node_count"] = 1
            calljson["job"]["job_options"]["process_count_per_node"] = 1
            calljson["job"]["job_options"]["standard_output_file"] = "build-test.out"
            calljson["job"]["job_options"]["standard_error_file"] = "build-test.err"
            calljson["job"]["application"]["executable"] = "git clone git://example/git/repo.git\nsleep 1"
            self.assertEqual(expected_return, return_value)
            p1.assert_called_once_with(calljson)
    
    def test_copy_environment(self):
        """
        Tests a minimal job (with a build section)
        """
        with patch("MODAK.MODAK.get_optimisation") as p1:
            expected_return = """#! /bin/sh\n# some build script"""
            p1.return_value=(None, expected_return)
            injson = {
                "job": {
                    "job_options": {
                        "job_name": "test_job",
                        "node_count": 4,
                        "process_count_per_node": 2,
                        "standard_output_file": "test.out",
                        "standard_error_file": "test.err",
                        "combine_stdout_stderr": "true",
                        "copy_environment": "false"
                    },
                    "application": {
                        "build": {
                            "build_command": "sleep 1",
                            "src": "git://example/git/repo.git"
                        }
                    }
                }
            }
            return_value = MODAK().get_buildjob(injson)

            self.assertEqual("false", p1.call_args[0][0]["job"]["job_options"]["copy_environment"])

    def test_non_git_src(self):
        """
        Tests a minimal job (with a build section)
        """
        with patch("MODAK.MODAK.get_optimisation") as p1:
            expected_return = """#! /bin/sh\n# some build script"""
            p1.return_value=(None, expected_return)
            injson = {
                "job": {
                    "job_options": {
                        "job_name": "test_job",
                        "node_count": 4,
                        "process_count_per_node": 2,
                        "standard_output_file": "test.out",
                        "standard_error_file": "test.err",
                        "combine_stdout_stderr": "true",
                        "copy_environment": "false"
                    },
                    "application": {
                        "build": {
                            "build_command": "sleep 1",
                            "src": "http://example/tar.gz"
                        }
                    }
                }
            }
            return_value = MODAK().get_buildjob(injson)
            
            self.assertEqual("wget --no-check-certificate http://example/tar.gz\nsleep 1", p1.call_args[0][0]["job"]["application"]["executable"])

    def test_build_parallelism(self):
        """
        Tests a minimal job (with a build section)
        """
        with patch("MODAK.MODAK.get_optimisation") as p1:
            expected_return = """#! /bin/sh\n# some build script"""
            p1.return_value=(None, expected_return)
            injson = {
                "job": {
                    "job_options": {
                        "job_name": "test_job",
                        "node_count": 4,
                        "process_count_per_node": 2,
                        "standard_output_file": "test.out",
                        "standard_error_file": "test.err",
                        "combine_stdout_stderr": "true",
                        "copy_environment": "false"
                    },
                    "application": {
                        "build": {
                            "build_command": "sleep {{BUILD_PARALLELISM }}",
                            "src": "http://example/tar.gz",
                            "build_parallelism": 4,
                        }
                    }
                }
            }
            return_value = MODAK().get_buildjob(injson)
            
            self.assertEqual("wget --no-check-certificate http://example/tar.gz\nsleep 4", p1.call_args[0][0]["job"]["application"]["executable"])

if __name__ == "__main__":
    unittest.main()
