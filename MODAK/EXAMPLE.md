# MODAK REST API

MODAK has one API: optimise

```
http://34.eightnine.53.105:fivethousand/optimise
``` 

(Examples below)
which takes a json input and returns the updated json with modified entries and job script.
Optimise method takes the following input json as shown below (Full specification)

```
{
  "job":{
    "job_options": {
      "job_name": "test",
      "account": "test",
      "queue": "standard",
      "wall_time_limit": "12:00:00 ",
      "node_count": 4,
      "core_count": 12,
      "process_count_per_node": 24,
      "core_count_per_process": 2,
      "memory_limit": "",
      "minimum_memory_per_processor": "10 MB",
      "request_gpus": 2,
      "request_specific_nodes": "BW20",
      "job_array": "1,2,3,4",
      "standard_output_file": "output file path",
      "standard_error_file": "file path",
      "combine_stdout_stderr": true,
      "architecture_constraint": "arch",
      "copy_environment": true,
      "copy_environment_variable": "",
      "job_dependency": " ",
      "request_event_notification": "events",
      "email_address": "mail.com",
      "defer_job": "date/time",
      "node_exclusive": true
    },
    "application": {
      "app_tag": "",
      "container_runtime": "ubuntu:18_04",
      "app_type": "mpi",
      "executable": "test_mpi",
      "arguments": "a b c",
      "mpi_ranks": 48,
      "threads": 2,
      "pre-execution": "script to run before execution",
      "post-execution": "script to run after execution",
      "build": {
        "src": "git://solver",
        "build_command": "make -j 2"
      }
    },
    "target": {
      "name": "hlrs_testbed",
      "queue_type": "slurm"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":true,
      "app_type":"ai_training/hpc/ai_inference",
      "opt_build": {
        "cpu_type": "x86/arm/amd/power",
        "acc_type": "nvidia/amd/fpga"
      },
      "autotuning": {
        "tuner": "cresta",
        "input": "dsl text"
      },
      "app_type-ai_training": {
        "config": {
          "ai_framework": "tensorflow/pytorch/keras/cntk/mxnet",
          "type": "image_classification/object_detection/translation/recommendation/reinforncement_learning" ,
          "distributed_training": true,
          "layers": 6 ,
          "parameters": 872684236
        },
        "data": {
          "location": "/some/data" ,
          "basedata": "Imagenet/CIFAR/MNIST" ,
          "size": 67 ,
          "count": 4389,
          "etl": {
            "prefetch": 100,
            "cache": 100
          }
        },
        "ai_framework-keras": {
          "version": 1.1,
          "backend": "tensorflow/pytorch/cntk/mxnet/keras"
        },
        "ai_framework-tensorflow": {
          "version": "1.1",
          "xla": true
        },
        "ai_framework-pytorch": {
          "version": "1.1",
          "glow": true
        }
      },
      "app_type-hpc": {
        "config":{
          "parallelisation":"mpi/openmp/opencc/opencl"
        },
        "data":{
          "location": "/some/data" ,
          "basedata": "IMAGE/RESTART" ,
          "size": 67 ,
          "count": 4389,
          "etl": {
            "prefetch": true,
            "cache": true
          }
        },
        "parallelisation-mpi": {
          "library": "mvapch/opnmpi",
          "version": "1.1",
          "scaling_efficiency": 0.75,
          "core_subscription": 1,
          "message_size": "small/medium/large"
        },
        "parallelisation-openmp": {
          "number_of_threads": 2,
          "scaling_efficiency": 0.75,
          "affinity": "block/simpe"
        },
        "parallelisation-opencc": {
          "compiler": "pgi/cray",
          "version": "1.1",
          "number_of_acc": 2
        },
        "parallelisation-opencl": {
          "compiler": "pgi/cray",
          "version": "1.1",
          "number_of_acc": 2
        }
      },
      "app_type-ai_inference": {}
    }
}
  }
}             
```

Example:
HPC 
```
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
}'   http://34.eightnine.53.105:fivethousand/optimise
```
 
Example:AI training
 
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "job_options": {
      "job_name": "skyline-extraction-training",
      "wall_time_limit": "12:00:00 ",
      "node_count": 1,
      "core_count": 40,
      "request_gpus": 1,
      "request_specific_nodes": "ssd",
      "standard_output_file": "skyline-extraction-training.out",
      "standard_error_file": "skyline-extraction-training.err",
      "combine_stdout_stderr": true,
      "copy_environment": true,
      "request_event_notification": "abe",
      "email_address": "kartshy@gmail.com"
    },
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/karthee/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":true,
      "app_type":"ai_training",
      "opt_build": {
        "cpu_type": "x86",
        "acc_type": "nvidia"
      },
      "autotuning": {
        "tuner": "cresta",
        "input": "dsl text"
      },
      "app_type-ai_training": {
        "config": {
          "ai_framework": "tensorflow"
        },
        "data": {
        },
        "ai_framework-tensorflow": {
          "version": "2.1",
          "xla": true
        }
      }
    }
  }
}
' \
  http://34.eightnine.53.105:fivethousand/optimise

```

MODAK expects the singularity containers to be pulled in to $SINGULARITY_DIR (define the directory)