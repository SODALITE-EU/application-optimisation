import unittest
from opt_dsl_reader import opt_dsl_reader
import json

class test_dsl_reader(unittest.TestCase):
    def setUp(self):
        print('Test opt dsl reader driver')
        dsl_file = "../test/input/tf_snow.json"
        # dsl_file = "../test/input/mpi_solver.json"
        with open(dsl_file) as json_file:
            opt_json_obj = json.load(json_file)
            print(opt_json_obj)
            self.reader = opt_dsl_reader(opt_json_obj['job'])

    def tearDown(self):
        pass

    def test_reader(self):
        self.assertEqual(self.reader.get_cpu_type(), 'x86')
        self.assertEqual(self.reader.get_acc_type(), 'nvidia')
        self.assertEqual(self.reader.get_tuner(), 'cresta')
        self.assertEqual(self.reader.get_tuner_input(),'dsl text')
        self.assertEqual(self.reader.get_app_type(),'ai_training')
        keras_opt = self.reader.get_opt_list('tensorflow')
        self.assertEqual(keras_opt['version'],'2.1')


if __name__ == '__main__':
    unittest.main()
