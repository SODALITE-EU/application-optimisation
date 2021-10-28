#!/usr/bin/env python

import argparse
import pathlib
import sys

import sqlalchemy

from MODAK.db import Base

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()


def create(db_path, sql_path):
    if db_path.exists():
        db_path.unlink()

    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

    print(f"INFO: Creating schema on '{db_path}'...")
    Base.metadata.create_all(engine)

    print(f"INFO: Loading '{sql_path.name}' into '{db_path}'")
    con = engine.raw_connection()
    # Load the data via raw connection here to avoid var substitution:
    #   :true gets interpreted as var when loaded via SQLA's text()
    try:
        con.executescript(sql_path.read_text())
        con.commit()
    finally:
        con.close()


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

    prod_db_path = args.directory / "iac_model.db"
    test_db_path = args.directory / "test_iac_model.db"

    if (prod_db_path.exists() or test_db_path.exists()) and not args.force:
        print("ERROR: target database files already exist")
        sys.exit(1)

    create(prod_db_path, SCRIPT_DIR / "modak_prod.sql")
    create(test_db_path, SCRIPT_DIR / "modak_test.sql")
