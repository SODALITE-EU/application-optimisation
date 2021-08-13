This repository is used to build a Singularity image to be used for the Sodalite project, WP3 Performance modeling.

## Build the image
Two image configurations are provided, based on the MPI distributions:
* MPICH
* OpenMPI

A convenient [script](bin/build.sh) is provided for building the image:
```
> bin/build.sh
Choose which MPI distribution to use:
1) MPICH
2) OpenMPI
3) Quit
#?
```
Users can choose which MPI distribution to use and build the corresponding SIF image (default format), or they can use
```
USE_SB=1 bin/build.sh
```
to build a sandbox image format. Alternatively, they can directly build the MPICH image on their system with the command
```
cd build && sudo singularity build ../benchmarks.simg benchmarks.def # SIF format, requires root access
```
or
```
cd build && singularity build --sandbox --fakeroot ../benchmarks.imgdir benchmarks.def # Sandbox format, requires Singularity >=3.4.2
```

Also, we use gitlab-ci to automatically build the images. Any change to the [build files](build/) will trigger a build.
Then, the image files (only SIF format) are stored as artifacts.

**NOTE: in the following description only SIF format is used (`.simg` extension), however the commands are also valid for the sandbox format (`.imgdir` extension).**

## Download the pre-built image

You can use the script `bin/download`, which by default will download the MPICH image. You can specify `MPI_DIST=OpenMPI bin/download` to download the OpenMPI image.

Please specify your Gitlab personal access token by making a file `config/gitlab.conf`
and adding a line `GITLAB_PRIVATE_TOKEN=<your-private-token>`.
See this [page](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) on how to create a personal access token.

## Run the container

The image runs the [HPCC benchmark](https://icl.cs.utk.edu/hpcc/) and [b_eff_io](https://fs.hlrs.de/projects/par/mpi//b_eff_io/).
Currently, we only support the CPU execution.

The configuration file for the HPCC benchmark is [here](build/hpccinf.txt) and the options for the b_eff_io are [here](build/beffio_flags.txt).
These files are used by default (they are copied within the container), unless files with the same names are provided in the start run
directory of the Singularity container.

### Internal MPI in the container

You can run the container with

`NP=<# ranks> APP=<app> singularity run benchmarks.simg`

where `NP` specify the number of MPI ranks, `APP` can be `hpcc` or `beffio`.
At the end of the execution, the HPCC output is stored as `results/ranks<# ranks>_<timestamp>_hpccoutf.txt` file
and the b_eff_io outputs are `results/ranks<# ranks>_<timestamp>_b_eff_io.*`.

It can happen that you get a message like: `unable to open host file: /var/spool...`, in which case you have to mount `/var/`
within the container, e.g. `singularity run -B /var benchmarks.simg`.

### External MPI

A performant MPI implementation on the host can be used to run the container.
Requirement is the ABI compatibility between this version and the MPI within the container (MPICH 3.3.1 or OpenMPI 4.0.1).
A convenient script is provided [run.sh](bin/run.sh), e.g.

`bin/run.sh -n 2 -s "mpirun" -l "mycluster"`

where `-n` sets the number of ranks (default is 1), `-s` is the submission command (default is `mpiexec -bind-to socket -map-by socket`),
and `-l` is the name of the cluster which will be part of results file name (the default is based on the output of the `hostname` command). It is also possible to specify a submission queue with the `-q` flag. Use `-h` flag to see the help.
The script runs the two benchmarks and puts the results into the directory `results`. See below on how to analyze them.

#### Batch submission

A convenient [script](bin/submit.sh) is provided for submit the benchmarks execution on a cluster:

`bin/submit.sh -n <# nodes> -p <# ranks per node>`.

Multiple values can be specified, e.g. `bin/submit.sh -n "1 2" -p "18 36"`. Then, the script will submit all combinations.
Currently, the script supports `SLURM` and `PBS/Torque`, with some default options. Other batch systems can be added to the script, as well as
specific flags based on the cluster.

## Result analysis

You can see the results via (CSV format)
```
bin/run.sh -r
cluster, queue, timestamp, #nodes, #ppn, #procs, HPL_Tflops, RandomlyOrderedRingBandwidth_GBytes, StarSTREAM_Triad, b_eff_io
alazzaro-VB-maccray, default, 202008131129, -1, -1, 1, 0.0229369, -1, 28.1998, 1228.178
alazzaro-VB-maccray, default, 202008131129, -1, -1, 2, 0.0369765, 6.94895, 18.9876, 862.461
```
(Here the value `-1` means the value is not available)
It can be combined with the flag `-l <label>` to select results with a particular label (the default is based on the output of the `hostname` command) and the the submission queue with the `-q` flag. Use `-h` flag to see the help.

It is possible to delete the results files with

```
bin/run.sh -c
```
