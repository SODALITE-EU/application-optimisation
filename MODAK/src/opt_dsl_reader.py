import json

class opt_dsl_reader():

    def __init__(self, opt_dsl_obj):
        self.opt_node = opt_dsl_obj.get('optimisation')

    def enable_opt_build(self):
        return self.opt_node.get('enable_opt_build')

    def enable_autotuning(self):
        return self.opt_node.get('enable_autotuning')

    def get_app_type(self):
        return self.opt_node.get('app_type')

    def get_app_name(self):
        return self.opt_node.get('app_name')

    def get_opt_build(self):
        if self.enable_opt_build():
            return self.opt_node.get('arch_build')

    def get_cpu_type(self):
        if self.enable_opt_build():
            cpu_type = self.opt_node.get('arch_build').get('cpu_type')
            return cpu_type

    def get_acc_type(self):
        if self.enable_opt_build():
            acc_type = self.opt_node.get('arch_build').get('acc_type')
            return acc_type

    def get_tuner(self):
        if self.enable_autotuning():
            tuner = self.opt_node.get('autotuning').get('tuner')
            return tuner

    def get_tuner_input(self):
        if self.enable_autotuning():
            tuner = self.opt_node.get('autotuning').get('input')
            return tuner

    def get_app_type(self):
        return self.opt_node.get('app_type')

    def get_app_config(self):
        return self.opt_node.get('app_config')

    def get_app_data(self):
        return self.opt_node.get('app_data')

    def get_app_etl(self):
        return self.opt_node.get('app_data')

    def get_opt_list(self):
        return self.opt_node.get('app_opt')

    def get_app_build(self):
        return self.opt_node.get('app_build')

def main():
    print('Test opt dsl reader driver')
    dsl_file = "../test/mpi_solver.json"
    with open(dsl_file) as json_file:
        obj = json.load(json_file)
        reader = opt_dsl_reader(obj['job'])
        print(reader.get_cpu_type())
        print(reader.get_acc_type())
        print(reader.get_tuner())
        print(reader.get_tuner_input())
        print(reader.get_app_type())
        print(reader.get_app_config())
        print(reader.get_app_data())
        print(reader.get_app_etl())
        keras_opt = reader.get_opt_list('tensorflow')
        print(keras_opt)

if __name__ == '__main__':
    main()



