#!/bin/bash -e

CLUSTER=`echo $HOSTNAME | sed -e "s/[0-9]//g" | cut -f 1 -d '.'`
NNODES=1
PPN=1
wtime="1:00:00"
LABEL=""

while getopts "n:p:l:w:" OPTION; do
    case $OPTION in
	n)
	    NNODES=$OPTARG
	    ;;
	p)
	    PPN=$OPTARG
	    ;;
	l)
	    LABEL=$OPTARG
	    ;;
	w)
	    wtime=$OPTARG
	    ;;
	?)
	    exit
	    ;;
    esac
done

WLM=
set +e
if test `command -v qsub` > /dev/null; then
    echo "PBS recongnized on $CLUSTER"
    WLM="pbs"
    BATCH_CMD_PREFIX="qsub -j oe -V -l naccesspolicy=singlejob -lwalltime=${wtime} "
elif test `command -v sbatch` > /dev/null; then
    echo "SLURM recongnized on $CLUSTER"
    WLM="slurm"
    BATCH_CMD_PREFIX="sbatch -t ${wtime} --ntasks-per-core=1 --exclusive -D ${PWD} "
else
    echo "Batch system not recongnized!"
    exit
fi
set -e

# Specific options per cluster
SUBCMD=
case $CLUSTER in
    daint)
	BATCH_CMD_PREFIX+="--account=uzh1 --constraint=mc --switches=1@01:00:00 "
	SUBCMD="srun --hint=nomultithread "
    ;;
esac

if test ! -z "${SUBCMD}"; then
    SUBCMD="-s '${SUBCMD}'"
fi

NAMEOUT_PREFIX=perfbench

for inode in $NNODES; do
    for ippn in $PPN; do
	TEXT="nodes${inode}_ppn${ippn}_ranks$(( inode * ippn ))"
	if test ! -z "${LABEL}"; then
	    TEXT+="_"${LABEL}
	fi
	echo $TEXT

	BATCH_CMD=${BATCH_CMD_PREFIX}
	case $WLM in
	    pbs)
		BATCH_CMD+="-lnodes=${inode}:ppn=${ippn} "
		BATCH_CMD+="-N ${NAMEOUT_PREFIX}_${TEXT} "
		;;
	    slurm)
		BATCH_CMD+="--nodes=${inode} --ntasks-per-node=${ippn} --ntasks=$(( inode * ippn )) -J ${NAMEOUT_PREFIX}_${TEXT} "
		BATCH_CMD+="-o ${NAMEOUT_PREFIX}_${TEXT}.o%j "
		;;
	esac

	echo "Submission command: ${BATCH_CMD}"

	${BATCH_CMD} <<EOF
#!/bin/bash -l
echo "Submission command: ${BATCH_CMD}"

cd $PWD

$PWD/bin/run.sh -n $(( inode * ippn )) -l ${TEXT} ${SUBCMD}

EOF

    done
done
