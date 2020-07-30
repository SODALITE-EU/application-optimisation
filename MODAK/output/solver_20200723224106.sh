#!/bin/bash
## START OF HEADER ## 
#PBS -N solver
#PBS -l walltime=1:00:00 
#PBS -l nodes=2
#PBS -l procs=40
#PBS -l ppn=40
#PBS -o file.out
#PBS -e file.err
#PBS -j oe
#PBS -m abe
#PBS M kartshy@gmail.com
## END OF HEADER ## 
cd $PBS_O_WORKDIR

## START OF TUNER ##
wget --no-check-certificate https://storage.googleapis.com/modak//modak/solver_20200723224106_tune.sh

singularity exec ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof solver_20200723224106_tune.sh
## END OF TUNER ##

export OMP_NUM_THREADS=1

singularity exec ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof mpirun -np 40 ${ASTER_ROOT}/14.4/bin/aster  ${ASTER_ROOT}/14.4/lib/aster/Execution/E_SUPERV.py \
-commandes fort.1 --num_job=1432 --mode=interactif \
--rep_outils=${ASTER_ROOT}/outils \
--rep_mat=${ASTER_ROOT}/14.4/share/aster/materiau \
--rep_dex=${ASTER_ROOT}/14.4/share/aster/datg \
--numthreads=1 --suivi_batch --memjeveux=8192.0 --tpmax=3600.0
