#!/bin/bash -e

CLUSTER=`echo $HOSTNAME | sed -e "s/[0-9]//g" | cut -f 1 -d '.'`
NNODES=1
PPN=1
wtime="2:00:00"
LABEL=${CLUSTER}
QUEUE="default"

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
	q)
            QUEUE=$OPTARG
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
if test `command -v sbatch` > /dev/null; then
    echo "SLURM recongnized on $CLUSTER"
    WLM="slurm"
    BATCH_CMD_PREFIX="sbatch -t ${wtime} --ntasks-per-core=1 --exclusive -D ${PWD} "
elif test `command -v qsub` > /dev/null; then
    echo "PBS recongnized on $CLUSTER"
    WLM="pbs"
    BATCH_CMD_PREFIX="qsub -j oe -l naccesspolicy=singlejob -lwalltime=${wtime} "
else
    echo "Batch system not recongnized!"
    exit
fi
set -e

export SUBCMD="mpiexec -bind-to socket -map-by socket "
# Specific options per cluster
case $CLUSTER in
    daint)
	export MODULES="daint-mc singularity"
	export SINGULARITY_BIND=/lib64,/opt/cray,/usr/lib64
	export MPICH_GNI_MALLOC_FALLBACK=1 # drop hugepage support within the container
	QUEUE=mc
	BATCH_CMD_PREFIX+="--account=cray --constraint=${QUEUE} --switches=1@01:00:00 "
	export SUBCMD="srun --hint=nomultithread "
	;;
    osprey)
	export MODULES="singularity/3.2.1 openmpi/gcc/4.0.1"
	export IBDEVICES='mlx5_0'
	QUEUE=bdw18
	BATCH_CMD_PREFIX+="-p ${QUEUE} "
	export SUBCMD="mpirun -bind-to socket -map-by socket --mca oob_tcp_if_include ib0 --mca btl_tcp_if_include ib0 "
	;;
    cloudserver) # HLRS testbed
	export MODULES="compilers/gcc-9.2.0 mpi/mpich-3.3.1-gcc-9.2.0"
	export SUBCMD="mpiexec "
	;;
esac

NAMEOUT_PREFIX=code_aster

for inode in $NNODES; do
    for ippn in $PPN; do
	PREFIXNAME="nodes-${inode}_ppn-${ippn}_nranks-$(( inode * ippn ))_nthreads-1"
	echo $PREFIXNAME

	BATCH_CMD=${BATCH_CMD_PREFIX}
	case $WLM in
	    pbs)
		BATCH_CMD+="-lnodes=${inode}:ppn=${ippn} "
		BATCH_CMD+="-N ${NAMEOUT_PREFIX}_${PREFIXNAME}_${LABEL}_${QUEUE} "
		;;
	    slurm)
		BATCH_CMD+="--nodes=${inode} --ntasks-per-node=${ippn} --ntasks=$(( inode * ippn )) -J ${NAMEOUT_PREFIX}_${PREFIXNAME}_${LABEL}_${QUEUE} "
		BATCH_CMD+="-o ${NAMEOUT_PREFIX}_${PREFIXNAME}_${LABEL}_${QUEUE}.o%j "
		;;
	esac

	echo "Submission command: ${BATCH_CMD}"

	${BATCH_CMD} <<EOF
#!/bin/bash -l
echo "Submission command: ${BATCH_CMD}"

env

module load ${MODULES}
module list

cd $PWD

PREFIXNAME="${PREFIXNAME}" SUBCMD="${SUBCMD}" $PWD/scripts/run.sh -l ${LABEL}___${QUEUE}

EOF

    done
done
