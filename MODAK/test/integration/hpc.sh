#! /bin/sh

curl --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
    "job_options": {
      "job_name": "solver",
      "wall_time_limit": "1:00:00 ",
      "node_count": 2,
      "core_count": 40,
      "process_count_per_node": 40,
      "standard_output_file": "file.out",
      "standard_error_file": "file.err",
      "combine_stdout_stderr": true,
      "request_event_notification": "abe",
      "email_address": "kartshy@gmail.com"
    },
    "application": {
      "app_tag": "solver_clinicalUC",
      "container_runtime": "codeaster",
      "app_type": "hpc",
      "executable": "${ASTER_ROOT}/14.4/bin/aster ",
      "arguments": "${ASTER_ROOT}/14.4/lib/aster/Execution/E_SUPERV.py \\\n-commandes fort.1 --num_job=1432 --mode=interactif \\\n--rep_outils=${ASTER_ROOT}/outils \\\n--rep_mat=${ASTER_ROOT}/14.4/share/aster/materiau \\\n--rep_dex=${ASTER_ROOT}/14.4/share/aster/datg \\\n--numthreads=1 --suivi_batch --memjeveux=8192.0 --tpmax=3600.0",
      "mpi_ranks": 40,
      "threads": 1,
      "build": {
        "src": "https://www.code-aster.org/FICHIERS/aster-full-src-14.4.0-1.noarch.tar.gz",
        "build_command": "python3 setup.py install\n"
      }
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":true,
      "app_type":"hpc",
      "opt_build": {
        "cpu_type": "x86",
        "acc_type": ""
      },
      "autotuning": {
        "tuner": "cresta",
        "input": "dsl text"
      },
      "app_type-hpc": {
        "config":{
          "parallelisation":"mpi"
        },
        "data":{
          "location": "L1L2_NonLinear_prepared.tar.gz"
        },
        "parallelisation-mpi": {
          "library": "mpich",
          "version": "3.1.4"
        }
      }
    }
  }
}'   http://localhost:5000/optimise