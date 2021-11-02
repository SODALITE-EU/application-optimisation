import configparser
import logging
import os
import pathlib
import re
from configparser import ConfigParser
from typing import Any, Dict, Optional

from pydantic import BaseSettings

DEFAULT_SETTINGS_DIR = pathlib.Path(__file__).parent.resolve().parent / "conf"


def configparser_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    conf_file = pathlib.Path(
        os.environ.get("MODAK_CONFIG", DEFAULT_SETTINGS_DIR / "iac-model.ini")
    )

    logging.info(f"Reading ini file : {conf_file}")

    try:
        config = ConfigParser()
        config.read(conf_file)

        data: Dict[str, Any] = {
            "mode": config["modak"]["mode"],
        }

        data["quiet_server_logs"] = config["modak"]["quiet_server_log"] == "true"

        section = config[data["mode"]]
        logging.info(f"Reading section {data['mode']} of ini file ")
        data["db_uri"] = section["db_uri"]

        match = re.match(
            r"(?P<dialect>mysql|sqlite)://"
            r"(?P<path>(?:(?P<username>[^@:]+)(?::(?P<password>[^@]+))?@)?"
            r"(?P<hostname>[^@/:]+)?(?::(?P<port>\d+))?/"
            r"(?P<dbname>.+))",
            data["db_uri"],
        )

        if not match:
            raise ValueError(f"Unable to parse db_uri '{data['db_uri']}'")

        data["db_dialect"] = match["dialect"]

        if data["db_dialect"] == "mysql":
            data["db_user"] = match["username"]
            data["db_password"] = match["password"] if match["password"] else ""
            data["db_host"] = match["host"]
            data["db_port"] = int(match["port"]) if match["port"] else 3306
            data["db_name"] = match["dbname"]
        elif data["db_dialect"] == "sqlite":
            # relative directories are taken as relative to the configuration file,
            # absolute dirs are maintained as such
            data["db_path"] = conf_file.parent / match["path"]
        else:
            raise AssertionError(f"Invalid dialect: {match['dialect']}")

        data["out_dir"] = pathlib.Path(section["out_dir"])
        logging.info("out dir : {data['out_dir']}")

        if "google_credentials" in section:
            data["google_credentials"] = section["google_credentials"]

        if "dropbox_access_token" in section:
            data["dropbox_access_token"] = section["dropbox_access_token"]

        sa_section = f"{data['mode']}.image_hub_aliases"
        data["image_hub_aliases"] = (
            dict(config.items(sa_section)) if config.has_section(sa_section) else {}
        )

    except configparser.Error as exc:
        logging.exception(exc)
        raise

    return data


class SettingsBase(BaseSettings):
    """All settings required for MODAK will be stored in an instance of this."""

    mode: str
    quiet_server_logs: bool
    db_uri: str
    db_dialect: str
    db_user: Optional[str]
    db_password: Optional[str]
    db_host: Optional[str]
    db_port: Optional[int]
    db_name: Optional[str]
    db_path: Optional[pathlib.Path]
    out_dir: pathlib.Path
    image_hub_aliases: Dict[str, str]

    google_credentials: Optional[pathlib.Path]
    dropbox_access_token: Optional[str]

    class Config:
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                configparser_settings_source,
                env_settings,
                file_secret_settings,
            )


Settings = SettingsBase()
