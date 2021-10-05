#!/bin/bash -e

help() {
    echo "Usage: $0 [-l <label, e.g. cluster name>]"
    echo "Other optional options are:"
    echo "    -c : clean output files"
    echo "    -r : print results (if any)"
    echo "    -h : this help (default)"
    exit
}

ASTER_INPUT=L1L2_NonLinear_prepared

while getopts "l:hcr" OPTION; do
    case $OPTION in
	l)
	    LABEL=$OPTARG
	    ;;
	c)
	    echo "Clean output files."
	    rm -rf ${ASTER_INPUT}___*
	    exit
	    ;;
	r)
	    echo "show results"
	    grep -H TOTAL_JOB ${ASTER_INPUT}___*/aster___*.out | awk -F':' '{print $1":"$6}'
	    exit
	    ;;
	*|h)
	    help
        ;;
    esac
done

SUBCMD=${SUBCMD:-""}

# Avoid threading
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

# Check if the image exists
IMGBASENAME=code_aster_clinical
IMGNAME=${IMGBASENAME}.imgdir
if test ! -d "$IMGNAME"; then
    echo "Image ${IMGNAME} doesn't exist. Try SIF format..."
    IMGNAME=${IMGBASENAME}.sif
    if test ! -f "$IMGNAME"; then
	echo "Image ${IMGNAME} doesn't exist."
	exit
    fi
fi

# Run Apps
PREFIXNAME=${PREFIXNAME:-"nodes-1_ppn-1_nranks-1_nthreads-${OMP_NUM_THREADS}"}
# default label is the cluster name and the default queue
LABEL=${LABEL:-`echo $HOSTNAME | sed -e "s/[0-9]//g" | cut -f 1 -d '.'`"___default"}
LABEL=${PREFIXNAME}"___"${LABEL}
timestamp=$(date '+%Y%m%d%H%M')

ASTER_OUTPUT=${ASTER_INPUT}"___"$LABEL"___"$timestamp

rm -rf ${ASTER_OUTPUT}
cp -r ${ASTER_INPUT} ${ASTER_OUTPUT}

export ASTER_LOG=aster"___"$LABEL"___"$timestamp.out

${SUBCMD} singularity run ${IMGNAME} ${ASTER_OUTPUT}

