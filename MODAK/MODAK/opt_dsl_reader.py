import json


class OptDSLReader:
    def __init__(self, opt_dsl_obj):
        self.opt_node = opt_dsl_obj.get("optimisation", {})

    def optimisations_exist(self):
        return bool(self.opt_node)

    def enable_opt_build(self):
        return self.opt_node.get("enable_opt_build")

    def enable_autotuning(self):
        return bool(self.opt_node.get("enable_autotuning", False))

    def get_app_type(self):
        return self.opt_node.get("app_type")

    def get_opt_build(self):
        if self.enable_opt_build():
            return {"cpu_type": self.get_cpu_type(), "acc_type": self.get_acc_type()}
            # return self.opt_node.get('opt_build')

    def get_cpu_type(self):
        if self.enable_opt_build():
            cpu_type = self.opt_node.get("opt_build").get("cpu_type")
            return cpu_type

    def get_acc_type(self):
        if self.enable_opt_build():
            acc_type = self.opt_node.get("opt_build").get("acc_type")
            return (
                ""
                if (acc_type is None or acc_type == "None" or acc_type == "none")
                else acc_type
            )

    def get_tuner(self):
        if self.enable_autotuning():
            tuner = self.opt_node.get("autotuning").get("tuner")
            return tuner

    def get_tuner_input(self):
        if self.enable_autotuning():
            tuner = self.opt_node.get("autotuning").get("input")
            return tuner

    def get_app_config(self):
        app_type = self.opt_node.get("app_type")
        return self.opt_node.get("app_type-" + app_type).get("config")

    def get_app_data(self):
        app_type = self.opt_node.get("app_type")
        return self.opt_node.get("app_type-" + app_type).get("data")

    def get_app_etl(self):
        app_type = self.opt_node.get("app_type")
        return self.opt_node.get("app_type-" + app_type).get("data").get("etl")

    def get_opt_list(self, app):
        app_type = self.opt_node.get("app_type")
        if app_type == "ai_training":
            return self.opt_node.get("app_type-" + app_type).get("ai_framework-" + app)
        if app_type == "hpc":
            return self.opt_node.get("app_type-" + app_type).get(
                "parallelisation-" + app
            )

    def get_opts_list(self):
        opts = []
        if self.optimisations_exist():
            app_type = self.opt_node.get("app_type")
            config = self.get_app_config()
            if app_type == "ai_training":
                app = config["ai_framework"]
                opts = self.opt_node.get("app_type-" + app_type).get(
                    "ai_framework-" + app
                )
            elif app_type == "hpc":
                app = config["parallelisation"]
                opts = self.opt_node.get("app_type-" + app_type).get(
                    "parallelisation-" + app
                )
                if "library" in opts:
                    opts.pop("library")
        return opts


def main():
    print("Test opt dsl reader driver")
    dsl_file = "../test/mpi_solver.json"
    with open(dsl_file) as json_file:
        obj = json.load(json_file)
        reader = OptDSLReader(obj["job"])
        print(reader.get_cpu_type())
        print(reader.get_acc_type())
        print(reader.get_tuner())
        print(reader.get_tuner_input())
        print(reader.get_app_type())
        print(reader.get_app_config())
        print(reader.get_app_data())
        print(reader.get_app_etl())
        keras_opt = reader.get_opt_list("tensorflow")
        print(keras_opt)


if __name__ == "__main__":
    main()
