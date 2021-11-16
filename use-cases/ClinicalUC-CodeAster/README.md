# Code-Aster containers	
There are 3 directories:
*  **Serial**: this	is the serial plain installation of Code-Aster
*  **Reference**: this is the [Dockerhub](https://hub.docker.com/u/codeastersolver) version of the Code-Aster
*  **Parallel**: parallel build of Code-Aster

These directories have two subdirectories:
*  **def**: it contains what is needed to build the containers (e.g. definition file)
*  **scripts**: scripts used to build, run, and submit the containers in batch

Then the directory **inputs** contains the Code-Aster input simulations.

For example, we can build a parallel container with the following commands:
1.  Move inside the corresponding directory `parallel`
2.  `scripts/build.sh`

By default it builds a SIF image, which requires SUDO. Otherwise, you can specify `USE_SB=1 scripts/build.sh` to build a sandbox (rootless) image. Only for the parallel containers, the script will request which MPI implementation to use (MPICH, OpenMPI).
Then, it is possible to run the container via `scripts/run.sh`, which will run on the local node. Use the `-h` option to get an help on possible configurations.
Alternatively, it is possible to submit the execution in batch via `scripts/submit.sh`. Possible flags are: `-n` to specify the number of nodes, `-p` to specify the number of ranks per node.

At the end of the execution, you will get a directory with the outputs of the execution (e.g. `Case_prep-3_Segments-4mm-2mm___Case_prep-3_Segments_4mm_2mm-DM_CENTRALISE.com___MPICH___nodes-1_ppn-1_nranks-1-nthreads-1___cloudserver___default___202111152147`), which specify: the name of the input data directory as taken from `inputs` directory (e.g. `Case_prep-3_Segments-4mm-2mm`), the name of the test to execute (e.g. `Case_prep-3_Segments_4mm_2mm-DM_CENTRALISE.com`), the MPI implementation (e.g. `MPICH`), the number of nodes and ranks per node (e.g. `nodes-1_ppn-1_nranks-1-nthreads-1`), the system name (e.g. `cloudserver`), the compute queue (e.g. `default`), a timestamp when the job is submitted (e.g. `202111152147`).

Finally, execution time can be inspected via `scripts/run.sh -r`, e.g.:

```
$ scripts/run.sh -r
show results
Case_prep-3_Segments-4mm-2mm___Case_prep-3_Segments_4mm_2mm-DM_CENTRALISE.com___MPICH___nodes-1_ppn-1_nranks-1-nthreads-1___cloudserver___default___202111152147/aster___nodes-1_ppn-1_nranks-1-nthreads-1___cloudserver___default___202111152147.out:    1099.78 *
Case_prep-3_Segments-4mm-2mm___Case_prep-3_Segments_4mm_2mm-DM_CENTRALISE.com___MPICH___nodes-1_ppn-4_nranks-4-nthreads-1___cloudserver___default___202111152155/aster___nodes-1_ppn-4_nranks-4-nthreads-1___cloudserver___default___202111152155.out:     473.32 *
```
