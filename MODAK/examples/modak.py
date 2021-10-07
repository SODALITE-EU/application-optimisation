#!/usr/bin/env python3

import argparse
import pathlib
import sys
from typing import Any, Dict

from MODAK.MODAK import MODAK
from MODAK.model import JobModel
from MODAK.settings import DEFAULT_SETTINGS_DIR

parser = argparse.ArgumentParser(description="Generate MODAK output given a DSL file")
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
args = parser.parse_args()

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
