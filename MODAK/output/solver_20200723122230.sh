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
