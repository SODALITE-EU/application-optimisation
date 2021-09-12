#!/usr/bin/env python

import argparse
import pathlib
import sqlite3
import sys

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()

prod_sql_path = SCRIPT_DIR / "modak_prod.sql"
test_sql_path = SCRIPT_DIR / "modak_test.sql"


def create(out_dir, force=False):
    prod_db_path = out_dir / "iac_model.db"
    test_db_path = out_dir / "test_iac_model.db"

    if (prod_db_path.exists() or test_db_path.exists()) and not force:
        print("ERROR: target database files already exist")
        sys.exit(1)

    with sqlite3.connect(prod_db_path) as con:
        print(f"INFO: Loading '{prod_sql_path.name}' into '{prod_db_path}'")
        con.executescript(prod_sql_path.read_text())

    with sqlite3.connect(test_db_path) as con:
        print(f"INFO: Loading '{test_sql_path.name}' into '{test_db_path}'")
        con.executescript(test_sql_path.read_text())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-C",
        "--directory",
        type=pathlib.Path,
        required=False,
        default=pathlib.Path.cwd(),
        help="Where to create the DB files",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        required=False,
        default=False,
        help="overwrite existing DB files",
    )
    args = parser.parse_args()
    create(args.directory, args.force)
