#PBS -S /bin/bash
## START OF HEADER ##
#PBS -N mpi_test
#PBS -l walltime=1:00:00
#PBS -l nodes=2:ppn=40
#PBS -l procs=40
#PBS -o mpi_test.out
#PBS -e mpi_test.err
#PBS -j oe
#PBS -m abe
#PBS -M kartshy@gmail.com
## END OF HEADER ##
cd $PBS_O_WORKDIR
export PATH=$PBS_O_WORKDIR:$PATH

wget --no-check-certificate https://raw.githubusercontent.com/olcf/XC30-Training/master/affinity/Xthi.c

singularity exec "$SINGULARITY_DIR/mpich_ub1804_cuda101_mpi314_gnugprof.sif" mpicc -o xthi -fopenmp Xthi.c

export OMP_NUM_THREADS=2
mpirun -np 80 singularity exec "$SINGULARITY_DIR/mpich_ub1804_cuda101_mpi314_gnugprof.sif" ./xthi
