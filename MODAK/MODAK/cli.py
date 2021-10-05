import argparse
import sys

from pydantic import ValidationError

from .model import JobModel


def validate_json():
    parser = argparse.ArgumentParser(
        description="Verify that a JSON file matches the required Job schema"
    )
    parser.add_argument(
        "infile",
        metavar="<FILE>",
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
