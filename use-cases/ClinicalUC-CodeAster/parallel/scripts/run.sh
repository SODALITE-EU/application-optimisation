#!/bin/bash -e

help() {
    echo "Usage: $0 [-l <label, e.g. cluster name>]"
    echo "Other optional options are:"
    echo "    -c : clean output files"
    echo "    -r : print results (if any)"
    echo "    -h : this help (default)"
    exit
}

print_stats() {
    echo "show results"
    echo
    REGEX="${1}*/aster___*.out"
    res=(`for f in $(ls ${REGEX} 2>/dev/null); do echo $f; done`)
    if test ${#res[*]} -gt 0; then
	echo "testtype,testalgo,mpidist,cluster,queue,timestamp,nnodes,ppn,nranks,nthreads"
        IFS=$'\n' res_sorted=($(sort -V <<<"${res[*]}")); unset IFS
	for file in ${res_sorted[*]}; do
	    # Collect results
	    dirn=$(dirname ${file})
	    testtype=`echo $dirn | awk -F "___" '{print $1}'`
	    testalgo=`echo $dirn | awk -F "___" '{print $2}'`
	    mpidist=`echo $dirn | awk -F "___" '{print $3}'`
	    cluster=`echo $dirn | awk -F "___" '{print $5}'`
	    queue=`echo $dirn | awk -F "___" '{print $6}'`
            timestamp=`echo $dirn | awk -F "___" '{print $7}'`

            filename=$(basename ${file})
	    stats=`echo $filename | awk -F "___" '{print $2}'`
	    nnodes=`echo $stats | awk -F "_" '{print $1}' | tr -d "nodes-"`
            ppn=`echo $stats | awk -F "_" '{print $2}' | tr -d "ppn-"`
            nranks=`echo $stats | awk -F "_" '{print $3}' | tr -d "nranks-"`
            nthreads=`echo $stats | awk -F "_" '{print $4}' | tr -d "nthreads-"`

	    wtime=`grep -H TOTAL_JOB $file | awk -F':' '{print $6}' | awk -F'*' '{print $1}' | xargs`

	    echo $testtype,$testalgo,$mpidist,$cluster,$queue,$timestamp,$nnodes,$ppn,$nranks,$nthreads,$wtime
	done
    else
        echo "No results ${REGEX}!"
    fi
}

#export ASTER_DIR=L1L2_NonLinear_prepared
#export ASTER_INPUT="fort.1"
export ASTER_DIR="Case_prep-3_Segments-4mm-2mm"
#export ASTER_INPUT="Case_prep-3_Segments_4mm_2mm-DM_CENTRALISE.com"
#export ASTER_INPUT="Case_prep-3_Segments_4mm_2mm-DM_SOUS_DOMAINE_METIS.com"
export ASTER_INPUT="Case_prep-3_Segments_4mm_2mm-DM_SOUS_DOMAINE_METIS_PETSC.com"

ASTER_LABEL=${ASTER_DIR}___${ASTER_INPUT}

PRINT_STATS=0

while getopts "l:hcr" OPTION; do
    case $OPTION in
	l)
	    LABEL=$OPTARG
	    shift 2
	    ;;
	c)
	    echo "Clean output files."
	    rm -rf ${ASTER_LABEL}*
	    exit
	    ;;
	r)
	    PRINT_STATS=1
	    ;;
	*|h)
	    help
        ;;
    esac
done

if test ${PRINT_STATS} -eq 1; then
    print_stats "${LABEL:-$ASTER_LABEL}"
    exit
fi

SUBCMD=${SUBCMD:-""}

if [ -z "${IMGBASENAME}" ]; then
    BASEDIR=$(dirname "$0")
    . ${BASEDIR}/selection.sh
fi

# Avoid threading
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1

# Check if the image exists
IMGBASENAME+="_$CHOICE"
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
timestamp=$(date '+%Y%m%d%H%M%S')

ASTER_OUTPUT=${ASTER_LABEL}"___"${CHOICE}"___"$LABEL"___"$timestamp

rm -rf ${ASTER_OUTPUT}
cp -r ../inputs/${ASTER_DIR} ${ASTER_OUTPUT}

export ASTER_LOG=aster"___"$LABEL"___"$timestamp.out

${SUBCMD} singularity run ${IMGNAME} ${ASTER_OUTPUT}

