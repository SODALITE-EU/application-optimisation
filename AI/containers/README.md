# Singularity containers

Each framework and compiler combination is installed using two definition files:

- the OS base file - currently only one available, must always be used
- the FW/compiler file.

To build a complete container, follow the following recipe (change names as required):

```
# Enable fakeroot if necessary by mapping the user in (requires root permission!) 
vim /etc/subuid
vim /etc/subgid

# Build the base

singularity build --fakeroot --sandbox ubuntu_base/ ubuntu_base.def

# Build torch/glow on top:

singularity build --fakeroot --sandbox torch_pip_glow/ torch_pip_glow.def
```
Note that the container definition files expect the ubuntu base directory to be located in the working directory. Should this not be the case, change the relevant line in the definition file to reflect the change (see ``From:`` declaration).

To interactively test the created sandbox, one of the following commands can be used:
```
singularity shell <container_directory> # changes applied may influence all containers; e.g. installing a pip package will cause all other containers to use same package in this interactive mode
singularity shell --writable <container_directory> # changes applied to the container concern it exclusively
```

Besides the interactive builds, non-interactive single file images can be built for easy sharing. The commands are:
```
singularity build --fakeroot torch_pip_glow.sif torch_pip_glow.def
singularity build --fakeroot torch_pip_glow.sif torch_pip_glow/ # convert interactive sandbox to static container image
```

The FW/compiler definition files link to the directory name of the base image. If a different base image name is set, change the FW/compiler definition file to reflect the change (see "From:" header). The currently available definition files include:

* torch\_ubuntu\_base # base for all containers, including the tensorflow containers. Must be built before any FW container.
* pytorch containers:  
	- pytorch built from source
	- GLOW from source built on pytorch from source
	- GLOW from source built on pytorch from pip wheel
* tensorflow containers:
	- tensorflow + XLA from PIP container 
	- tensorflow + XLA from source
	- tensorflow + nGraph from PIP container

## Glow MNIST - tested

The glow MNIST files are coded in C++ and located in the directory /home/glow/build\_Debug/bin/mnist. To run them, the mnist database and the lenet_mnist set must be downloaded to the same working directory using the command:


```
singularity shell torch_pip_glow
mkdir $WORK_DIR
cd  $WORK_DIR
python /home/glow/utils/download_datasets_and_models.py -d mnist
python /home/glow/utils/download_datasets_and_models.py -c lenet_mnist
/home/glow/build_Debug/bin/mnist
```

To use the PyTorch installed from source containers, make sure to previously load the correct anaconda paths. To do so, use the .bashrc file located in the home directory:

```
source /home/.bashrc
```
## PyTorch MNIST (from source) - tested

```
# Build torch from source
singularity build --fakeroot --sandbox torch_source/ torch_source.def
```

MNIST can be tested as follows
```
singularity shell torch_source
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate
cd /home/examples/mnist/
python3 main.py
```

Once anaconda has been loaded, proceed with the previously mentioned workflow. 

Full details can be found in https://github.com/pytorch/glow .

## TensorFlow XLA (from source) - in progress

Build time for TensorFlow from source: approximately 45 minutes on sodalite testbed; multiple hours on local machine. 

Currently available sources of TF were built using:

```
tensorflow_2.0_source_xla.def
TF r2.0
bazel 0.26.1
gcc 7.3
```
```
tensorflow_2.0_opt_source_xla.def
TF r2.0
bazel 0.26.1
gcc 7.3
--config = opt
```
```
tensorflow_2.1_opt_source_xla.def
TF 2.1 # ! Not tied to specific TF version, pulls most current version of TF! MAY POSSIBLY BREAK WITH TF UPDATES
bazel 2.0.0 
gcc 8.0
--config = opt
```

After the build has finished, enter the container and manually execute the command:

```
cd /home/tensorflow
pip3 install tensorflow_pkg/tensorflow-[build].whl
```

## nGraph Tensorflow (PIP install) - in progress

Build the container as above using

```
singularity build --fakeroot --sandbox tensorflow_pip_ngraph/ tensorflow_pip_ngraph.def
```

Note that at current nGraph is only available for Tensorflow 1.14.

# GPU containers
To use the GPU, two prerequisites exist:
- the host must have the nvidia-drivers installed
- the container must have complementary nvidia-drivers, as well as any additional requirements (cuda, cudnn, etc) installed.

The second requirements is simplified by the singularity '--nv' flag. This option makes the containers more portable by bind mounting the hosts nvidia drivers into the container. Like this, a container can be moved to and used on a system that does not use the same nvidia-driver versions. 

To run a GPU container, it *must* be invoked using the nvidia --nv flag. 

```
singularity shell --nv <container>
```
Currently, two images can be used as the GPU base container - the nvidia Docker image, as well as the manually built image `gpu_ubuntu_base' located under the '/gpu' folder. The tensorflow GPU image is set to use the nvidia Docker image for speed purposes, but this can be changed by uncommenting the 'Bootstrap' and 'From' lines in the 'gpu_tensorflow_source.def' file. 

## Tensorflow GPU container

To test the Tensorflow GPU build, execute the following command in the python console:
```
tf.test.gpu_device_name()
```

The expected result should include information regarding the number of GPUs and GPU names, as well as libraries used. An example of this output for the testbed would be as follows:
```
>>> tf.test.gpu_device_name()
2020-05-18 12:37:53.329146: I tensorflow/core/platform/profile_utils/cpu_utils.cc:94] CPU Frequency: 2200000000 Hz
2020-05-18 12:37:53.336004: I tensorflow/compiler/xla/service/service.cc:168] XLA service 0x51d4eb0 initialized for platform Host (this does not guarantee that XLA will be used). Devices:
2020-05-18 12:37:53.336066: I tensorflow/compiler/xla/service/service.cc:176]   StreamExecutor device (0): Host, Default Version
2020-05-18 12:37:53.338973: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library libcuda.so.1
2020-05-18 12:37:53.491079: I tensorflow/compiler/xla/service/service.cc:168] XLA service 0x51d6c60 initialized for platform CUDA (this does not guarantee that XLA will be used). Devices:
2020-05-18 12:37:53.491125: I tensorflow/compiler/xla/service/service.cc:176]   StreamExecutor device (0): GeForce GTX 1080 Ti, Compute Capability 6.1
2020-05-18 12:37:53.492035: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1555] Found device 0 with properties: 
pciBusID: 0000:03:00.0 name: GeForce GTX 1080 Ti computeCapability: 6.1
coreClock: 1.582GHz coreCount: 28 deviceMemorySize: 10.92GiB deviceMemoryBandwidth: 451.17GiB/s
2020-05-18 12:37:53.494379: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library libcudart.so.10.1
2020-05-18 12:37:53.524638: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library libcublas.so.10
2020-05-18 12:37:53.551095: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library libcufft.so.10
2020-05-18 12:37:53.590217: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library libcurand.so.10
2020-05-18 12:37:53.616705: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library libcusolver.so.10
2020-05-18 12:37:53.637184: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library libcusparse.so.10
2020-05-18 12:37:53.687702: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library libcudnn.so.7
2020-05-18 12:37:53.689311: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1697] Adding visible gpu devices: 0
2020-05-18 12:37:53.689372: I tensorflow/stream_executor/platform/default/dso_loader.cc:44] Successfully opened dynamic library libcudart.so.10.1
2020-05-18 12:37:53.690541: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1096] Device interconnect StreamExecutor with strength 1 edge matrix:
2020-05-18 12:37:53.690563: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1102]      0 
2020-05-18 12:37:53.690574: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1115] 0:   N 
2020-05-18 12:37:53.692073: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1241] Created TensorFlow device (/device:GPU:0 with 10479 MB memory) -> physical GPU (device: 0, name: GeForce GTX 1080 Ti, pci bus id: 0000:03:00.0, compute capability: 6.1)
'/device:GPU:0'
```

## PyTorch GPU container

The PyTorch GPU container is built on top of the gpu_ubuntu_base image. Build it prior to this container, or set the bootstrap section to use the Docker nvidia container (note that the Docker container may not meet all dependencies and any missing package installs will have to be manually added to the gpu_torch_source.def file). 

To test whether PyTorch can call on the GPUs, use following command:
```
>>> torch.cuda.device_count()
1
>>> torch.cuda.get_device_name(0)
'GeForce GTX 1080 Ti'
```

## MXNet GPU container

Source build of MXNet container. Set to GPU and MKL DNN build using flags US_CUDA=1 and MKL_DNN=1. 
