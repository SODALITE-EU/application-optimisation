BEGIN EXCLUSIVE TRANSACTION;


DROP TABLE IF EXISTS `benchmarks`;
CREATE TABLE `benchmarks` (
	`infra_name` varchar(255) NOT NULL,
	`queue_name` varchar(255) NOT NULL,
	`timestamp` DOUBLE NOT NULL,
	`nodes` int NOT NULL,
	`ppn` int DEFAULT NULL,
	`procs` int NOT NULL,
	`HPL_Tflops` DOUBLE DEFAULT NULL,
	`RandomlyOrderedRingBandwidth_GBytes` DOUBLE DEFAULT NULL,
	`StarSTREAM_Triad` DOUBLE DEFAULT NULL,
	`b_eff_io` DOUBLE DEFAULT NULL,
	PRIMARY KEY (
		`infra_name`,
		`timestamp`,
		`nodes`,
		`procs`
	),
	CONSTRAINT `infra_name` FOREIGN KEY (`infra_name`) REFERENCES `infrastructure` (`name`)
) WITHOUT ROWID;

INSERT INTO `benchmarks` VALUES
  ('daint','mc',202008142144,1,36,36,0.568058,1.19493,2.66687,1231.643),
  ('daint','mc',202008142253,2,36,72,1.12257,0.344078,2.66616,1784.748),
  ('daint','mc',202008152301,3,36,108,1.63381,0.17286,2.41578,2253.114),
  ('daint','mc',202008152301,4,36,144,2.10035,0.146564,2.43171,2725.038),
  ('daint','mc',202008162146,6,36,216,3.30128,0.103099,2.68443,3927.583),
  ('daint','mc',202008162315,8,36,288,4.01995,0.0982196,2.70001,4725.084),
  ('daint','mc',202008170821,10,36,360,4.9849,0.0927042,2.64713,5252.072),
  ('hlrs_testbed','default',202008050926,1,1,1,0.0239732,-1,9.27506,121.312),
  ('hlrs_testbed','default',202008050928,1,10,10,0.0939289,1.02249,2.70778,164.531),
  ('hlrs_testbed','default',202008050928,1,20,20,0.262648,0.596652,1.51067,182.832),
  ('hlrs_testbed','default',202008050934,4,10,40,0.482774,0.361033,6.77187,269.673),
  ('hlrs_testbed','default',202008050956,4,20,80,1.11853,0.123702,3.87105,388.968),
  ('hlrs_testbed','default',202008051133,2,20,40,0.158173,0.0122831,8.83938,141.145);


DROP TABLE IF EXISTS `infrastructure`;
CREATE TABLE `infrastructure` (
	`name` varchar(255) NOT NULL,
	`num_nodes` int DEFAULT NULL,
	`active` int DEFAULT NULL,
	`desc` varchar(2550) DEFAULT NULL,
	`host` varchar(255) DEFAULT NULL,
	`user` varchar(255) DEFAULT NULL,
	`keyid` varchar(255) DEFAULT NULL,
	`scheduler` varchar(45) DEFAULT NULL,
	`mpi` varchar(45) DEFAULT NULL,
	PRIMARY KEY (`name`)
);

INSERT INTO `infrastructure` VALUES
  ('aws',1000,1,'AWS Parallel cluster',NULL,NULL,NULL,'slurm','openmpi'),
  ('cirrus',256,1,'UK Tier2 HPC','cirrus Uk Tier 2',NULL,NULL,'slurm','openmpi'),
  ('daint',1000,1,'Piz Daint CSCS',NULL,NULL,NULL,'slurm','mpich'),
  ('egi',10,1,'EGI testbed',NULL,NULL,NULL,'torque','openmpi'),
  ('gcp',1000,1,'Google Cloud Platform',NULL,NULL,NULL,'slurm','openmpi'),
  ('hlrs_testbed',5,1,'SODALITE HPC testbed',NULL,NULL,NULL,'torque','mpich');


DROP TABLE IF EXISTS `mapper`;
CREATE TABLE `mapper` (
	`map_id` int,
	`opt_dsl_code` varchar(255) NOT NULL,
	`container_file` varchar(255) DEFAULT NULL,
	`image_type` varchar(255) DEFAULT NULL,
	`image_hub` varchar(255) DEFAULT NULL,
	`src` varchar(255) DEFAULT NULL,
	PRIMARY KEY (`map_id`),
	CONSTRAINT `opt_dsl_code` FOREIGN KEY (`opt_dsl_code`) REFERENCES `optimisation` (`opt_dsl_code`) ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO `mapper` VALUES
  (1,'modak-pytorch-1.5-cpu-pip','modakopt/modak:pytorch-1.5-cpu-pip','docker','docker','none'),
  (2,'modak-pytorch-1.5-cpu-src','modakopt/modak:pytorch-1.5-cpu-src','docker','docker','none'),
  (3,'modak-pytorch-1.5-gpu-pip','modakopt/modak:pytorch-1.5-gpu-pip','docker','docker','none'),
  (4,'modak-pytorch-1.5-gpu-src','modakopt/modak:pytorch-1.5-gpu-src','docker','docker','none'),
  (5,'modak-pytorch-latest-cpu-pip','modakopt/modak:pytorch-latest-cpu-pip','docker','docker','none'),
  (6,'modak-pytorch-latest-cpu-src','modakopt/modak:pytorch-latest-cpu-src','docker','docker','none'),
  (7,'modak-pytorch-latest-gpu-pip','modakopt/modak:pytorch-latest-gpu-pip','docker','docker','none'),
  (8,'modak-tensorflow-2.1-cpu-pip','modakopt/modak:tensorflow-2.1-cpu-pip','docker','docker','none'),
  (9,'modak-tensorflow-2.1-cpu-src','modakopt/modak:tensorflow-2.1-cpu-src','docker','docker','none'),
  (10,'modak-tensorflow-2.1-gpu-pip','modakopt/modak:tensorflow-2.1-gpu-pip','docker','docker','none'),
  (11,'modak-tensorflow-2.1-gpu-src','modakopt/modak:tensorflow-2.1-gpu-src','docker','docker','none'),
  (12,'modak-tensorflow-2.4-cpu-src','modakopt/modak:tensorflow-2.4-cpu-src','docker','docker','none'),
  (13,'modak-tensorflow-latest-cpu-pip','modakopt/modak:tensorflow-latest-cpu-pip','docker','docker','none'),
  (14,'modak-tensorflow-latest-gpu-pip','modakopt/modak:tensorflow-latest-gpu-pip','docker','docker','none'),
  (15,'modak-tensorflow-latest-gpu-src','modakopt/modak:tensorflow-latest-gpu-src','docker','docker','none'),
  (16,'modak-tensorflow-ngraph-1.14','modakopt/modak:tensorflow-ngraph-1.14','docker','docker','none'),
  (17,'modak-test-ubuntu','modakopt/modak:test-ubuntu','docker','docker','none'),
  (18,'modak-ubuntu-18-04','modakopt/modak:ubuntu-18-04','docker','docker','none'),
  (19,'tensorflow-latest-gpu','tensorflow/tensorflow:latest-gpu','docker','docker','none'),
  (20,'tensorflow-latest-py3','tensorflow/tensorflow:latest-py3','docker','docker','none'),
  (21,'tensorflow-2.1.0-gpu-py3','tensorflow/tensorflow:2.1.0-gpu-py3','docker','docker','none'),
  (22,'tensorflow-2.1.0-py3','tensorflow/tensorflow:2.1.0-py3','docker','docker','none'),
  (23,'pytorch-latest','pytorch/pytorch:latest','docker','docker','none'),
  (24,'pytorch-1.5.1-cuda10.1-cudnn7-runtime','pytorch/pytorch:1.5.1-cuda10.1-cudnn7-runtime','docker','docker','none'),
  (33,'ethcscs_openmpi_3.1.3','ethcscs/openmpi:3.1.3','docker','docker',''),
  (38,'mpich_ub1804_cuda101_mpi314_gnugprof','ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof','docker','docker','none'),
  (39,'mvapich_ub1804_cuda101_mpi22_osu','ethcscs/mvapich:ub1804_cuda101_mpi22_osu','docker','docker','none'),
  (48,'pottava_openmpi:1.10','pottava/openmpi:1.10','docker','docker',NULL),
  (54,'sodalite-hpe_modak_cp2k-openmpi','sodalite-hpe/modak:cp2k-openmpi','singularity','shub','none'),
  (55,'sodalite-hpe_modak_cp2k-mpich','sodalite-hpe/modak:cp2k-mpich','singularity','shub','none');


DROP TABLE IF EXISTS `optimisation`;
CREATE TABLE `optimisation` (
	`opt_dsl_code` varchar(255) NOT NULL,
	`app_name` varchar(255) DEFAULT NULL,
	`target` varchar(5000) DEFAULT NULL,
	`optimisation` varchar(5000) DEFAULT NULL,
	`version` varchar(255) DEFAULT NULL,
	PRIMARY KEY (`opt_dsl_code`)
) WITHOUT ROWID;


INSERT INTO `optimisation` VALUES
  ('ethcscs_openmpi_3.1.3','openmpi','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:3.1.3,mpicc:true,mpic++:true,mpifort:true,','3.1.3'),
  ('modak-pytorch-1.5-cpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:none|','version:1.5|','1.5'),
  ('modak-pytorch-1.5-cpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:none|','version:1.5|','1.5'),
  ('modak-pytorch-1.5-gpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','version:1.5|','1.5'),
  ('modak-pytorch-1.5-gpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','version:1.5|','1.5'),
  ('modak-pytorch-latest-cpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:none|','version:latest|','latest'),
  ('modak-pytorch-latest-cpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:none|','version:latest|','latest'),
  ('modak-pytorch-latest-gpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','version:latest|','latest'),
  ('modak-tensorflow-2.1-cpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','xla:true|version:2.1|','2.1'),
  ('modak-tensorflow-2.1-cpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:none|','xla:true|version:2.1|','2.1'),
  ('modak-tensorflow-2.1-gpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','xla:true|version:2.1|','2.1'),
  ('modak-tensorflow-2.1-gpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:2.1|','2.1'),
  ('modak-tensorflow-2.4-cpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:none|','xla:true|version:latest|','latest'),
  ('modak-tensorflow-latest-cpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','xla:true|version:latest|','latest'),
  ('modak-tensorflow-latest-gpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','xla:true|version:latest|','latest'),
  ('modak-tensorflow-latest-gpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:latest|','latest'),
  ('modak-tensorflow-ngraph-1.14','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','ngraph:true|version:1.14|','1.14'),
  ('modak-test-ubuntu','test','enable_opt_build:true|cpu_type:none|acc_type:none|','test:true',NULL),
  ('modak-ubuntu-18-04','ubuntu','enable_opt_build:true|cpu_type:none|acc_type:none|','','18.04'),
  ('mpich_ub1804_cuda101_mpi314_gnugprof','mpich','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:3.1.4,mpic++:true,mpicc:true,','3.1.4'),
  ('mvapich_ub1804_cuda101_mpi22_osu','mvapich','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:2.2,mpic++:true,mpicc:true,mpifort:true,','2.2'),
  ('pottava_openmpi:1.10','openmpi','enable_opt_build:true,cpu_type:x86,acc_type:none','version:1.10,mpicc:true,mpic++:true,mpifort:true,','1.10'),
  ('pytorch-1.5.1-cuda10.1-cudnn7-runtime','pytorch','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','version:1.5|','1.5'),
  ('pytorch-latest','pytorch','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','version:latest|','latest'),
  ('sodalite-hpe_modak_cp2k-mpich','cp2k','enable_opt_build:true,cpu_type:x86,','version:7.1.0,mpich:3.3.1,scalapack:2.1.0,fftw:3.3.8,libxsmm:1.15,openblac:0.3.9,','7.1.0'),
  ('sodalite-hpe_modak_cp2k-openmpi','cp2k','enable_opt_build:true,cpu_type:x86,','version:7.1.0,openmpi:4.0.1,scalapack:2.1.0,fftw:3.3.8,libxsmm:1.15,openblac:0.3.9,','7.1.0'),
  ('tensorflow-2.1.0-gpu-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:2.1|','2.1'),
  ('tensorflow-2.1.0-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:2.1|','2.1'),
  ('tensorflow-latest-gpu','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','xla:true|version:latest|','latest'),
  ('tensorflow-latest-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:latest|','latest'),
  ('TF_PIP_XLA','tensorflow','cpu_type:x86,acc_type:nvidia,','xla:true,version:1.1,','1.1');


DROP TABLE IF EXISTS `optscript`;
CREATE TABLE `optscript` (
	`opt_code` varchar(255) NOT NULL,
	`script_name` varchar(255) DEFAULT NULL,
	`script_loc` varchar(5000) DEFAULT NULL,
	`stage` int DEFAULT NULL,
	PRIMARY KEY (`opt_code`)
) WITHOUT ROWID;

INSERT INTO `optscript` VALUES
  ('egi','set_default_egi.sh','file://modak-builtin/set_default_egi.sh',0),
  ('hlrs_testbed','set_default_hlrs_testbed.sh','file://modak-builtin/set_default_hlrs_testbed.sh',0),
  ('xla','enable_xla.sh','file://modak-builtin/enable_xla.sh',0);


DROP TABLE IF EXISTS `queue`;
CREATE TABLE `queue` (
	`queue_id` int,
	`infrastructure` varchar(255) DEFAULT NULL,
	`name` varchar(255) NOT NULL,
	`num_nodes` int DEFAULT NULL,
	`active` int DEFAULT NULL,
	`node_spec` varchar(255) DEFAULT NULL,
	`desc` varchar(2550) DEFAULT NULL,
	PRIMARY KEY (`queue_id`),
	CONSTRAINT `infra` FOREIGN KEY (`infrastructure`) REFERENCES `infrastructure` (`name`)
);


COMMIT;
