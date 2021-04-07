import unittest
import jobfile_generator
import json

class test_ArgumentConverter(unittest.TestCase):
    def setUp(self):
        self.jfg = jobfile_generator.ArgumentConverter()

    def test_is_slurm_options_valid_options(self):
        self.assertTrue(self.jfg._is_slurm_options("BEGIN,TIME_LIMIT_90,FAIL,END"))
        self.assertTrue(self.jfg._is_slurm_options("BEGIN"))
        self.assertTrue(self.jfg._is_slurm_options(""))
    
    def test_is_torque_options_vaild_options(self):
        self.assertTrue(self.jfg._is_torque_options("abe"))
        self.assertTrue(self.jfg._is_torque_options("e"))
        self.assertTrue(self.jfg._is_torque_options(""))

    def test_is_slurm_options_torque(self):
        self.assertFalse(self.jfg._is_slurm_options("abe"))
    
    def test_is_torque_options_slurm(self):
        self.assertFalse(self.jfg._is_torque_options("BEGIN"))
    
    def test_is_slurm_options_invalid(self):
        self.assertFalse(self.jfg._is_slurm_options("INVALIDOPT"))
    
    def test_is_torque_options_invalid(self):
        self.assertFalse(self.jfg._is_torque_options("inv"))
    
    def test_slurm_to_torque_valid(self):
        self.assertEqual(
            self.jfg._slurm_to_torque("REQUEUE,BEGIN,END,FAIL,TIME_LIMIT"),
            "beaa"
        )
        self.assertEqual(
            self.jfg._slurm_to_torque("ALL"),
            "abe"
        )
    
    def test_torque_to_slurm_valid(self):
        self.assertEqual(
            self.jfg._torque_to_slurm("abe"),
            "FAIL,INVALID_DEPEND,TIME_LIMIT,BEGIN,END"
        )
    
    def test_convert_notifications_slurm_no_change(self):
        TEST_STRING="ALL,TIME_LIMIT_50"
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_SLURM,
                TEST_STRING),
            TEST_STRING
        )
    
    def test_convert_notifications_torque_no_change(self):
        TEST_STRING="abe"
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_TORQUE,
                TEST_STRING),
            TEST_STRING
        )
    
    def test_convert_notifications_slurm_to_torque(self):
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_TORQUE,
                "END,BEGIN,FAIL,INVALID_DEPEND,REQUEUE"
            ),
            "ebaa"
        )
    
    def test_convert_notifications_torque_to_slurm(self):
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_SLURM,
                "abe"
            ),
            "FAIL,INVALID_DEPEND,TIME_LIMIT,BEGIN,END"
        )
    
    def test_convert_notifications_torque_bad_opts(self):
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_TORQUE,
                "abef"
            ),
            "abef"
        )
    
    def test_convert_notifications_slurm_bad_opts(self):
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_SLURM,
                "ALL,INVALID_OPT"
            ),
            "ALL,INVALID_OPT"
        )
    
    def test_convert_notifications_blank(self):
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_SLURM,
                ""
            ),
            ""
        )
        self.assertEqual(
            self.jfg.convert_notifications(
                jobfile_generator.SCHEDULER_TORQUE,
                ""
            ),
            ""
        )

if __name__ == '__main__':
    unittest.main()
