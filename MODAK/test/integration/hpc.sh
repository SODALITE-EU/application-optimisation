#! /bin/sh

# Fail if any command fails
set -e

# local test
curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
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
}'   http://localhost:55000/get_image

curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":true,
      "app_type":"hpc",
      "opt_build": {
        "cpu_type": "x86",
        "acc_type": "none"
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
}'   http://localhost:55000/get_image

# + test getting image
curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
    "optimization": {
      "app_type": "ai_training", 
      "app_type-ai_training": {
        "ai_framework-tensorflow": {
          "version": "2.1", 
          "xla": false
        }, 
        "config": {
          "ai_framework": "tensorflow", 
          "distributed_training": true, 
          "layers": 6, 
          "parameters": 872684236, 
          "type": "translation"
        }, 
        "data": {
          "basedata": "imagenet", 
          "count": 4389, 
          "etl": {
            "cache": 100, 
            "prefetch": 100
          }, 
          "location": "/some/data", 
          "size": 67
        }
      }, 
      "autotuning": {
        "input": "begin parameters begin typing int NB end typing begin constraints range NB 80. 90, 100, 120, 140 end constraints end parameters begin build command: make -DNB=$NB end build begin run command: ./solver end run", 
        "tuner": "cresta"
      }, 
      "enable_autotuning": true, 
      "enable_opt_build": true, 
      "opt_build": {
        "acc_type": "nvidia", 
        "cpu_type": "x86"
      }
    }
  }
}'   http://localhost:55000/get_image

curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
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
          "xla": false
        }
      }
    }
  }
}'   http://localhost:55000/get_image

# + test getting image
curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
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
}'   http://77.231.202.209:5000/get_image
# {
#   "job": {
#     "container_runtime": "docker://ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof", 
#     "optimisation": {
#       "app_type": "hpc", 
#       "app_type-hpc": {
#         "config": {
#           "parallelisation": "mpi"
#         }, 
#         "data": {
#           "location": "L1L2_NonLinear_prepared.tar.gz"
#         }, 
#         "parallelisation-mpi": {
#           "version": "3.1.4"
#         }
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": true, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "", 
#         "cpu_type": "x86"
#       }
#     }
#   }
# }

curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
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
}'   http://77.231.202.209:5000/get_image
# {
#   "job": {
#     "container_runtime": "docker://modakopt/modak:tensorflow-2.1-gpu-src", 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": true
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": true, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }
#   }
# }


# + test full job script with target name = hlrs_testbed, job_scheduler_type = slurm
# + assert torque header, since hlrs_testbed has torque wm
curl --fail --header "Content-Type: application/json" \
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
      "email_address": "abc@gmail.com"
    },
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "name": "hlrs_testbed",
      "job_scheduler_type": "slurm"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://modakopt/modak:tensorflow-2.1-gpu-src", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#PBS -S /bin/bash\n## START OF HEADER ## \n#PBS -N skyline-extraction-training\n#PBS -l walltime=12:00:00 \n#PBS -l nodes=1:gpus=1\n#PBS -l procs=40\n#PBS -l nodes=ssd\n#PBS -o skyline-extraction-training.out\n#PBS -e skyline-extraction-training.err\n#PBS -j oe\n#PBS -V \n#PBS -m abe\n#PBS -M abc@gmail.com\n## END OF HEADER ## \ncd $PBS_O_WORKDIR\nexport PATH=$PBS_O_WORKDIR:$PATH\n\nfile=set_default_hlrs_testbed.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/hpfcwwkd4zy52t9/set_default_hlrs_testbed.sh\nchmod 755 set_default_hlrs_testbed.sh\nsource set_default_hlrs_testbed.sh\nsingularity exec --nv  $SINGULARITY_DIR/modak_tensorflow-2.1-gpu-src.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "job_options": {
#       "combine_stdout_stderr": true, 
#       "copy_environment": true, 
#       "core_count": 40, 
#       "email_address": "abc@gmail.com", 
#       "job_name": "skyline-extraction-training", 
#       "node_count": 1, 
#       "request_event_notification": "abe", 
#       "request_gpus": 1, 
#       "request_specific_nodes": "ssd", 
#       "standard_error_file": "skyline-extraction-training.err", 
#       "standard_output_file": "skyline-extraction-training.out", 
#       "wall_time_limit": "12:00:00 "
#     }, 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": true
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }, 
#     "target": {
#       "job_scheduler_type": "slurm", 
#       "name": "hlrs_testbed"
#     }
#   }
# }

# + test full job script with target name = hlrs_testbed, job_scheduler_type = torque
# + assert torque header
curl --fail --header "Content-Type: application/json" \
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
      "email_address": "abc@gmail.com"
    },
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "name": "hlrs_testbed",
      "job_scheduler_type": "torque"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://modakopt/modak:tensorflow-2.1-gpu-src", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#PBS -S /bin/bash\n## START OF HEADER ## \n#PBS -N skyline-extraction-training\n#PBS -l walltime=12:00:00 \n#PBS -l nodes=1:gpus=1\n#PBS -l procs=40\n#PBS -l nodes=ssd\n#PBS -o skyline-extraction-training.out\n#PBS -e skyline-extraction-training.err\n#PBS -j oe\n#PBS -V \n#PBS -m abe\n#PBS -M abc@gmail.com\n## END OF HEADER ## \ncd $PBS_O_WORKDIR\nexport PATH=$PBS_O_WORKDIR:$PATH\n\nfile=set_default_hlrs_testbed.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/hpfcwwkd4zy52t9/set_default_hlrs_testbed.sh\nchmod 755 set_default_hlrs_testbed.sh\nsource set_default_hlrs_testbed.sh\nsingularity exec --nv  $SINGULARITY_DIR/modak_tensorflow-2.1-gpu-src.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "job_options": {
#       "combine_stdout_stderr": true, 
#       "copy_environment": true, 
#       "core_count": 40, 
#       "email_address": "abc@gmail.com", 
#       "job_name": "skyline-extraction-training", 
#       "node_count": 1, 
#       "request_event_notification": "abe", 
#       "request_gpus": 1, 
#       "request_specific_nodes": "ssd", 
#       "standard_error_file": "skyline-extraction-training.err", 
#       "standard_output_file": "skyline-extraction-training.out", 
#       "wall_time_limit": "12:00:00 "
#     }, 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": true
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }, 
#     "target": {
#       "job_scheduler_type": "torque", 
#       "name": "hlrs_testbed"
#     }
#   }
# }

# + test full job script with target name = hlrs_testbed
# + assert torque header, since hlrs_testbed has torque wm
curl --fail --header "Content-Type: application/json" \
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
      "email_address": "abc@gmail.com"
    },
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "name": "hlrs_testbed"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://modakopt/modak:tensorflow-2.1-gpu-src", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#PBS -S /bin/bash\n## START OF HEADER ## \n#PBS -N skyline-extraction-training\n#PBS -l walltime=12:00:00 \n#PBS -l nodes=1:gpus=1\n#PBS -l procs=40\n#PBS -l nodes=ssd\n#PBS -o skyline-extraction-training.out\n#PBS -e skyline-extraction-training.err\n#PBS -j oe\n#PBS -V \n#PBS -m abe\n#PBS -M abc@gmail.com\n## END OF HEADER ## \ncd $PBS_O_WORKDIR\nexport PATH=$PBS_O_WORKDIR:$PATH\n\nfile=set_default_hlrs_testbed.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/hpfcwwkd4zy52t9/set_default_hlrs_testbed.sh\nchmod 755 set_default_hlrs_testbed.sh\nsource set_default_hlrs_testbed.sh\nsingularity exec --nv  $SINGULARITY_DIR/modak_tensorflow-2.1-gpu-src.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "job_options": {
#       "combine_stdout_stderr": true, 
#       "copy_environment": true, 
#       "core_count": 40, 
#       "email_address": "abc@gmail.com", 
#       "job_name": "skyline-extraction-training", 
#       "node_count": 1, 
#       "request_event_notification": "abe", 
#       "request_gpus": 1, 
#       "request_specific_nodes": "ssd", 
#       "standard_error_file": "skyline-extraction-training.err", 
#       "standard_output_file": "skyline-extraction-training.out", 
#       "wall_time_limit": "12:00:00 "
#     }, 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": true
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }, 
#     "target": {
#       "name": "hlrs_testbed"
#     }
#   }
# }

# + test full job script with target job_scheduler_type = torque no xla and with xla
# + assert torque header
curl --fail --header "Content-Type: application/json" \
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
      "email_address": "abc@gmail.com"
    },
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "job_scheduler_type": "torque"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
          "xla": false
        }
      }
    }
  }
}
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#PBS -S /bin/bash\n## START OF HEADER ## \n#PBS -N skyline-extraction-training\n#PBS -l walltime=12:00:00 \n#PBS -l nodes=1:gpus=1\n#PBS -l procs=40\n#PBS -l nodes=ssd\n#PBS -o skyline-extraction-training.out\n#PBS -e skyline-extraction-training.err\n#PBS -j oe\n#PBS -V \n#PBS -m abe\n#PBS -M abc@gmail.com\n## END OF HEADER ## \ncd $PBS_O_WORKDIR\nexport PATH=$PBS_O_WORKDIR:$PATH\nsingularity exec --nv  $SINGULARITY_DIR/tensorflow_2.1.0-gpu-py3.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "job_options": {
#       "combine_stdout_stderr": true, 
#       "copy_environment": true, 
#       "core_count": 40, 
#       "email_address": "abc@gmail.com", 
#       "job_name": "skyline-extraction-training", 
#       "node_count": 1, 
#       "request_event_notification": "abe", 
#       "request_gpus": 1, 
#       "request_specific_nodes": "ssd", 
#       "standard_error_file": "skyline-extraction-training.err", 
#       "standard_output_file": "skyline-extraction-training.out", 
#       "wall_time_limit": "12:00:00 "
#     }, 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": false
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }, 
#     "target": {
#       "job_scheduler_type": "torque"
#     }
#   }
# }

# + test full job script with target job_scheduler_type = slurm
# + assert slurm header
curl --fail --header "Content-Type: application/json" \
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
      "email_address": "abc@gmail.com"
    },
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "job_scheduler_type": "slurm"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://modakopt/modak:tensorflow-2.1-gpu-src", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n## START OF HEADER ##\n#SBATCH -J skyline-extraction-training\n#SBATCH --time=12:00:00 \n#SBATCH -N 1\n#SBATCH -n 40\n#SBATCH --gres=gpu:1\n#SBATCH --nodelist=ssd\n#SBATCH --output=skyline-extraction-training.out\n#SBATCH -error=skyline-extraction-training.err\n#SBATCH --export=ALL \n#SBATCH --mail-type=abe\n#SBATCH --mail-user=abc@gmail.com\n## END OF HEADER ##\ncd $SLURM_SUBMIT_DIR\nexport PATH=$SLURM_SUBMIT_DIR:$PATH\n\nfile=enable_xla.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/e6n9yb0a5601gp2/enable_xla.sh\nchmod 755 enable_xla.sh\nsource enable_xla.sh\nsingularity exec --nv  $SINGULARITY_DIR/modak_tensorflow-2.1-gpu-src.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "job_options": {
#       "combine_stdout_stderr": true, 
#       "copy_environment": true, 
#       "core_count": 40, 
#       "email_address": "abc@gmail.com", 
#       "job_name": "skyline-extraction-training", 
#       "node_count": 1, 
#       "request_event_notification": "abe", 
#       "request_gpus": 1, 
#       "request_specific_nodes": "ssd", 
#       "standard_error_file": "skyline-extraction-training.err", 
#       "standard_output_file": "skyline-extraction-training.out", 
#       "wall_time_limit": "12:00:00 "
#     }, 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": true
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }, 
#     "target": {
#       "job_scheduler_type": "slurm"
#     }
#   }
# }

# + test script with opts without job_options with target job_scheduler_type = slurm
# + test script with opts without job_options with target job_scheduler_type = torque
# + test script with opts without job_options without target
# + assert no headers with opts
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "job_scheduler_type": "slurm"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
          "xla": false
        }
      }
    }
  }
}
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\nsingularity exec $SINGULARITY_DIR/tensorflow_2.1.0-gpu-py3.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": false
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }, 
#     "target": {
#       "job_scheduler_type": "slurm"
#     }
#   }
# }

curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "job_scheduler_type": "torque"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://modakopt/modak:tensorflow-2.1-gpu-src", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nfile=enable_xla.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/e6n9yb0a5601gp2/enable_xla.sh\nchmod 755 enable_xla.sh\nsource enable_xla.sh\nsingularity exec $SINGULARITY_DIR/modak_tensorflow-2.1-gpu-src.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": true
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }, 
#     "target": {
#       "job_scheduler_type": "torque"
#     }
#   }
# }


curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://modakopt/modak:tensorflow-2.1-gpu-src", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nfile=enable_xla.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/e6n9yb0a5601gp2/enable_xla.sh\nchmod 755 enable_xla.sh\nsource enable_xla.sh\nsingularity exec $SINGULARITY_DIR/modak_tensorflow-2.1-gpu-src.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": true
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }
#   }
# }


# + test script with opts without job_options with target name = egi
# + test script with opts without job_options with target name = hlrs_testbed
# + assert no headers with opts specific to target
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "name": "hlrs_testbed"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://modakopt/modak:tensorflow-2.1-gpu-src", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nfile=set_default_hlrs_testbed.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/hpfcwwkd4zy52t9/set_default_hlrs_testbed.sh\nchmod 755 set_default_hlrs_testbed.sh\nsource set_default_hlrs_testbed.sh\nsingularity exec $SINGULARITY_DIR/modak_tensorflow-2.1-gpu-src.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": true
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }, 
#     "target": {
#       "name": "hlrs_testbed"
#     }
#   }
# }

curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "name": "egi"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://modakopt/modak:tensorflow-2.1-gpu-src", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nfile=set_default_egi.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/97h9zkj7uxx9sc5/set_default_egi.sh\nchmod 755 set_default_egi.sh\nsource set_default_egi.sh\nsingularity exec $SINGULARITY_DIR/modak_tensorflow-2.1-gpu-src.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": true
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }, 
#     "target": {
#       "name": "egi"
#     }
#   }
# }

# - test script without opts without job_options with target target name = egi
# - test script without opts without job_options with target target name = hlrs_testbed
# - assert no headers with opts specific to target
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "name": "hlrs_testbed"
    }
  }
}
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nfile=set_default_hlrs_testbed.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/hpfcwwkd4zy52t9/set_default_hlrs_testbed.sh\nchmod 755 set_default_hlrs_testbed.sh\nsource set_default_hlrs_testbed.sh\nsingularity exec $SINGULARITY_DIR/tensorflow_2.1.0-gpu-py3.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "target": {
#       "name": "hlrs_testbed"
#     }
#   }
# }

curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "name": "egi"
    }
  }
}
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nfile=set_default_egi.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/97h9zkj7uxx9sc5/set_default_egi.sh\nchmod 755 set_default_egi.sh\nsource set_default_egi.sh\nsingularity exec $SINGULARITY_DIR/tensorflow_2.1.0-gpu-py3.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "target": {
#       "name": "egi"
#     }
#   }
# }


# - test script without opts without target
# - assert no headers without opts - only app
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    }
  }
}
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "tensorflow/tensorflow:2.1.0-gpu-py3", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\nsingularity exec $SINGULARITY_DIR/tensorflow_2.1.0-gpu-py3.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n"
#   }
# }

# + test app without container runtime
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    }
  }
}
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n"
#   }
# }

# + test app without container runtime but with target
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "name": "egi"
    }
  }
}
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nfile=set_default_egi.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/97h9zkj7uxx9sc5/set_default_egi.sh\nchmod 755 set_default_egi.sh\nsource set_default_egi.sh\n python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "target": {
#       "name": "egi"
#     }
#   }
# }

# + test app without container runtime with app_type mpi without target
curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "app_type": "mpi",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    }
  }
}
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "mpi", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nexport OMP_NUM_THREADS=1\nmpirun -np 1  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n"
#   }
# }

# + test app without container runtime with app_type mpi with target
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "app_type": "mpi",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "name": "egi"
    }
  }
}
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "mpi", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nfile=set_default_egi.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/97h9zkj7uxx9sc5/set_default_egi.sh\nchmod 755 set_default_egi.sh\nsource set_default_egi.sh\n\nexport OMP_NUM_THREADS=1\nmpirun -np 1  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "target": {
#       "name": "egi"
#     }
#   }
# }

# + test app without container runtime but with target without app_type
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "name": "egi"
    }
  }
}
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nfile=set_default_egi.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/97h9zkj7uxx9sc5/set_default_egi.sh\nchmod 755 set_default_egi.sh\nsource set_default_egi.sh\n python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "target": {
#       "name": "egi"
#     }
#   }
# }

# + test app without container runtime but with opt
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://modakopt/modak:tensorflow-2.1-gpu-src", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nfile=enable_xla.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/e6n9yb0a5601gp2/enable_xla.sh\nchmod 755 enable_xla.sh\nsource enable_xla.sh\nsingularity exec $SINGULARITY_DIR/modak_tensorflow-2.1-gpu-src.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": true
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }
#   }
# }

# + test app without container runtime but with opt and target
# + assert two enforced scripts - one for hlrs_testbed target and one for xla
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "app_type": "python",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
    },
    "target": {
      "name": "hlrs_testbed"
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
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
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "python", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://modakopt/modak:tensorflow-2.1-gpu-src", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nfile=set_default_hlrs_testbed.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/hpfcwwkd4zy52t9/set_default_hlrs_testbed.sh\nchmod 755 set_default_hlrs_testbed.sh\nsource set_default_hlrs_testbed.sh\n\nfile=enable_xla.sh\nif [ -f $file ] ; then rm $file; fi\nwget --no-check-certificate https://www.dropbox.com/s/e6n9yb0a5601gp2/enable_xla.sh\nchmod 755 enable_xla.sh\nsource enable_xla.sh\nsingularity exec $SINGULARITY_DIR/modak_tensorflow-2.1-gpu-src.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "optimisation": {
#       "app_type": "ai_training", 
#       "app_type-ai_training": {
#         "ai_framework-tensorflow": {
#           "version": "2.1", 
#           "xla": true
#         }, 
#         "config": {
#           "ai_framework": "tensorflow"
#         }, 
#         "data": {}
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": false, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "nvidia", 
#         "cpu_type": "x86"
#       }
#     }, 
#     "target": {
#       "name": "hlrs_testbed"
#     }
#   }
# }

# + test app without container runtime but with opt hpc
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "app_type": "mpi",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
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
}
' http://77.231.202.209:5000/get_job_content
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "mpi", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "job_content": "#!/bin/bash\n\n\nexport OMP_NUM_THREADS=1\nmpirun -np 1 singularity exec $SINGULARITY_DIR/mpich_ub1804_cuda101_mpi314_gnugprof.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "optimisation": {
#       "app_type": "hpc", 
#       "app_type-hpc": {
#         "config": {
#           "parallelisation": "mpi"
#         }, 
#         "data": {
#           "location": "L1L2_NonLinear_prepared.tar.gz"
#         }, 
#         "parallelisation-mpi": {
#           "version": "3.1.4"
#         }
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": true, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "", 
#         "cpu_type": "x86"
#       }
#     }
#   }
# }


# - test full optimisation
curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "application": {
      "app_tag": "skyline-extraction-training",
      "app_type": "mpi",
      "executable": "python3 resnet/resnet_imagenet_main.py",
      "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false"
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
}
' http://77.231.202.209:5000/get_optimisation
# {
#   "job": {
#     "application": {
#       "app_tag": "skyline-extraction-training", 
#       "app_type": "mpi", 
#       "arguments": "--data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false", 
#       "container_runtime": "docker://ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof", 
#       "executable": "python3 resnet/resnet_imagenet_main.py"
#     }, 
#     "container_runtime": "docker://ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof", 
#     "job_content": "#!/bin/bash\n\n\nexport OMP_NUM_THREADS=1\nmpirun -np 1 singularity exec $SINGULARITY_DIR/mpich_ub1804_cuda101_mpi314_gnugprof.sif  python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/abc/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10 --use_synthetic_data=false\n", 
#     "optimisation": {
#       "app_type": "hpc", 
#       "app_type-hpc": {
#         "config": {
#           "parallelisation": "mpi"
#         }, 
#         "data": {
#           "location": "L1L2_NonLinear_prepared.tar.gz"
#         }, 
#         "parallelisation-mpi": {
#           "version": "3.1.4"
#         }
#       }, 
#       "autotuning": {
#         "input": "dsl text", 
#         "tuner": "cresta"
#       }, 
#       "enable_autotuning": true, 
#       "enable_opt_build": true, 
#       "opt_build": {
#         "acc_type": "", 
#         "cpu_type": "x86"
#       }
#     }
#   }
# }


curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
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
          "library": "openmpi",
          "version": "3.1.3"
        }
      }
    }
  }
}'   http://localhost:55000/get_image



curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "job_options": {
      "job_name": "test",
      "wall_time_limit": "1:00:00 ",
      "node_count": 1,
      "process_count_per_node": 2,
      "standard_output_file": "test.out",
      "standard_error_file": "test.err",
      "combine_stdout_stderr": true,
      "copy_environment": true
    },
    "application": {
      "app_tag": "test",
      "executable": "bash -c \"cd modpy/build/lib/moduli/ && python3 main_mpi.py -s -f $PBS_O_WORKDIR/output/iso/L1L2-iso.dens -o $PBS_O_WORKDIR/output/moduli\"",
      "build": {
        "src": "$HOME/modpy/.git",
        "build_command": "bash -c \"cd modpy && pip3 --no-cache-dir install numpy pandas mpi4py --user && python3 setup.py install --user\""
      }
    },
    "target": {
      "name": "egi"
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
          "library": "openmpi",
          "version": "3.1.3"
        }
      }
    }
  }
}
' http://localhost:55000/get_job_content




curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "job_options": {
      "job_name": "test",
      "wall_time_limit": "1:00:00 ",
      "node_count": 1,
      "process_count_per_node": 2,
      "standard_output_file": "test.out",
      "standard_error_file": "test.err",
      "combine_stdout_stderr": true,
      "copy_environment": true
    },
    "application": {
      "app_tag": "test",
      "executable": "bash -c \"cd modpy/build/lib/moduli/ && python3 main_mpi.py -s -f $PBS_O_WORKDIR/output/iso/L1L2-iso.dens -o $PBS_O_WORKDIR/output/moduli\"",
      "build": {
        "src": "$HOME/modpy/.git",
        "build_command": "bash -c \"cd modpy && pip3 --no-cache-dir install numpy pandas mpi4py --user && python3 setup.py install --user\""
      }
    },
    "target": {
      "name": "egi"
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
          "library": "openmpi",
          "version": "3.1.3"
        }
      }
    }
  }
}
' http://77.231.202.209:5000/get_job_content

curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "job_options": {
      "job_name": "test",
      "wall_time_limit": "1:00:00 ",
      "node_count": 1,
      "process_count_per_node": 2,
      "standard_output_file": "test.out",
      "standard_error_file": "test.err",
      "combine_stdout_stderr": true,
      "copy_environment": true
    },
    "application": {
      "app_tag": "test",
      "executable": "bash -c \"cd modpy/build/lib/moduli/ && python3 main_mpi.py -s -f $PBS_O_WORKDIR/output/iso/L1L2-iso.dens -o $PBS_O_WORKDIR/output/moduli\"",
      "build": {
        "src": "$HOME/modpy/.git",
        "build_command": "bash -c \"cd modpy && pip3 --no-cache-dir install numpy pandas mpi4py --user && python3 setup.py install --user\""
      }
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":true,
      "app_type":"hpc",
      "opt_build": {
        "cpu_type": "x86",
        "acc_type": "none"
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
          "library": "openmpi",
          "version": "3.1.3"
        }
      }
    }
  }
}
' http://localhost:55000/get_job_content

curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "job_options": {
      "job_name": "test",
      "wall_time_limit": "1:00:00 ",
      "node_count": 1,
      "process_count_per_node": 2,
      "standard_output_file": "test.out",
      "standard_error_file": "test.err",
      "combine_stdout_stderr": true,
      "copy_environment": true
    },
    "application": {
      "app_tag": "test",
      "executable": "bash -c \"cd modpy/build/lib/moduli/ && python3 main_mpi.py -s -f $PBS_O_WORKDIR/output/iso/L1L2-iso.dens -o $PBS_O_WORKDIR/output/moduli\"",
      "build": {
        "src": "$HOME/modpy/.git",
        "build_command": "bash -c \"cd modpy && pip3 --no-cache-dir install numpy pandas mpi4py --user && python3 setup.py install --user\""
      }
    },
    "target": {
      "name": "egi"
    }
  }
}
' http://localhost:55000/get_job_content




curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
      "app_type":"hpc",
      "opt_build": {
        "cpu_type": "x86",
        "acc_type": "none"
      },
      "app_type-hpc": {
        "config":{
          "parallelisation":"mpi"
        },
        "data":{
          "location": ""
        },
        "parallelisation-mpi": {
          "library": "mpich",
          "version": "3.1.4"
        }
      }
    }
  }
}'   http://localhost:55000/get_image




curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
      "app_type":"hpc",
      "opt_build": {
        "cpu_type": "x86",
        "acc_type": "none"
      },
      "app_type-hpc": {
        "config":{
          "parallelisation":"mpi"
        },
        "data":{
          "location": ""
        },
        "parallelisation-mpi": {
          "library": "openmpi",
          "version": "3.1.3"
        }
      }
    }
  }
}'   http://localhost:55000/get_image





curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "job_options": {
      "job_name": "test",
      "wall_time_limit": "1:00:00 ",
      "node_count": 1,
      "process_count_per_node": 2,
      "standard_output_file": "test.out",
      "standard_error_file": "test.err",
      "combine_stdout_stderr": true,
      "copy_environment": true
    },
    "application": {
      "app_tag": "test",
      "executable": "bash -c \"cd modpy/build/lib/moduli/ && python3 main_mpi.py -s -f $PBS_O_WORKDIR/output/iso/L1L2-iso.dens -o $PBS_O_WORKDIR/output/moduli\"",
      "build": {
        "src": "$HOME/modpy/.git",
        "build_command": "bash -c \"cd modpy && pip3 --no-cache-dir install numpy pandas mpi4py --user && python3 setup.py install --user\""
      }
    },
    "target": {
      "name": "egi"
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
          "library": "openmpi",
          "version": "3.1.3"
        }
      }
    }
  }
}
' http://77.231.202.209:5000/get_job_content

curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "job_options": {
      "job_name": "test",
      "wall_time_limit": "1:00:00 ",
      "node_count": 1,
      "process_count_per_node": 2,
      "standard_output_file": "test.out",
      "standard_error_file": "test.err",
      "combine_stdout_stderr": true,
      "copy_environment": true
    },
    "application": {
      "app_tag": "test",
      "executable": "bash -c \"cd modpy/build/lib/moduli/ && python3 main_mpi.py -s -f $PBS_O_WORKDIR/output/iso/L1L2-iso.dens -o $PBS_O_WORKDIR/output/moduli\"",
      "build": {
        "src": "$HOME/modpy/.git",
        "build_command": "bash -c \"cd modpy && pip3 --no-cache-dir install numpy pandas mpi4py --user && python3 setup.py install --user\""
      }
    },
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":true,
      "app_type":"hpc",
      "opt_build": {
        "cpu_type": "x86",
        "acc_type": "none"
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
          "library": "openmpi",
          "version": "3.1.3"
        }
      }
    }
  }
}
' http://77.231.202.209:5000/get_job_content

curl --fail --header "Content-Type: application/json" \
  --request POST \
  --data '{
  "job": {
    "job_options": {
      "job_name": "test",
      "wall_time_limit": "1:00:00 ",
      "node_count": 1,
      "process_count_per_node": 2,
      "standard_output_file": "test.out",
      "standard_error_file": "test.err",
      "combine_stdout_stderr": true,
      "copy_environment": true
    },
    "application": {
      "app_tag": "test",
      "executable": "bash -c \"cd modpy/build/lib/moduli/ && python3 main_mpi.py -s -f $PBS_O_WORKDIR/output/iso/L1L2-iso.dens -o $PBS_O_WORKDIR/output/moduli\"",
      "build": {
        "src": "$HOME/modpy/.git",
        "build_command": "bash -c \"cd modpy && pip3 --no-cache-dir install numpy pandas mpi4py --user && python3 setup.py install --user\""
      }
    },
    "target": {
      "name": "egi"
    }
  }
}
' http://77.231.202.209:5000/get_job_content




curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
      "app_type":"hpc",
      "opt_build": {
        "cpu_type": "x86",
        "acc_type": "none"
      },
      "app_type-hpc": {
        "config":{
          "parallelisation":"mpi"
        },
        "data":{
          "location": ""
        },
        "parallelisation-mpi": {
          "library": "mpich",
          "version": "3.1.4"
        }
      }
    }
  }
}'   http://77.231.202.209:5000/get_image




curl --fail --header "Content-Type: application/json"   --request POST   --data '{
  "job":{
    "optimisation": {
      "enable_opt_build": true,
      "enable_autotuning":false,
      "app_type":"hpc",
      "opt_build": {
        "cpu_type": "x86",
        "acc_type": "none"
      },
      "app_type-hpc": {
        "config":{
          "parallelisation":"mpi"
        },
        "data":{
          "location": ""
        },
        "parallelisation-mpi": {
          "library": "openmpi",
          "version": "3.1.3"
        }
      }
    }
  }
}'   http://77.231.202.209:5000/get_image