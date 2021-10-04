#!/bin/bash

IMGBASENAME=code_aster_clinical

echo "Build ${IMGBASENAME} container with Singularity"

cd build
if test -n "$USE_SB"; then
    echo "Build Sandbox image"
    singularity build --sandbox --fakeroot ../${IMGBASENAME}.imgdir ${IMGBASENAME}.def
else
    echo "Build SIF image"
    sudo singularity build ../${IMGBASENAME}.sif ${IMGBASENAME}.def
fi
cd ..

