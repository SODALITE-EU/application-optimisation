#!/bin/bash

IMGBASENAME=code_aster_clinical

echo "Build ${IMGBASENAME} container with Singularity"

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

# Configuration file
cat > def/${IMGBASENAME}_conf.sh <<EOF
export MPI_DIST=$CHOICE
EOF

cd def
if test -n "$USE_SB"; then
    echo "Build Sandbox image"
    singularity build --sandbox --fakeroot --force ../${IMGBASENAME}_${CHOICE}.imgdir ${IMGBASENAME}.def
else
    echo "Build SIF image"
    sudo singularity build --force ../${IMGBASENAME}_${CHOICE}.sif ${IMGBASENAME}.def
fi
cd ..

# Clean configuration file
rm -f def/${IMGBASENAME}_conf.sh
