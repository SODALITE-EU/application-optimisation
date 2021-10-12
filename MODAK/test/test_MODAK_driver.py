import unittest

from MODAK.MODAK_driver import MODAK_driver


class test_MODAK_driver(unittest.TestCase):
    def setUp(self):
        self.driver = MODAK_driver()

    def tearDown(self):
        pass

    def test_driver(self):
        data = self.driver.selectSQL(
            "SELECT * FROM optimisation WHERE app_name = %s", ("pytorch",)
        )
        self.assertEqual(data[0][1], "pytorch")
