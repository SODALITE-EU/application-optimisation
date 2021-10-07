#!/bin/bash
## START OF HEADER ##
#SBATCH -J mpi_test_egi
#SBATCH --time=1:00:00
#SBATCH -N 2
#SBATCH --ntasks-per-node=1
#SBATCH --output=mpi_test.out
#SBATCH -error=mpi_test.err
#SBATCH --mail-type=abe
#SBATCH --mail-user=kartshy@gmail.com
## END OF HEADER ##

cd "${SLURM_SUBMIT_DIR}"
export PATH="${SLURM_SUBMIT_DIR}:${PATH}"
## MODAK: START HLRS TESTBED ##
module load mpi/openmpi-x86_64
## MODAK: END HLRS TESTBED ##


wget --no-check-certificate https://raw.githubusercontent.com/olcf/XC30-Training/master/affinity/Xthi.c

singularity exec "$SINGULARITY_DIR/openmpi_3.1.3.sif" mpicc -o xthi -fopenmp Xthi.c

export OMP_NUM_THREADS=2
srun -n 80 singularity exec "$SINGULARITY_DIR/openmpi_3.1.3.sif" ./xthi
