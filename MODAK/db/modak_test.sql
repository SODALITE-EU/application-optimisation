BEGIN EXCLUSIVE TRANSACTION;

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
  ('pytorch-latest','pytorch','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','version:latest|','latest'),
  ('modak-tensorflow-2.1-gpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:2.1|','2.1'),
  ('ethcscs_openmpi_3.1.3','openmpi','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:3.1.3,mpicc:true,mpic++:true,mpifort:true,','3.1.3'),
  ('mpich_ub1804_cuda101_mpi314_gnugprof','mpich','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:3.1.4,mpic++:true,mpicc:true,','3.1.4');

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
  (11,'modak-tensorflow-2.1-gpu-src','modakopt/modak:tensorflow-2.1-gpu-src','docker','docker','none'),
  (33,'ethcscs_openmpi_3.1.3','ethcscs/openmpi:3.1.3','docker','docker',''),
  (38,'mpich_ub1804_cuda101_mpi314_gnugprof','ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof','docker','docker','none');


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
