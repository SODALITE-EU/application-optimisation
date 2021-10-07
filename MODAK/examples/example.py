#!/usr/bin/env python3

import pathlib
import sys

sys.path.append(".")

from MODAK.MODAK import MODAK  # noqa:E402
from MODAK.model import JobModel  # noqa:E402

m = MODAK()
dsl_file = pathlib.Path("test/input/mpi_test.json")
dsl_content = dsl_file.read_text()
model = JobModel.parse_raw(dsl_content)
link = m.optimise(model.job)

print(link)
