import argparse
import ast
import asyncio
import json
import logging
import sys
from typing import Any, Dict

from fastapi.openapi.utils import get_openapi
from pydantic import ValidationError
from rich import print
from sqlalchemy.dialects import sqlite
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable

from . import db
from .app import app
from .MODAK import MODAK
from .model import (
    JobModel,
    Script,
    ScriptConditionApplication,
    ScriptConditionInfrastructure,
    ScriptConditions,
    ScriptData,
    ScriptDataStage,
    ScriptIn,
)
from .modeldb import create_script
from .settings import Settings


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
                CreateTable(getattr(db, tbl).__table__).compile(
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

    m = MODAK()

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


def import_script():
    parser = argparse.ArgumentParser(description="Import a script into MODAK")
    parser.add_argument(
        "script",
        type=argparse.FileType("r"),
        help="Script file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose logging output",
        action="count",
        dest="loglevel",
        default=0,
    )
    parser.add_argument(
        "--stage",
        help="At which stage to run this script",
        default="pre",
        choices=ScriptDataStage._member_names_,
    )
    parser.add_argument(
        "--condition-application-name",
        metavar="NAME",
        help="Specify the application name (if any) to run this script for",
    )
    parser.add_argument(
        "--condition-application-feature",
        help="Specify the application feature condition",
        metavar="NAME=VALUE",
        action="append",
        default=[],
    )
    parser.add_argument(
        "--condition-infrastructure-name",
        metavar="NAME",
        help="Specify the name of an infrastructure to run this script for",
    )
    parser.add_argument(
        "--description",
        help="Description for the script",
    )

    args = parser.parse_args()
    loglevel = logging.WARNING
    if args.loglevel >= 2:
        loglevel = logging.DEBUG
    elif args.loglevel > 1:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel, force=True)

    conditions = ScriptConditions()

    if args.condition_application_name:
        app_feats = {
            k: ast.literal_eval(v)
            for k, v in (
                f.split("=", maxsplit=1) for f in args.condition_application_feature
            )
        }
        conditions.application = ScriptConditionApplication(
            name=args.condition_application_name, feature=app_feats
        )

    if args.condition_infrastructure_name:
        app_feats = {
            k: ast.literal_eval(v)
            for k, v in (
                f.split("=", maxsplit=1) for f in args.condition_application_feature
            )
        }
        conditions.infrastructure = ScriptConditionInfrastructure(
            name=args.condition_infrastructure_name
        )

    script = ScriptIn(
        description=args.description,
        conditions=conditions,
        data=ScriptData(stage=args.stage, raw=args.script.read()),
    )

    engine = create_async_engine(f"sqlite+aiosqlite:///{Settings.db_path}", future=True)
    SessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    async def create_async(script):
        async with SessionLocal() as session:
            dbobj = await create_script(session, script)
            session.add(dbobj)
            await session.commit()
            script = Script.from_orm(dbobj)

        print("Added script:\n")
        print("ID:", script.id)
        print("Description:", script.description)
        print("Conditions:")
        print("  Application:")
        print(
            "    Name:",
            script.conditions.application.name
            if script.conditions.application
            else None,
        )
        print("    Feature:")
        if script.conditions.application:
            for key, value in script.conditions.application.feature.items():
                print(f"      {key}:", value)
        print("  Infrastructure:")
        print(
            "    Name:",
            script.conditions.infrastructure.name
            if script.conditions.infrastructure
            else None,
        )
        print("Data:")
        print("  Stage:", script.data.stage)
        print("  Raw:")
        print("  ==>")
        print(script.data.raw, end="")
        print("  <==")

    asyncio.run(create_async(script))


def dbshell():
    from IPython import embed

    engine = create_async_engine(f"sqlite+aiosqlite:///{Settings.db_path}", future=True)
    SessionLocal = sessionmaker(  # noqa: F841
        engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    embed(using="asyncio")
