#!/bin/bash -e

help() {
    echo "Usage: $0 [-l <label, e.g. cluster name>]"
    echo "Other optional options are:"
    echo "    -c : clean output files"
    echo "    -t : number of threads"
    echo "    -r : print results (if any)"
    echo "    -h : this help (default)"
    exit
}

print_stats() {
    echo "show results"
    echo
    REGEX="${1}*/cp2k_rpa___*.out"
    res=(`for f in $(ls ${REGEX} 2>/dev/null); do echo $f; done`)
    if test ${#res[*]} -gt 0; then
	echo "testtype,mpidist,cluster,queue,timestamp,nnodes,ppn,nranks,nthreads,time"
        IFS=$'\n' res_sorted=($(sort -V <<<"${res[*]}")); unset IFS
	for file in ${res_sorted[*]}; do
	    # Collect results
	    dirn=$(dirname ${file})
	    testtype=`echo $dirn | awk -F "___" '{print $1}'`
	    mpidist=`echo $dirn | awk -F "___" '{print $2}'`
	    cluster=`echo $dirn | awk -F "___" '{print $4}'`
	    queue=`echo $dirn | awk -F "___" '{print $5}'`
            timestamp=`echo $dirn | awk -F "___" '{print $6}'`

            filename=$(basename ${file})
	    stats=`echo $filename | awk -F "___" '{print $3}'`
	    nnodes=`echo $stats | awk -F "_" '{print $1}' | tr -d "nodes-"`
            ppn=`echo $stats | awk -F "_" '{print $2}' | tr -d "ppn-"`
            nranks=`echo $stats | awk -F "_" '{print $3}' | tr -d "nranks-"`
            nthreads=`echo $stats | awk -F "_" '{print $4}' | tr -d "nthreads-"`

	    wtime=`grep -H "CP2K    " $file | awk '{print $7}' | xargs`

	    echo $testtype,$mpidist,$cluster,$queue,$timestamp,$nnodes,$ppn,$nranks,$nthreads,$wtime
	done
    else
        echo "No results ${REGEX}!"
    fi
}

CP2K_LABEL="cp2k_rpa"

PRINT_STATS=0

NSHIFT=0

while getopts "l:t:hcr" OPTION; do
    case $OPTION in
	l)
	    LABEL=$OPTARG
	    NSHIFT=$((NSHIFT+2))
	    ;;
	t)
	    export OMP_NUM_THREADS=$OPTARG
	    NSHIFT=$((NSHIFT+2))
	    ;;
	c)
	    echo "Clean output files."
	    rm -rf ${CP2K_LABEL}*
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

shift $NSHIFT

if test ${PRINT_STATS} -eq 1; then
    print_stats "${LABEL:-$CP2K_LABEL}"
    exit
fi

SUBCMD=${SUBCMD:-""}

if [ -z "${IMGBASENAME}" ]; then
    BASEDIR=$(dirname "$0")
    . ${BASEDIR}/selection.sh
fi

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

CP2K_OUTPUT=${CP2K_LABEL}"___"${CHOICE}"___"$LABEL"___"$timestamp

rm -rf ${CP2K_OUTPUT}
cp -r inputs ${CP2K_OUTPUT}

cd ${CP2K_OUTPUT}
${SUBCMD} singularity run --nv ../${IMGNAME} "-i H2O-32-RI-dRPA-TZ.inp -o ${CP2K_OUTPUT}.out"
cd ..
