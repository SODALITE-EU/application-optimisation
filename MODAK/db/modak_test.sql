INSERT INTO `optimisation` VALUES
  ('pytorch-latest','pytorch','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','version:latest|','latest'),
  ('modak-tensorflow-2.1-gpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:2.1|','2.1'),
  ('code-aster-14.4-mpich-avx2','code-aster','enable_opt_build:false|cpu_type:x86|acc_type:none|','version:3.3.1|library:mpich','3.3.1'),
  ('code-aster-14.4-openmpi-avx2','code-aster','enable_opt_build:false|cpu_type:x86|acc_type:none|','version:3.1.3|library:openmpi','3.1.3'),
  ('modak-tensorflow-2.2.1-gpu-py3','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:2.2.1|','2.2.1'),
  ('ethcscs_openmpi_3.1.3','openmpi','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','version:3.1.3|mpicc:true|mpic++:true|mpifort:true|','3.1.3'),
  ('mpich_ub1804_cuda101_mpi314_gnugprof','mpich','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','version:3.1.4|mpic++:true|mpicc:true|','3.1.4'),
  ('TF_PIP_XLA','tensorflow','cpu_type:x86|acc_type:nvidia|','xla:true|version:1.1|','');

INSERT INTO `mapper` VALUES
  (11,'modak-tensorflow-2.1-gpu-src','modakopt/modak:tensorflow-2.1-gpu-src','docker','docker','none'),
  (12,'modak-tensorflow-2.2.1-gpu-py3','tensorflow_2.2.1-gpu-py3','shub','library','none'),
  (13,'code-aster-14.4-mpich-avx2','code_aster_14.4.0_mpich_avx2','shub','library','none'),
  (14,'code-aster-14.4-openmpi-avx2','code_aster_14.4.0_openmpi_avx2','shub','library','none'),
  (33,'ethcscs_openmpi_3.1.3','ethcscs/openmpi:3.1.3','docker','docker',''),
  (38,'mpich_ub1804_cuda101_mpi314_gnugprof','ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof','docker','docker','none');

INSERT INTO infrastructure VALUES
  ('504f14b523a3405c911f50c8a9c31c0d', 'egi', NULL, 'HLRS Testbed', '{}'),
  ('bdf713bbe3024f2cb63a3771c28d254f', 'hlrs-testbed', NULL, 'HLRS Testbed Infrastructure', '{"scheduler": "torque", "storage": {}}');

INSERT INTO script VALUES
  ('80593ce7fc404e1d988d84c38930f8e5', NULL, '{"application": {"name": "openmpi", "feature": {}}, "infrastructure": {"name": "egi"}}', '{"stage": "pre", "raw": "module load mpi/openmpi-x86_64"}'),
  ('16c9b7309a2d4d80b4c9a045ab885984', NULL, '{"application": {"name": "tensorflow", "feature": {"xla": true}}, "infrastructure": null}','{"stage": "pre", "raw": "mkdir xla_dump\nexport TF_XLA_FLAGS=\"--tf_xla_auto_jit=2 --tf_xla_cpu_global_jit\"\nexport XLA_FLAGS=\"--xla_dump_to=xla_dump/generated\""}');
