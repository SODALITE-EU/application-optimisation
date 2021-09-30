#!/bin/bash
#
#SBATCH --job-name=skyline
#SBATCH --output=slurm-%j.out
#
#SBATCH --ntasks=1
#SBATCH --time=10:00:00
#SBATCH -p spider
#SBATCH -C V100
#SBATCH --error=slurm-%j.err

module load craype-ml-plugin-py2/gnu49/1.1.4
module load gcc/4.9.1
module load cudatoolkit/9.2      
module load openmpi/gcc/3.0.0 
module use /cray/css/users/dctools/modulefiles
module load anaconda2
module list
export LD_LIBRARY_PATH=/home/users/ksivalinga/cuda/lib64:$LD_LIBRARY_PATH
XLA_FLAGS="--xla_hlo_profile --xla_dump_to=/lus/scratch/ksivalinga/TF/training/tmp/foo --xla_dump_hlo_as_text"
srun python mnist_softmax_xla.py >> training-$SLURM_JOB_ID
