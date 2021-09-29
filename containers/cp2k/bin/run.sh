#!/bin/bash -e

help() {
    echo "Usage: $0 [-n <NPROCS>] [-s <submission command>] [-l <label, e.g. cluster name>] [-q <queue>] -i <CP2K input>"
    echo "Other options are:"
    echo "    -c : clean output files"
    echo "    -r : print results (if any)"
    echo "    -h : this help (default)"
    echo "All options are optional."
    exit
}

NP=1
SUBCMD="mpiexec -bind-to socket -map-by socket "
no_args=1
INPUT=
while getopts "n:s:l:q:i:h" OPTION; do
    case $OPTION in
        n)
	    NP=$OPTARG
	    ;;
	s)
	    SUBCMD=$OPTARG
	    ;;
	l)
	    LABEL=$OPTARG
	    ;;
	q)
	    QUEUE=$OPTARG
	    ;;
	i)
	    INPUT=$OPTARG
	    ;;
	*|h)
	    help
        ;;
    esac
    no_args=0
done

if test ${no_args} -eq 1; then
    help
fi

LABEL=${LABEL:-`echo $HOSTNAME | sed -e "s/[0-9]//g" | cut -f 1 -d '.'`}
QUEUE=${QUEUE:-"default"}

# Check if the image exists
IMGBASENAME=cp2k
IMGNAME=${IMGBASENAME}.imgdir
if test ! -d "$IMGNAME"; then
    echo "Image ${IMGNAME} doesn't exist. Try SIF format..."
    IMGNAME=${IMGBASENAME}.simg
    if test ! -f "$IMGNAME"; then
	echo "Image ${IMGNAME} doesn't exist."
	exit
    fi
fi

# Avoid threading
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export OMP_PROC_BIND=TRUE

# Check that the container # ranks are as requested
NRANKS_CONTAINER=`${SUBCMD} -n ${NP} singularity exec ${IMGNAME} bash -c '${MYWORKDIR}/bin/mpirank' | cut -d':' -f 2 | uniq`
if test "${NRANKS_CONTAINER}" != "${NP}"; then
    echo "Something went wrong with MPI inside the container!"
    echo "Requested ${NP} ranks, recongnized ${NRANKS_CONTAINER} ranks"
    exit -1
fi

if test -z ${INPUT}; then
    echo "Require to specify a CP2K input file!"
    help
fi

# Run
${SUBCMD} -n ${NP} singularity run ${IMGNAME} ${INPUT}
