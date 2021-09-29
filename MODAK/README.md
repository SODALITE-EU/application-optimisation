# MODAK Application Optimizer


## Containers, performance model, and database preparation

For a given application and hardware, an optimized container (Singularity format) is built by an expert and pushed to an image registry. Then, its location and optimizations are recorded in a database. The expert also builds the performance model for that container. MODAK is used to retrive this information. Singularity was chosen to provide a portable and reproducible runtime for the application deployment, due to better performance and native support for
HPC systems.

## MODAK components

MODAK has four main components, as described below:

-   **Mapper.** Containers provide an optimized runtime for application deployment based on the target hardware and along with any software dependencies and libraries. MODAK labels containers with appropriate optimization. The Mapper maps application deployment to an optimized container runtime based on the required optimisation. Currently, MODAK supports TensorFlow, PyTorch, MXnet, mpich, and openmpi containers for x86 and NVIDIA GPUs. These containers are further labelled with version requirements and support for optimizations like graph compilers or BLAS/LAPACK.

-   **Enforcer.** The Enforcer optimizes the deployment based on optimization rules defined by users and optimization DSL
  inputs. Rules can be defined for targets, applications, libraries, and data. The Enforcer component generates
  an optimization script that is then added to the deployment.

-   **Autotuning.** It enables users to automatically search possible application deployments for the desired result. Parameters are exposed as environment variables or configuration options for the applications.

-   **Scaler.** In MODAK, we can predict the efficiency and speedup of an application on N nodes based on the performance
prediction model. This allows MODAK to automatically scale applications to certain numbers of nodes based
on the model prediction. Using the parallel efficiency metric specified by the user in the optimisation DSL,
the Scaler aims to predict the scale at which parallel efficiency is achieved and automatically increase the number of nodes of the deployment (Autoscale). The Scaler can also enable or disable accelerator, memory, and storage devices based on the model and availability in the target.

## Usage

MODAK requires the following inputs:

-   Job submission options for batch schedulers such as SLURM and TORQUE
-   Application configuration such as application name, run and build command
-   Infrastructure configuration such as target name, type and scheduler type
-   Optimization DSL with specification of target hardware, software libraries and optimizations to encode. Also contains inputs for auto-tuning and scaling.

MODAK output consists of:

-   a job script (for batch submission)
-   the path of the optimized container
-   the scaling efficiency (for an MPI parallel application)
-   Set of autotuning parameters

### Server API and database

A [database](db) is provided for checking purposes.  It requires a MariaDB/MySQL server running, hence Docker is recommended (minimal version 18.09). The same container deploy the MODAK API server.
```console
$ docker build -t modakopt/modak:api .
$ docker-compose up
```
MODAK is provided as a Python module. An example is provided [here](examples/example.py). You can run it by opening a shell within the container:
```console
$ docker exec -ti modak_restapi_1 /bin/bash
$ examples/example.py
This is the MODAK driver program
JobScripts(jobscript=PosixPath('output/mpi_test_20210929104842.sh'), buildscript='output/mpi_test_build_20210929104842.sh')
```
The output are two job submission scripts that you can use to submit to a batch scheduler like SLURM or Torque.
MODAK expects the singularity containers to be pulled in to `$SINGULARITY_DIR` (define the directory).
