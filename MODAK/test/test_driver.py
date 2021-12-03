import unittest

from sqlalchemy import select

from MODAK.db import Optimisation
from MODAK.driver import Driver


class test_driver(unittest.TestCase):
    def setUp(self):
        self.driver = Driver()

    def tearDown(self):
        pass

    def test_driver(self):
        data = self.driver.selectSQL(
            select(Optimisation.opt_dsl_code, Optimisation.app_name).where(
                Optimisation.app_name == "pytorch"
            )
        )
        self.assertEqual(data[0][1], "pytorch")
