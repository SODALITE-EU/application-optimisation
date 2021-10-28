import argparse
import json
import logging
import pathlib
import sys
from typing import Any, Dict

from fastapi.openapi.utils import get_openapi
from pydantic import ValidationError
from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import CreateTable

from . import db
from .app import app
from .MODAK import MODAK
from .model import JobModel
from .settings import DEFAULT_SETTINGS_DIR


def validate_json():
    parser = argparse.ArgumentParser(
        description="Verify that a JSON file matches the required Job schema"
    )
    parser.add_argument(
        "infile",
        metavar="<FILE>",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="The file to use. <stdin> if not specified.",
    )
    args = parser.parse_args()

    try:
        JobModel.parse_raw(args.infile.read())
        print("OK: Validation succeeded.", file=sys.stderr)
    except ValidationError as exc:
        print("ERROR: Validation failed.", file=sys.stderr)
        print(exc, file=sys.stderr)
        sys.exit(1)


def _print_json(json_data, outfile, raw=False):
    dumpopts = {}

    if not raw:
        dumpopts["indent"] = 2

    json.dump(json_data, outfile, **dumpopts)


def schema():
    parser = argparse.ArgumentParser(description="Generate different schema documents")
    parser.add_argument(
        "schema",
        metavar="<SCHEMA>",
        type=str,
        choices=("openapi", "dsl", "sql"),
        default="openapi",
        help=(
            "The schema to generate: 'openapi' for the complete web OpenAPI/Swagger schema,"
            " 'dsl' for the JSON schema for the DSL, 'sql' for the database schema."
        ),
    )
    parser.add_argument(
        "outfile",
        metavar="<FILE>",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="The file to use. <stdout> if not specified.",
    )
    parser.add_argument(
        "-r",
        "--raw",
        action="store_true",
        help="Do not pretty print the generated JSON.",
    )
    args = parser.parse_args()

    if args.schema == "openapi":
        json_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )
        _print_json(json_schema, args.outfile, args.raw)
    elif args.schema == "dsl":
        json_schema = JobModel.schema()
        _print_json(json_schema, args.outfile, args.raw)

    elif args.schema == "sql":
        for tbl in db.__all__:
            print(
                CreateTable(getattr(getattr(db, tbl), "__table__")).compile(
                    dialect=sqlite.dialect()
                ),
                file=args.outfile,
            )


def modak():
    parser = argparse.ArgumentParser(
        description="Generate MODAK output given a DSL file"
    )
    parser.add_argument(
        "-i",
        "--ifile",
        metavar="DSLFILE",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="DSL file (default: read from stdin)",
    )
    parser.add_argument(
        "-o",
        "--ofile",
        metavar="OUTPUTFILE",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Output file (default: write to stdout)",
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="CONFIGFILE",
        type=pathlib.Path,
        default=DEFAULT_SETTINGS_DIR / "iac-model.ini",
        help=f"Configuration file (default: {DEFAULT_SETTINGS_DIR / 'iac-model.ini'}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose logging output",
        action="count",
        dest="loglevel",
        default=0,
    )
    args = parser.parse_args()

    loglevel = logging.WARNING
    if args.loglevel >= 2:
        loglevel = logging.DEBUG
    elif args.loglevel > 1:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, force=True)

    print(f"Input file: '{args.ifile.name}'", file=sys.stderr)
    print(f"Output file: '{args.ofile.name}'", file=sys.stderr)

    m = MODAK(args.config)

    model = JobModel.parse_raw(args.ifile.read())

    link = m.optimise(model.job)

    json_dump_opts: Dict[str, Any] = {}
    if args.ofile == sys.stdout:
        json_dump_opts["indent"] = 2

    print(f"Job script location: {link.jobscript}", file=sys.stderr)
    print(f"Job script location: {link.buildscript}", file=sys.stderr)
    model.job.job_script = link.jobscript
    model.job.build_script = link.buildscript

    args.ofile.write(model.json(**json_dump_opts))

    if args.ofile == sys.stdout:
        args.ofile.write("\n")
