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
cd $SLURM_SUBMIT_DIR
export PATH=$SLURM_SUBMIT_DIR:$PATH

file=set_default_egi.sh
if [ -f $file ] ; then rm $file; fi
wget --no-check-certificate https://www.dropbox.com/s/97h9zkj7uxx9sc5/set_default_egi.sh
chmod 755 set_default_egi.sh
source set_default_egi.sh

wget --no-check-certificate https://raw.githubusercontent.com/olcf/XC30-Training/master/affinity/Xthi.c

singularity exec $SINGULARITY_DIR/openmpi_3.1.3.sif  mpicc -o xthi -fopenmp Xthi.c

export OMP_NUM_THREADS=2
srun -n 80 singularity exec $SINGULARITY_DIR/openmpi_3.1.3.sif  ./xthi
