import unittest
from MODAK_driver import MODAK_driver
from settings import settings

class test_MODAK_driver(unittest.TestCase):

    def setUp(self):
        self.driver = MODAK_driver()

    def tearDown(self):
        pass

    def test_driver(self):
        if settings.MODE == 'test':
            self.assertEqual(self.driver.dbname, 'test_iac_model')
        else:
            self.assertEqual(self.driver.dbname, 'iac_model')
        df = self.driver.applySQL("select * from optimisation where app_name = 'pytorch'")
        self.assertEqual(df['app_name'][0], 'pytorch')


if __name__ == '__main__':
    unittest.main()
