BEGIN EXCLUSIVE TRANSACTION;


DROP TABLE IF EXISTS `mapper`;
CREATE TABLE `mapper` (
	`map_id` int,
	`opt_dsl_code` varchar(255) NOT NULL,
	`container_file` varchar(255) DEFAULT NULL,
	`image_type` varchar(255) DEFAULT NULL,
	`image_hub` varchar(255) DEFAULT NULL,
	`src` varchar(255) DEFAULT NULL,
	PRIMARY KEY (`map_id`),
	CONSTRAINT `opt_dsl_code` FOREIGN KEY (`opt_dsl_code`) REFERENCES `optimisation` (`opt_dsl_code`)
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
  (32,'TF_PIP_XLA','AI/containers/tensorflow/tensorflow_pip_xla','docker','docker',''),
  (33,'ethcscs_openmpi_3.1.3','ethcscs/openmpi:3.1.3','docker','docker',''),
  (38,'mpich_ub1804_cuda101_mpi314_gnugprof','ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof','docker','docker','none'),
  (39,'mvapich_ub1804_cuda101_mpi22_osu','ethcscs/mvapich:ub1804_cuda101_mpi22_osu','docker','docker','none'),
  (48,'pottava_openmpi:1.10','pottava/openmpi:1.10','docker','docker','none');


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
  ('modak-pytorch-1.5-cpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:none|','version:1.5|',NULL),
  ('modak-pytorch-1.5-cpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:none|','version:1.5|',NULL),
  ('modak-pytorch-1.5-gpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','version:1.5|',NULL),
  ('modak-pytorch-1.5-gpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','version:1.5|',NULL),
  ('modak-pytorch-latest-cpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:none|','version:latest|',NULL),
  ('modak-pytorch-latest-cpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:none|','version:latest|',NULL),
  ('modak-pytorch-latest-gpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','version:latest|',NULL),
  ('modak-tensorflow-2.1-cpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','xla:true|version:2.1|',NULL),
  ('modak-tensorflow-2.1-cpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:none|','xla:true|version:2.1|',NULL),
  ('modak-tensorflow-2.1-gpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','xla:true|version:2.1|',NULL),
  ('modak-tensorflow-2.1-gpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:2.1|',NULL),
  ('modak-tensorflow-2.4-cpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:none|','xla:true|version:latest|',NULL),
  ('modak-tensorflow-latest-cpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','xla:true|version:latest|',NULL),
  ('modak-tensorflow-latest-gpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','xla:true|version:latest|',NULL),
  ('modak-tensorflow-latest-gpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:latest|',NULL),
  ('modak-tensorflow-ngraph-1.14','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','ngraph:true|version:1.14|',NULL),
  ('modak-test-ubuntu','test','enable_opt_build:true|cpu_type:none|acc_type:none|','test:true',NULL),
  ('modak-ubuntu-18-04','ubuntu','enable_opt_build:true|cpu_type:none|acc_type:none|','',NULL),
  ('mpich_ub1804_cuda101_mpi314_gnugprof','mpich','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:3.1.4,mpic++:true,mpicc:true,',''),
  ('mvapich_ub1804_cuda101_mpi22_osu','mvapich','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:2.2,mpic++:true,mpicc:true,mpifort:true,',''),
  ('pottava_openmpi:1.10','openmpi','enable_opt_build:true,cpu_type:x86,acc_type:none','version:1.10,mpicc:true,mpic++:true,mpifort:true,','1.10'),
  ('pytorch-1.5.1-cuda10.1-cudnn7-runtime','pytorch','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','version:1.5|',NULL),
  ('pytorch-latest','pytorch','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','version:latest|',NULL),
  ('tensorflow-2.1.0-gpu-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:2.1|',NULL),
  ('tensorflow-2.1.0-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:2.1|',NULL),
  ('tensorflow-latest-gpu','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','xla:true|version:latest|',NULL),
  ('tensorflow-latest-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:latest|',NULL),
  ('TF_PIP_XLA','tensorflow','cpu_type:x86,acc_type:nvidia,','xla:true,version:1.1,','');


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


COMMIT;
