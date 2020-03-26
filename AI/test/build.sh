# Build Ubuntu base
singularity build --fakeroot --sandbox ubuntu_base/ ../containers/ubuntu_base.def

#Build Tensorflow containers
singularity build --fakeroot --sandbox tensorflow_2.0_opt_source_xla ../containers/tensorflow/tensorflow_2.0_opt_source_xla.def  
singularity build --fakeroot --sandbox tensorflow_2.1_opt_source_xla ../containers/tensorflow/tensorflow_2.1_opt_source_xla.def   
singularity build --fakeroot --sandbox tensorflow_pip_ngraph ../containers/tensorflow/tensorflow_pip_ngraph.def  
singularity build --fakeroot --sandbox tensorflow_pip_xla ../containers/tensorflow/tensorflow_pip_xla.def
singularity build --fakeroot --sandbox tensorflow_2.0_source_xla ../containers/tensorflow/tensorflow_2.0_source_xla.def      
singularity build --fakeroot --sandbox tensorflow_manually_opt_source ../containers/tensorflow/tensorflow_manually_opt_source.def  
singularity build --fakeroot --sandbox tensorflow_pip_opt ../containers/tensorflow/tensorflow_pip_opt.def     
singularity build --fakeroot --sandbox tensorflow_source_xla ../containers/tensorflow/tensorflow_source_xla.def

#Build Torch containers
singularity build --fakeroot --sandbox torch_pip_glow ../containers/torch/torch_pip_glow.def  
singularity build --fakeroot --sandbox torch_pip_glow_ver-2 ../containers/torch/torch_pip_glow_ver-2.def  
singularity build --fakeroot --sandbox torch_source ../containers/torch/torch_source.def  
singularity build --fakeroot --sandbox torch_source_glow ../containers/torch/torch_source_glow.def  
singularity build --fakeroot --sandbox torch_source_glow_ver-2 ../containers/torch/torch_source_glow_ver-2.def
