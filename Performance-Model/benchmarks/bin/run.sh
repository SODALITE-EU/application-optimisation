#!/bin/bash -e

help() {
    echo "Usage: $0 [-n <NPROCS>] [-s <submission command>] [-l <prefix output files>]"
    echo "Other options are:"
    echo "    -c : clean output files"
    echo "    -r : print results (if any)"
    echo "    -h : this help (default)"
    exit
}

print_stats() {
    res=(`find results -name "*$1*_hpccoutf.txt"`)
    if test ${#res[*]} -gt 0; then
	IFS=$'\n' res_sorted=($(sort -V <<<"${res[*]}")); unset IFS

	first=1
	for file in ${res_sorted[*]}; do
	    # Collect results
	    filename=$(basename ${file})
	    nnodes=`echo $filename | awk -F "_" '{print $1}' | tr -d "nodes"`
	    ppn=`echo $filename | awk -F "_" '{print $2}' | tr -d "ppn"`
	    nranks=`echo $filename | awk -F "_" '{print $3}' | tr -d "nranks"`
	    text="#nodes=$nnodes #ppn=$ppn #procs=$nranks "
	    text+=$(grep -e HPL_Tflops \
		-e StarSTREAM_Triad \
		-e RandomlyOrderedRingBandwidth_GByte \
		${file} | sort)
	    #	     -e RandomlyOrderedRingLatency_usec \
	    #	     -e AvgPingPongLatency_usec \
	    #	     -e AvgPingPongBandwidth_GByte \
	    #	     -e NaturallyOrderedRingLatency_usec \
	    #	     -e NaturallyOrderedRingBandwidth_GByte \
	    text+=$(grep "b_eff_io =" ${file/_hpccoutf.txt/_b_eff_io.sum} | awk '{ print " "$1"="$3 }')

	    labels=
	    values=
	    for value in $text; do
		labels+=`echo $value | cut -d'=' -f 1`" "
		values+=`echo $value | cut -d'=' -f 2`" "
	    done

	    if test $first -eq 1; then
		echo $labels
		first=0
	    fi
	    echo $values
	done
    else
	echo "No results!"
    fi
}

NP=1
SUBCMD="mpiexec -bind-to socket -map-by socket "
PRINT_STATS=0
no_args=1
while getopts "n:s:l:hcr" OPTION; do
    case $OPTION in
        n)
	    NP=$OPTARG
	    ;;
	s)
	    SUBCMD=$OPTARG
	    ;;
	l)
	    filelabel=$OPTARG
	    ;;
	c)
	    echo "Clean output files."
	    rm -rf results/* b_eff_io* hpccoutf.txt *.o*
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
    print_stats $filelabel
    exit
fi

# Check if the image exists
IMGNAME=benchmarks.imgdir
if test ! -d "$IMGNAME"; then
    echo "Image ${IMGNAME} doesn't exist"
    exit
fi

# Avoid threading
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export OMP_PROC_BIND=TRUE

# Run Apps
timestamp=$(date '+%Y%m%d%H%M')
filelabel=${filelabel:-"nodes-1_ppn-1_nranks${NP}"}
rundir=$(mktemp -d ${PWD}/results/results_${filelabel}_${timestamp}_XXXX)
for APP in hpcc beffio; do
    APP=$APP timestamp=$timestamp filelabel=$filelabel rundir=$rundir ${SUBCMD} -n ${NP} singularity run ${IMGNAME}
done
rm -rf $rundir
