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

