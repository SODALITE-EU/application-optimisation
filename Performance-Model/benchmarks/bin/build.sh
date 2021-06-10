#!/bin/bash

echo "Build benchmark container with Singularity"

options=("MPICH" "OpenMPI" "Quit")
CHOICE=""

do_select() {
    case "$1" in
	"${options[0]}"|"${options[1]}")
	    CHOICE="$1"
	    ;;
	"Quit")
	    CHOICE=""
	    ;;
	*)
	    echo "Invalid distribution $REPLY"
	    exit -1
	    ;;
    esac
}

if (($# == 0)); then
echo "Choose which MPI distribution to use:"
select opt in "${options[@]}"
do
    do_select "$opt"
    break
done
else
    do_select "$1"
fi

if test -z $CHOICE; then
    echo $opt
    exit 0
fi

echo "Use $CHOICE distribution."

# Save previous configuration file
mv build/benchmarks_conf.def build/benchmarks_conf.def.bak

cat > build/benchmarks_conf.def <<EOF
MPI_DIST=$CHOICE
EOF

cd build
if test -n "$USE_SB"; then
    echo "Build Sandbox image"
    singularity build --sandbox --fakeroot ../benchmarks.imgdir benchmarks.def
else
    echo "Build SIF image"
    sudo singularity build ../benchmarks.simg benchmarks.def
fi
cd ..

# Restore configuration file
mv build/benchmarks_conf.def.bak build/benchmarks_conf.def
