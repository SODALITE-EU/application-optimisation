#Sanity check built sif containers. Simple test that traverses directory and runs import of ngraph, tensorflow, pytorch, as well as version check. Pass if version returned, fail otherwise. 
#Invoke as ./sanity_check_containers.sh [sif_directory]
#will test working directory if no path specified

#!/bin/bash

#set counter variables
pass=0
fail=0

dir=$1

#choose to not test individual .sif containers. Exit gracefully.  
if [[ $dir == *".sif" ]]
then
	echo "$dir is container image"
	echo "stopping execution"
	exit 0
fi

#change to directory passed by user
if [ ! -z "$dir" ]
then
	echo "Testing containers in ${dir}"
	cd $dir
fi

#traverse all files in directory of type .sif
#test containers for ngraph, tensorflow, and pytorch. Glow test packages separately due to lack of import capability. 
for f in *.sif
do
#test for ngraph first. If ngraph runs correctly, then TF is also installed correctly. 
	case $f in
		*"ngraph"*)
			echo "$f contains ngraph"
			/usr/local/bin/singularity exec $f python3 -c "import ngraph_bridge; print(ngraph_bridge.__version__)" 
			if [[ $? -eq 0 ]]
			then
				echo "$(tput setaf 1)ngraph successfully installed$(tput sgr0)"
				let pass++ 
			else
				echo "$(tput setaf 1)ngraph not found in container or corrupt image$(tput sgr0)"
				let fail++
			fi
			;;

		*"tensorflow"*)
			echo "$f contains tensorflow"
			/usr/local/bin/singularity exec $f python3 -c "import tensorflow; print(tensorflow.__version__)"
		    if [[ $? -eq 0 ]]
            then
                echo "$(tput setaf 1)tensorflow successfully installed$(tput sgr0)"
				let pass++
            else
                echo "$(tput setaf 1)tensorflow not found in container or corrupt image$(tput sgr0)"
				let fail++
            fi
			;;

		*"torch"*)
			echo "$f contains torch"
			/usr/local/bin/singularity exec $f python3 -c "import torch; print(torch.__version__)"
            if [[ $? -eq 0 ]]
            then
                echo "$(tput setaf 1)torch successfully installed$(tput sgr0)"
				let pass++
            else
                echo "$(tput setaf 1)torch not found in container or corrupt image$(tput sgr0)"
				let fail++
            fi
			;;

		*)
			echo "$(tput setaf 1)No sif images found. $(tput sgr0)"
			;;
	esac
done

total=$((pass+fail))

#Output stats in red color
echo "$(tput setaf 1)Passed tests: ${pass} / ${total}$(tput sgr0)"
echo "$(tput setaf 1)Failed tests: ${fail} / ${total}$(tput sgr0)"
