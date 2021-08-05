#!/usr/bin/env python3

import sys
import json

sys.path.append("../src")

from MODAK import MODAK

m = MODAK()
dsl_file = "../test/input/mpi_test.json"
with open(dsl_file) as json_file:
    job_data = json.load(json_file)
    link = m.optimise(job_data)

print(link)
