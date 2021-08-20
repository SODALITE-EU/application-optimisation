#PBS -S /bin/bash
## START OF HEADER ##
#PBS -N resnet
#PBS -l walltime=12:00:00
#PBS -l nodes=1:ppn=40:gpus=1
#PBS -o resnet.out
#PBS -j oe
#PBS -m abe
#PBS -M kartshy@gmail.com
## END OF HEADER ##
cd $PBS_O_WORKDIR
export PATH=$PBS_O_WORKDIR:$PATH
## MODAK: START OF OPT:XLA ##
mkdir xla_dump
export TF_XLA_FLAGS="--tf_xla_auto_jit=2 --tf_xla_cpu_global_jit"
export XLA_FLAGS="--xla_dump_to=xla_dump/generated"
## MODAK: END OF OPT:XLA ##

singularity exec --nv "$SINGULARITY_DIR/modak_tensorflow-2.1-gpu-src.sif" ./resnet_benchmark.sh
