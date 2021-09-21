import tempfile
import unittest

import pytest

import jobfile_generator

TEST_STRING = b"""## OPTSCRIPT here ##"""


class test_mapper(unittest.TestCase):
    def setUp(self):
        self.outfile = tempfile.NamedTemporaryFile()
        self.optscript = tempfile.NamedTemporaryFile()
        self.optscript.file.write(TEST_STRING)
        self.optscript.file.flush()
        self.jg = jobfile_generator.JobfileGenerator(
            {
                "job": {
                    "job_options": {},
                    "application": {},
                    "optimization": {},
                    "target": {"job_scheduler_type": "torque", "name": "hlrs_testbed"},
                }
            },
            self.outfile.name,
        )

    def test_add_optscript(self):
        self.jg.add_optscript(self.optscript.name, f"file://{self.optscript.name}")

        # If everything worked correctly, our test line should have been
        # inserted into the output file by attempting to add an option script.
        self.outfile.file.seek(0)
        self.assertTrue(TEST_STRING in self.outfile.file.readlines())

    def test_add_optscript_bad_url(self):
        with pytest.raises(Exception):
            self.jg.add_optscript(self.optscript.name, f"asdf://{self.optscript.name}")


class test_ArgumentConverter(unittest.TestCase):
    def setUp(self):
        self.jfg = jobfile_generator.ArgumentConverter()

    def test_is_slurm_options_valid_options(self):
        self.assertTrue(self.jfg._is_slurm_options("BEGIN,TIME_LIMIT_90,FAIL,END"))
        self.assertTrue(self.jfg._is_slurm_options("BEGIN"))
        self.assertTrue(self.jfg._is_slurm_options("NONE"))

    def test_is_torque_options_vaild_options(self):
        self.assertTrue(self.jfg._is_torque_options("abe"))
        self.assertTrue(self.jfg._is_torque_options("e"))
        self.assertTrue(self.jfg._is_torque_options("p"))
        self.assertTrue(self.jfg._is_torque_options("f"))

    def test_is_slurm_options_torque(self):
        self.assertFalse(self.jfg._is_slurm_options("abe"))

    def test_is_torque_options_slurm(self):
        self.assertFalse(self.jfg._is_torque_options("BEGIN"))

    def test_is_slurm_options_invalid(self):
        self.assertFalse(self.jfg._is_slurm_options("INVALIDOPT"))
        self.assertFalse(self.jfg._is_slurm_options("NONE,ALL"))

    def test_is_torque_options_invalid(self):
        self.assertFalse(self.jfg._is_torque_options("inv"))
        self.assertFalse(self.jfg._is_torque_options("na"))
        self.assertFalse(self.jfg._is_torque_options("pa"))

    def test_slurm_to_torque_valid(self):
        self.assertEqual(
            self.jfg._slurm_to_torque("REQUEUE,BEGIN,END,FAIL,TIME_LIMIT"), "befa"
        )
        self.assertEqual(self.jfg._slurm_to_torque("ALL"), "abef")
        self.assertEqual(self.jfg._slurm_to_torque("NONE"), "n")

    def test_torque_to_slurm_valid(self):
        self.assertEqual(
            self.jfg._torque_to_slurm("abe"), "FAIL,INVALID_DEPEND,TIME_LIMIT,BEGIN,END"
        )
        self.assertEqual(self.jfg._torque_to_slurm("n"), "FAIL")
        self.assertEqual(self.jfg._torque_to_slurm("p"), "NONE")

    def test_convert_notifications_slurm_no_change(self):
        TEST_STRING = "ALL,TIME_LIMIT_50"
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_SLURM, TEST_STRING
            ),
            TEST_STRING,
        )

    def test_convert_notifications_torque_no_change(self):
        TEST_STRING = "abe"
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_TORQUE, TEST_STRING
            ),
            TEST_STRING,
        )

    def test_convert_notifications_slurm_to_torque(self):
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_TORQUE,
                "END,BEGIN,FAIL,INVALID_DEPEND,REQUEUE",
            ),
            "ebfa",
        )

    def test_convert_notifications_torque_to_slurm(self):
        self.assertEqual(
            self.jfg.convert_notifications(jobfile_generator.SCHEDULER_SLURM, "abe"),
            "FAIL,INVALID_DEPEND,TIME_LIMIT,BEGIN,END",
        )

    def test_convert_notifications_torque_bad_opts(self):
        self.assertEqual(
            self.jfg.convert_notifications(jobfile_generator.SCHEDULER_TORQUE, "abef"),
            "abef",
        )

    def test_convert_notifications_slurm_bad_opts(self):
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_SLURM, "ALL,INVALID_OPT"
            ),
            "ALL",  # default
        )

    def test_convert_notifications_blank(self):
        self.assertEqual(
            self.jfg.convert_notifications(jobfile_generator.SCHEDULER_SLURM, ""), "ALL"
        )
        self.assertEqual(
            self.jfg.convert_notifications(jobfile_generator.SCHEDULER_TORQUE, ""),
            "abe",
        )


if __name__ == "__main__":
    unittest.main()
