singularity exec $1 mpicc -o mpitest mpitest.c
singularity exec $1 mpic++ -o heat_mpi heat_mpi.cpp
singularity exec $1 mpifort -o random_mpi random_mpi.f90

OMPI_MCA_plm_rsh_agent=sh singularity exec $1 mpirun -n 4 ./heat_mpi
OMPI_MCA_plm_rsh_agent=sh singularity exec $1 mpirun -n 4 ./mpitest
OMPI_MCA_plm_rsh_agent=sh singularity exec $1 mpirun -n 4 ./random_mpi
