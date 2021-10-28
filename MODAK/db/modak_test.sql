INSERT INTO `optimisation` VALUES
  ('pytorch-latest','pytorch','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','version:latest|','latest'),
  ('modak-tensorflow-2.1-gpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:2.1|','2.1'),
  ('code-aster-14.4-mpich-avx2','mpich','enable_opt_build:true|cpu_type:x86|acc_type:none|','version:3.3.1|','3.3.1'),
  ('modak-tensorflow-2.2.1-gpu-py3','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:2.2.1|','2.2.1'),
  ('ethcscs_openmpi_3.1.3','openmpi','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:3.1.3,mpicc:true,mpic++:true,mpifort:true,','3.1.3'),
  ('mpich_ub1804_cuda101_mpi314_gnugprof','mpich','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:3.1.4,mpic++:true,mpicc:true,','3.1.4');

INSERT INTO `mapper` VALUES
  (11,'modak-tensorflow-2.1-gpu-src','modakopt/modak:tensorflow-2.1-gpu-src','docker','docker','none'),
  (12,'modak-tensorflow-2.2.1-gpu-py3','tensorflow_2.2.1-gpu-py3','shub','library','none'),
  (13,'code-aster-14.4-mpich-avx2','code_aster_14.4.0_mpich_avx2','shub','library','none'),
  (33,'ethcscs_openmpi_3.1.3','ethcscs/openmpi:3.1.3','docker','docker',''),
  (38,'mpich_ub1804_cuda101_mpi314_gnugprof','ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof','docker','docker','none');

INSERT INTO `optscript` VALUES
  ('egi','set_default_egi.sh','file://modak-builtin/set_default_egi.sh',0),
  ('hlrs_testbed','set_default_hlrs_testbed.sh','file://modak-builtin/set_default_hlrs_testbed.sh',0),
  ('xla','enable_xla.sh','file://modak-builtin/enable_xla.sh',0);
