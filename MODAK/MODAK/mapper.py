import json
import logging
from typing import List, Mapping

from .MODAK_driver import MODAK_driver
from .opt_dsl_reader import OptDSLReader
from .settings import Settings


class Mapper:
    def __init__(self, driver: MODAK_driver):
        logging.info("Initialised MODAK mapper")
        self._driver = driver
        self._opts: List[str] = []

    def map_container(self, opt_json_obj):
        logging.info("Mapping to optimal container")
        logging.info(str(opt_json_obj.get("job").get("optimisation")))
        reader = OptDSLReader(opt_json_obj["job"])
        app_type = reader.get_app_type()
        dsl_code = None

        try:
            self._opts.append(f"{opt_json_obj['job']['target']['name'].strip()}:true")
        except KeyError:
            pass

        if app_type == "ai_training":
            logging.info("Decoding AI training application")
            dsl_code = self.decode_ai_training_opt(reader)
        if app_type == "hpc":
            logging.info("Decoding HPC application")
            dsl_code = self.decode_hpc_opt(reader)
        else:
            logging.warning("Unknown application type")

        logging.info(f"Decoded opt code: {dsl_code}")

        return self.get_container(dsl_code)

    def add_optcontainer(self, map_obj):
        logging.info(f"Adding optimal container {map_obj}")
        self.add_optimisation(
            map_obj.get("name"),
            map_obj.get("app_name"),
            map_obj.get("build"),
            map_obj.get("optimisation"),
        )
        self.add_container(
            map_obj.get("name"),
            map_obj.get("container_file"),
            map_obj.get("image_hub"),
            map_obj.get("image_type"),
            map_obj.get("src"),
        )

    def add_container(
        self,
        opt_dsl_code: str,
        container_file: str,
        image_hub: str = "docker",
        image_type: str = "docker",
        src: str = "",
    ):
        logging.info("Adding container to mapper ")
        stmt = """
            INSERT INTO `mapper`
             (`map_id`, `opt_dsl_code`, `container_file`, `image_type`, `image_hub`, `src`)
             VALUES
             (NULL, %(opt_dsl_code)s, %(container_file)s,
              %(image_type)s, %(image_hub)s, %(src)s)
            """

        logging.info(
            stmt
            % {
                "opt_dsl_code": opt_dsl_code,
                "container_file": container_file,
                "image_type": image_type,
                "image_hub": image_hub,
                "src": src,
            }
        )
        self._driver.updateSQL(
            stmt,
            {
                "opt_dsl_code": opt_dsl_code,
                "container_file": container_file,
                "image_type": image_type,
                "image_hub": image_hub,
                "src": src,
            },
        )
        return True

    def add_optimisation(
        self, opt_dsl_code: str, app_name: str, target: Mapping, optimisation: Mapping
    ):
        logging.info("Adding DSL code to Optimisation ")

        target_str = ",".join(
            f"{str(key).lower()}:{str(value).lower()}" for key, value in target.items()
        )
        opt_str = ",".join(
            f"{str(key).lower()}:{str(value).lower()}"
            for key, value in optimisation.items()
        )

        logging.info(f"Target string: '{target_str}'")
        logging.info(f"Opt string: '{opt_str}'")

        stmt = """
            INSERT INTO `optimisation`
              (`opt_dsl_code`, `app_name`, `target`, `optimisation`, `version`)
            VALUES
              (%(opt_dsl_code)s, %(app_name)s, %(target)s, %(optimisation)s, %(version)s)
            """

        logging.info(
            stmt.format(
                opt_dsl_code=opt_dsl_code,
                app_name=app_name,
                target=target_str,
                optimisation=opt_str,
                version="",
            )
        )
        self._driver.updateSQL(
            stmt,
            {
                "opt_dsl_code": opt_dsl_code,
                "app_name": app_name,
                "target": target_str,
                "optimisation": opt_str,
                "version": "",
            },
        )
        return True

    def get_container(self, opt_dsl_code: str):
        logging.info(f"Get container for opt code: {opt_dsl_code}")

        stmt = (
            "SELECT container_file, image_type, image_hub FROM mapper"
            " WHERE opt_dsl_code=%s ORDER BY map_id desc limit 1"
        )
        df = self._driver.applySQL(stmt, (opt_dsl_code,))

        if df.size > 0:
            container_file = df["container_file"][0]
            image_hub = df["image_hub"][0]

            # replace the image hub with the alias if available
            image_hub = Settings.IMAGE_HUB_ALIASES.get(image_hub, image_hub)

            container_link = f"{image_hub}://{container_file}"
            logging.info(f"Container link: {container_link}")
            return container_link

        logging.warning("No optimal container found")
        return None

    def get_json_nodes(self, target_str: str):
        target_str = (
            target_str.replace("{", "")
            .replace("}", "")
            .replace('"', "")
            .replace("'", "")
            .replace("\\", "")
            .replace(" ", "")
        )

        if target_str == "":
            return [""]

        target_nodes = target_str.split(",")
        return target_nodes

    def decode_hpc_opt(self, opt_dsl: OptDSLReader):
        logging.info("Decoding HPC optimisation")
        app_type = opt_dsl.get_app_type()
        if not app_type == "hpc":
            return ""
        if opt_dsl.enable_opt_build():
            target = opt_dsl.get_opt_build()
        else:
            target = '{"cpu_type":"none","acc_type":"none"}'
            target = "{}"

        config = opt_dsl.get_app_config()
        logging.info("Config section: " + str(config))
        parallel = config["parallelisation"]
        logging.info(f"Parallelisation {parallel}")
        opts = opt_dsl.get_opt_list(parallel)
        logging.info(f"optimisations: {opts}")
        app_name = opts.get("library")

        # TODO: this changes original values from the request, but
        #       having this still in for the next call enables an artificial constraint
        opts.pop("library", None)

        sqlstr = "SELECT opt_dsl_code FROM optimisation WHERE app_name = %(app_name)s"

        target_nodes = self.get_json_nodes(json.dumps(target))
        for t in target_nodes:
            targetstr = f" AND target LIKE '%{t}%'"
            sqlstr += targetstr
            logging.info(f"Adding target query '{targetstr}'")

        if opt_dsl.enable_opt_build():
            sqlstr += " AND target LIKE '%enable_opt_build:true%'"
        else:
            sqlstr += " AND target LIKE '%enable_opt_build:false%'"

        opt_nodes = self.get_json_nodes(json.dumps(opts))
        for t in opt_nodes:
            optstr = f" AND optimisation LIKE '%{t}%'"
            sqlstr += optstr
            logging.info(f"Adding opt query '{optstr}'")
            self._opts.append(t)

        df = self._driver.selectSQL(sqlstr, {"app_name": app_name})
        if df.size > 0:
            dsl_code = df["opt_dsl_code"][0]
        else:
            dsl_code = None
        logging.info(f"Decoded dsl code :  {dsl_code}")
        return dsl_code

    def decode_ai_training_opt(self, opt_dsl: OptDSLReader):
        logging.info("Decoding AI training optimisation")
        app_type = opt_dsl.get_app_type()
        if not app_type == "ai_training":
            return ""
        config = opt_dsl.get_app_config()
        logging.info(f"Config section: {config}")
        data = opt_dsl.get_app_data()
        logging.info(f"Data section: {data}")
        ai_framework = config["ai_framework"]
        if opt_dsl.enable_opt_build():
            target = opt_dsl.get_opt_build()
        else:
            target = '{"cpu_type":"none","acc_type":"none"}'
            target = "{}"

        optimisation = opt_dsl.get_opt_list(ai_framework)

        sqlstr = "SELECT opt_dsl_code FROM optimisation WHERE app_name = %(app_name)s"

        target_nodes = self.get_json_nodes(json.dumps(target))
        for t in target_nodes:
            targetstr = f" AND target LIKE '%{t}%'"
            sqlstr += targetstr
            logging.info(f"Adding target query '{targetstr}'")

        if opt_dsl.enable_opt_build():
            sqlstr += " AND target LIKE '%enable_opt_build:true%'"
        else:
            sqlstr += " AND target LIKE '%enable_opt_build:false%'"

        opt_nodes = self.get_json_nodes(json.dumps(optimisation))
        logging.info(f"Optimisations: '{opt_nodes}'")
        for t in opt_nodes:
            optstr = f" AND optimisation LIKE '%{t}%'"
            sqlstr += optstr
            logging.info(f"Adding opt query '{optstr}'")
            self._opts.append(t)

        df = self._driver.selectSQL(sqlstr, {"app_name": ai_framework})
        if df.size > 0:
            dsl_code = df["opt_dsl_code"][0]
        else:
            dsl_code = None
        logging.info(f"Decoded dsl code '{dsl_code}'")
        return dsl_code

    def get_opts(self):
        return self._opts

    def get_decoded_opts(self, opt_json_obj):
        opts = []

        try:
            target_name = opt_json_obj["job"]["target"]["name"].strip()
            if target_name:
                opts.append(f"{target_name}:true")
        except KeyError:
            pass

        reader = OptDSLReader(opt_json_obj["job"])
        opts_list = reader.get_opts_list()
        if opts_list:
            opt_nodes = self.get_json_nodes(json.dumps(opts_list))
            opts.extend(opt_nodes)

        return opts
