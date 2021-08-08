#!/usr/bin/env python3

import json
import sys

sys.path.append("../src")

from MODAK import MODAK  # noqa:E402

m = MODAK()
dsl_file = "../test/input/mpi_test.json"
with open(dsl_file) as json_file:
    job_data = json.load(json_file)
    link = m.optimise(job_data)

print(link)
