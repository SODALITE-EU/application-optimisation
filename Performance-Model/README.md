This repository is used to build a Singularity image to be used for the Sodalite project, WP3 Performance modeling.
The original repository is at https://gitlab.com/cerl/containers/sodalite/benchmarks.


## Build the image
We use gitlab-ci to build the image. Any change to the [Singularity definition file](build/benchmarks.def) will trigger a build of the image.
Then the image file is stored as artifacts.

Alternatively, you can build it on your system with the command
```
sudo singularity build benchmarks.sif build/benchmarks.def # Requires root access
```
or
```
singularity build --sandbox --fakeroot benchmarks.imgdir build/benchmarks.def # Requires Singularity 3.4.2
```

## Download the image

You can use the script `bin/download`. Please specify your Gitlab personal access token by making a file `config/gitlab.conf` 
and adding a line `GITLAB_PRIVATE_TOKEN=<your-private-token>`.
See this [page](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) on how to create a personal access token.

## Run the image

The image runs the [HPCC benchmark](https://icl.cs.utk.edu/hpcc/) and [b_eff_io](https://fs.hlrs.de/projects/par/mpi//b_eff_io/).
Currently, we only support the CPU execution.

The configuration file for the HPCC benchmark is [here](hpccinf.txt) and the options for the b_eff_io are [here](beffio_flags.txt).

### Internal MPI in the container

You can run the container with 

`singularity run benchmarks.imgdir`

which runs with a single MPI rank, or 

`NP=<# ranks> APP=<app> singularity run benchmarks.imgdir`

where `NP` specify the number of MPI ranks, <app> can be `hpcc` or `beffio`.
At the end of the execution, the HPCC output is stored as `results/ranks<# ranks>_<timestamp>_hpccoutf.txt` file 
and the b_eff_io outputs are `results/ranks<# ranks>_<timestamp>_b_eff_io.*`.

It can happen that you get a message like: `unable to open host file: /var/spool...`, in which case you have to mount `/var/`
within the container, e.g. `singularity run -B /var benchmarks.imgdir`.

### External MPI

A performant MPI implementation on the host can be used to run the container.
Requirement is the ABI compatibility between this version and the MPI within the container (MPICH 3.3.1).
A convenient script is provided [run.sh](bin/run.sh), e.g.

`bin/run.sh -n 2 -s "mpirun"`

where `-n` sets the number of ranks and `-s` the submission command.
The script runs the two benchmarks, grep the results, and put them in a file `results/ranks<# ranks>_<timestamp>.res` file.

