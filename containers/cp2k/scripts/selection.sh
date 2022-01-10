#!/bin/bash

export IMGBASENAME=cp2k

echo "Select ${IMGBASENAME} container with Singularity"

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

