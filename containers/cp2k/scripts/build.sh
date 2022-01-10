#!/bin/bash

BASEDIR=$(dirname "$0")
. ${BASEDIR}/selection.sh

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
