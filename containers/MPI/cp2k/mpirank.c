/*
   Get MPI rank
*/

#include <mpi.h>
#include <stdio.h>

int main( int argc, char *argv[])
{
  int myrank, nranks;

  MPI_Init(&argc,&argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &myrank); // get mynode
  MPI_Comm_size(MPI_COMM_WORLD, &nranks); // get totalnodes

  printf("%d:%d\n",myrank, nranks);

#ifdef OMPI_MAJOR_VERSION
  MPI_Finalize();
#endif

  return 0;
}
