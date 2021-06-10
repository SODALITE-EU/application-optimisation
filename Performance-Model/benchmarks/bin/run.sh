#!/bin/bash -e

help() {
    echo "Usage: $0 [-n <NPROCS>] [-s <submission command>] [-l <label, e.g. cluster name>] [-q <queue>]"
    echo "Other options are:"
    echo "    -c : clean output files"
    echo "    -r : print results (if any)"
    echo "    -h : this help (default)"
    echo "All options are optional."
    exit
}

print_stats() {
    REGEX="*___$1___$2___*___hpccoutf.txt"
    res=(`find results -name "${REGEX}"`)
    if test ${#res[*]} -gt 0; then
	IFS=$'\n' res_sorted=($(sort -V <<<"${res[*]}")); unset IFS

	first=1
	for file in ${res_sorted[*]}; do
	    # Collect results
	    filename=$(basename ${file})
	    cluster=`echo $filename | awk -F "___" '{print $2}'`
	    queue=`echo $filename | awk -F "___" '{print $3}'`
	    text="cluster=$cluster queue=$queue "
	    nnodes=`echo $filename | awk -F "_" '{print $1}' | tr -d "nodes"`
	    ppn=`echo $filename | awk -F "_" '{print $2}' | tr -d "ppn"`
	    nranks=`echo $filename | awk -F "_" '{print $3}' | tr -d "nranks"`
	    timestamp=`echo $filename | awk -F "___" '{print $4}'`
	    text+="timestamp=$timestamp #nodes=$nnodes #ppn=$ppn #procs=$nranks "
	    text+=$(grep -e HPL_Tflops \
		-e StarSTREAM_Triad \
		-e RandomlyOrderedRingBandwidth_GByte \
		${file} | sort)
	    #	     -e RandomlyOrderedRingLatency_usec \
	    #	     -e AvgPingPongLatency_usec \
	    #	     -e AvgPingPongBandwidth_GByte \
	    #	     -e NaturallyOrderedRingLatency_usec \
	    #	     -e NaturallyOrderedRingBandwidth_GByte \
	    if test -f ${file/_hpccoutf.txt/_b_eff_io.sum}; then
		text+=$(grep "b_eff_io =" ${file/_hpccoutf.txt/_b_eff_io.sum} | awk '{ print " "$1"="$3 }')
	    else
		text+=" b_eff_io=-1"
	    fi

	    labels=
	    values=
	    sep=""
	    for value in $text; do
		labels+=${sep}`echo ${value} | cut -d'=' -f 1`
		values+=${sep}`echo ${value} | cut -d'=' -f 2`
		sep=", "
	    done

	    if test $first -eq 1; then
		echo $labels
		first=0
	    fi
	    echo $values
	done
    else
	echo "No results ${REGEX}!"
    fi
}

NP=1
SUBCMD="mpiexec -bind-to socket -map-by socket "
PRINT_STATS=0
no_args=1
while getopts "n:s:l:q:hcr" OPTION; do
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
	c)
	    echo "Clean output files."
	    rm -rf results/* b_eff_io* hpccoutf.txt *.o* *.sum *.prot perfbench*.o*
	    exit
	    ;;
	r)
	    PRINT_STATS=1
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

if test ${PRINT_STATS} -eq 1; then
    print_stats "${LABEL:-*}" "${QUEUE:-*}"
    exit
fi

LABEL=${LABEL:-`echo $HOSTNAME | sed -e "s/[0-9]//g" | cut -f 1 -d '.'`}
QUEUE=${QUEUE:-"default"}

# Check if the image exists
IMGNAME=benchmarks.imgdir
if test ! -d "$IMGNAME"; then
    echo "Image ${IMGNAME} doesn't exist. Try SIF format..."
    IMGNAME=benchmarks.simg
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
NRANKS_CONTAINER=`${SUBCMD} -n ${NP} singularity exec ${IMGNAME} bash -c '${BINDIR}/mpirank' | cut -d':' -f 2 | uniq`
if test "${NRANKS_CONTAINER}" != "${NP}"; then
    echo "Something went wrong with MPI inside the container!"
    echo "Requested ${NP} ranks, recongnized ${NRANKS_CONTAINER} ranks"
    exit -1
fi

# Run Apps
PREFIXNAME=${PREFIXNAME:-"nodes-1_ppn-1_nranks${NP}"}
LABEL=${PREFIXNAME}"___"${LABEL}"___"${QUEUE}
timestamp=$(date '+%Y%m%d%H%M')
rundir=$(mktemp -d ${PWD}/results/results___${LABEL}___${timestamp}___XXXX)
for APP in hpcc beffio; do
    APP=$APP timestamp=$timestamp filelabel=$LABEL rundir=$rundir ${SUBCMD} -n ${NP} singularity run ${IMGNAME}
done
rm -rf $rundir
