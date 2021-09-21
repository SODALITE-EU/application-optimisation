import unittest

from MODAK_driver import MODAK_driver


class test_MODAK_driver(unittest.TestCase):
    def setUp(self):
        self.driver = MODAK_driver()

    def tearDown(self):
        pass

    def test_driver(self):
        df = self.driver.applySQL(
            "SELECT * FROM optimisation WHERE app_name = %s", ("pytorch",)
        )
        self.assertEqual(df["app_name"][0], "pytorch")


if __name__ == "__main__":
    unittest.main()
