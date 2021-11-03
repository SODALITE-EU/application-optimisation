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
# MODAK: Start Script<id=80593ce7-fc40-4e1d-988d-84c38930f8e5>
module load mpi/openmpi-x86_64
# MODAK: End   Script<id=80593ce7-fc40-4e1d-988d-84c38930f8e5>

wget --no-check-certificate https://raw.githubusercontent.com/olcf/XC30-Training/master/affinity/Xthi.c

singularity exec "$SINGULARITY_DIR/openmpi_3.1.3.sif" mpicc -o xthi -fopenmp Xthi.c

export OMP_NUM_THREADS=2
srun -n 80 singularity exec "$SINGULARITY_DIR/openmpi_3.1.3.sif" ./xthi
