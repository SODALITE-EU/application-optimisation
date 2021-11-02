# SnowUC SkylineExtraction-training

We have optimised the skyline extraction component for the Snow use case. The goal of this component is to obtain the landscape skyline of a photograph via a DL classification method run in TensorFlow. The dataset used for the training consists of 8,856 images with skyline annotations, from which 80% is used for training and validation and the remaining 20% for testing. The component was initially trained using TensorFlow 1.11. The training was performed with a baseline container taken from DockerHub (tensorflow/tensorflow:1.11.0-gpu-py3) and converged within approximately 7.2 hours on one GPU node of the HPC testbed (using single core execution). The training executed until convergence was achieved and early stopping initiated at epoch 20.

This directory contains:
- the GPU optimised SkylineExtraction-training code - `peaklens-gpuopt_training.py` - for Tensorflow 2.x
- our optimised TensorFlow for GPU Singularity container files
- the results of our experiments

Additionally, the code requires the `skyline-extraction-patches-dataset` upon which training is performed. This is available from the use-case owner at https://drive.google.com/file/d/1C_JgQa9d5RvfBlBGb19acEbsvCrmLpql/view .

## Python code
The python file `peaklens-gpuopt_training.py` was optimised for use with TensorFlow 2.x and uses Keras as its API. Before starting training, changes must be made to the input variables, in particular the datasets paths should be changed to point to the appropriate system paths:

```
DATASET_PATH = "/mnt/nfs/home/hpccrnm/soda/data/skyline/skyline-extraction-patches-dataset" #change to <path_to_dataset> 
```
The dataset path above is set to point to the local datast path. Should the dataset be located on a non-local storage - especially SSD - set the path accordingly and bing the dataset to Singularity during execution. 

Further possible changes include the `EPOCHS`, as well as enabling or disabling `prefetch` to the GPU.

## Containers
The TensorFlow containers are located under `/containers`. They can be built as follows:

```
# build container sandbox
singularity build --fakeroot --sandbox tensorflow_gpu/ gpu_tensorflow_2.2_opt_source_xla.def

# build non-interactive .sif container:
singularity build --fakeroot tensorflow_gpu.sif gpu_tensorflow_2.2_opt_source_xla.def
```

The containers must have access to the `gpu_ubuntu_base` container during build. Please also see the DL containers `Singularity container` README for further information. Note that our containers use an older numpy version (<19.0) due to a bug in the TensorFlow build. See here: https://github.com/tensorflow/tensorflow/issues/40688 .

The Docker TensorFlow container was pulled directly from Dockerhub. We pulled the container tagged `2.2.3-gpu` for our experiments. 

## Training

Once the setup is completed, the training is executed as follows:
```
singularity exec --nv <path_to_container> python3 <path_to_peaklens-gpuopt_training.py> 
```
If a non-local storage is used, binding is required using the Singularity `-B` flag: 
```
singularity exec -B <storage_path>:<storage_path_in_container> --nv <container_path> python3 <path_to_peaklens-gpuopt_training.py> 
```

