-- MySQL dump 10.13  Distrib 8.0.21, for macos10.15 (x86_64)
--
-- Host: localhost    Database: iac_model
-- ------------------------------------------------------
-- Server version	8.0.21

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `iac_model`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `iac_model` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `iac_model`;

--
-- Table structure for table `mapper`
--

DROP TABLE IF EXISTS `mapper`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mapper` (
  `map_id` int NOT NULL AUTO_INCREMENT,
  `opt_dsl_code` varchar(255) NOT NULL,
  `container_file` varchar(255) DEFAULT NULL,
  `image_type` varchar(255) DEFAULT NULL,
  `image_hub` varchar(255) DEFAULT NULL,
  `src` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`map_id`),
  KEY `opt_dsl_code_idx` (`opt_dsl_code`),
  CONSTRAINT `opt_dsl_code` FOREIGN KEY (`opt_dsl_code`) REFERENCES `optimisation` (`opt_dsl_code`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mapper`
--

LOCK TABLES `mapper` WRITE;
/*!40000 ALTER TABLE `mapper` DISABLE KEYS */;
INSERT INTO `mapper` VALUES (1,'modak-pytorch-1.5-cpu-pip','modakopt/modak:pytorch-1.5-cpu-pip','docker','docker','none'),(2,'modak-pytorch-1.5-cpu-src','modakopt/modak:pytorch-1.5-cpu-src','docker','docker','none'),(3,'modak-pytorch-1.5-gpu-pip','modakopt/modak:pytorch-1.5-gpu-pip','docker','docker','none'),(4,'modak-pytorch-1.5-gpu-src','modakopt/modak:pytorch-1.5-gpu-src','docker','docker','none'),(5,'modak-pytorch-latest-cpu-pip','modakopt/modak:pytorch-latest-cpu-pip','docker','docker','none'),(6,'modak-pytorch-latest-cpu-src','modakopt/modak:pytorch-latest-cpu-src','docker','docker','none'),(7,'modak-pytorch-latest-gpu-pip','modakopt/modak:pytorch-latest-gpu-pip','docker','docker','none'),(8,'modak-tensorflow-2.1-cpu-pip','modakopt/modak:tensorflow-2.1-cpu-pip','docker','docker','none'),(9,'modak-tensorflow-2.1-cpu-src','modakopt/modak:tensorflow-2.1-cpu-src','docker','docker','none'),(10,'modak-tensorflow-2.1-gpu-pip','modakopt/modak:tensorflow-2.1-gpu-pip','docker','docker','none'),(11,'modak-tensorflow-2.1-gpu-src','modakopt/modak:tensorflow-2.1-gpu-src','docker','docker','none'),(12,'modak-tensorflow-2.4-cpu-src','modakopt/modak:tensorflow-2.4-cpu-src','docker','docker','none'),(13,'modak-tensorflow-latest-cpu-pip','modakopt/modak:tensorflow-latest-cpu-pip','docker','docker','none'),(14,'modak-tensorflow-latest-gpu-pip','modakopt/modak:tensorflow-latest-gpu-pip','docker','docker','none'),(15,'modak-tensorflow-latest-gpu-src','modakopt/modak:tensorflow-latest-gpu-src','docker','docker','none'),(16,'modak-tensorflow-ngraph-1.14','modakopt/modak:tensorflow-ngraph-1.14','docker','docker','none'),(17,'modak-test-ubuntu','modakopt/modak:test-ubuntu','docker','docker','none'),(18,'modak-ubuntu-18-04','modakopt/modak:ubuntu-18-04','docker','docker','none'),(19,'tensorflow-latest-gpu','tensorflow/tensorflow:latest-gpu','docker','docker','none'),(20,'tensorflow-latest-py3','tensorflow/tensorflow:latest-py3','docker','docker','none'),(21,'tensorflow-2.1.0-gpu-py3','tensorflow/tensorflow:2.1.0-gpu-py3','docker','docker','none'),(22,'tensorflow-2.1.0-py3','tensorflow/tensorflow:2.1.0-py3','docker','docker','none'),(23,'pytorch-latest','pytorch/pytorch:latest','docker','docker','none'),(24,'pytorch-1.5.1-cuda10.1-cudnn7-runtime','pytorch/pytorch:1.5.1-cuda10.1-cudnn7-runtime','docker','docker','none'),(32,'TF_PIP_XLA','AI/containers/tensorflow/tensorflow_pip_xla','docker','docker',''),(33,'ethcscs_openmpi_3.1.3','ethcscs/openmpi:3.1.3','docker','docker',''),(38,'mpich_ub1804_cuda101_mpi314_gnugprof','ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof','docker','docker','none'),(39,'mvapich_ub1804_cuda101_mpi22_osu','ethcscs/mvapich:ub1804_cuda101_mpi22_osu','docker','docker','none'),(48,'pottava_openmpi:1.10','pottava/openmpi:1.10','docker','docker','none');
/*!40000 ALTER TABLE `mapper` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `optimisation`
--

DROP TABLE IF EXISTS `optimisation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `optimisation` (
  `opt_dsl_code` varchar(255) NOT NULL,
  `app_name` varchar(255) DEFAULT NULL,
  `target` varchar(5000) DEFAULT NULL,
  `optimisation` varchar(5000) DEFAULT NULL,
  `version` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`opt_dsl_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `optimisation`
--

LOCK TABLES `optimisation` WRITE;
/*!40000 ALTER TABLE `optimisation` DISABLE KEYS */;
INSERT INTO `optimisation` VALUES ('ethcscs_openmpi_3.1.3','openmpi','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:3.1.3,mpicc:true,mpic++:true,mpifort:true,','3.1.3'),('modak-pytorch-1.5-cpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:none|','version:1.5|',NULL),('modak-pytorch-1.5-cpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:none|','version:1.5|',NULL),('modak-pytorch-1.5-gpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','version:1.5|',NULL),('modak-pytorch-1.5-gpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','version:1.5|',NULL),('modak-pytorch-latest-cpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:none|','version:latest|',NULL),('modak-pytorch-latest-cpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:none|','version:latest|',NULL),('modak-pytorch-latest-gpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','version:latest|',NULL),('modak-tensorflow-2.1-cpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','xla:true|version:2.1|',NULL),('modak-tensorflow-2.1-cpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:none|','xla:true|version:2.1|',NULL),('modak-tensorflow-2.1-gpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','xla:true|version:2.1|',NULL),('modak-tensorflow-2.1-gpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:2.1|',NULL),('modak-tensorflow-2.4-cpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:none|','xla:true|version:latest|',NULL),('modak-tensorflow-latest-cpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','xla:true|version:latest|',NULL),('modak-tensorflow-latest-gpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','xla:true|version:latest|',NULL),('modak-tensorflow-latest-gpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:latest|',NULL),('modak-tensorflow-ngraph-1.14','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','ngraph:true|version:1.14|',NULL),('modak-test-ubuntu','test','enable_opt_build:true|cpu_type:none|acc_type:none|','test:true',NULL),('modak-ubuntu-18-04','ubuntu','enable_opt_build:true|cpu_type:none|acc_type:none|','',NULL),('mpich_ub1804_cuda101_mpi314_gnugprof','mpich','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:3.1.4,mpic++:true,mpicc:true,',''),('mvapich_ub1804_cuda101_mpi22_osu','mvapich','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:2.2,mpic++:true,mpicc:true,mpifort:true,',''),('pottava_openmpi:1.10','openmpi','enable_opt_build:true,cpu_type:x86,acc_type:none','version:1.10,mpicc:true,mpic++:true,mpifort:true,','1.10'),('pytorch-1.5.1-cuda10.1-cudnn7-runtime','pytorch','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','version:1.5|',NULL),('pytorch-latest','pytorch','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','version:latest|',NULL),('tensorflow-2.1.0-gpu-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:2.1|',NULL),('tensorflow-2.1.0-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:2.1|',NULL),('tensorflow-latest-gpu','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','xla:true|version:latest|',NULL),('tensorflow-latest-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:latest|',NULL),('TF_PIP_XLA','tensorflow','cpu_type:x86,acc_type:nvidia,','xla:true,version:1.1,','');
/*!40000 ALTER TABLE `optimisation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `optscript`
--

DROP TABLE IF EXISTS `optscript`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `optscript` (
  `opt_code` varchar(255) NOT NULL,
  `script_name` varchar(255) DEFAULT NULL,
  `script_loc` varchar(5000) DEFAULT NULL,
  `stage` int DEFAULT NULL,
  PRIMARY KEY (`opt_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `optscript`
--

LOCK TABLES `optscript` WRITE;
/*!40000 ALTER TABLE `optscript` DISABLE KEYS */;
INSERT INTO `optscript` VALUES ('egi','set_default_egi.sh','https://www.dropbox.com/s/97h9zkj7uxx9sc5/set_default_egi.sh?dl=1',0),('hlrs_testbed','set_default_hlrs_testbed.sh','https://www.dropbox.com/s/hpfcwwkd4zy52t9/set_default_hlrs_testbed.sh?dl=1',0),('xla','enable_xla.sh','https://www.dropbox.com/s/e6n9yb0a5601gp2/enable_xla.sh?dl=1',0);
/*!40000 ALTER TABLE `optscript` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Current Database: `test_iac_model`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `test_iac_model` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `test_iac_model`;

--
-- Table structure for table `benchmarks`
--

DROP TABLE IF EXISTS `benchmarks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `benchmarks` (
  `infra_name` varchar(255) NOT NULL,
  `queue_name` varchar(255) NOT NULL,
  `timestamp` double NOT NULL,
  `nodes` int NOT NULL,
  `ppn` int DEFAULT NULL,
  `procs` int NOT NULL,
  `HPL_Tflops` double DEFAULT NULL,
  `RandomlyOrderedRingBandwidth_GBytes` double DEFAULT NULL,
  `StarSTREAM_Triad` double DEFAULT NULL,
  `b_eff_io` double DEFAULT NULL,
  PRIMARY KEY (`infra_name`,`timestamp`,`nodes`,`procs`),
  KEY `infra_idx` (`infra_name`),
  CONSTRAINT `infra1` FOREIGN KEY (`infra_name`) REFERENCES `infrastructure` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `benchmarks`
--

LOCK TABLES `benchmarks` WRITE;
/*!40000 ALTER TABLE `benchmarks` DISABLE KEYS */;
INSERT INTO `benchmarks` VALUES ('daint','mc',202008142144,1,36,36,0.568058,1.19493,2.66687,1231.643),('daint','mc',202008142253,2,36,72,1.12257,0.344078,2.66616,1784.748),('daint','mc',202008152301,3,36,108,1.63381,0.17286,2.41578,2253.114),('daint','mc',202008152301,4,36,144,2.10035,0.146564,2.43171,2725.038),('daint','mc',202008162146,6,36,216,3.30128,0.103099,2.68443,3927.583),('daint','mc',202008162315,8,36,288,4.01995,0.0982196,2.70001,4725.084),('daint','mc',202008170821,10,36,360,4.9849,0.0927042,2.64713,5252.072),('hlrs_testbed','default',202008050926,1,1,1,0.0239732,-1,9.27506,121.312),('hlrs_testbed','default',202008050928,1,10,10,0.0939289,1.02249,2.70778,164.531),('hlrs_testbed','default',202008050928,1,20,20,0.262648,0.596652,1.51067,182.832),('hlrs_testbed','default',202008050934,4,10,40,0.482774,0.361033,6.77187,269.673),('hlrs_testbed','default',202008050956,4,20,80,1.11853,0.123702,3.87105,388.968),('hlrs_testbed','default',202008051133,2,20,40,0.158173,0.0122831,8.83938,141.145),('osprey','bdw18',202008140940,1,36,36,0.524869,1.26318,2.66651,1600.056),('osprey','bdw18',202008141446,2,36,72,0.947159,0.417804,2.6419,2035.046),('osprey','bdw18',202008141520,3,36,108,1.30762,0.334797,2.65406,2448.995),('osprey','bdw18',202008141544,4,36,144,1.57744,0.282844,2.64153,2497.883),('osprey','bdw18',202008141551,6,36,216,1.92585,0.254916,2.61324,2816.175),('osprey','bdw18',202008151601,8,36,288,2.04625,0.227028,2.59919,3295.858),('osprey','bdw18',202008151629,10,36,360,1.93514,0.218925,2.5804,3366.516);
/*!40000 ALTER TABLE `benchmarks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `infrastructure`
--

DROP TABLE IF EXISTS `infrastructure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `infrastructure`
--

LOCK TABLES `infrastructure` WRITE;
/*!40000 ALTER TABLE `infrastructure` DISABLE KEYS */;
INSERT INTO `infrastructure` VALUES ('aws',1000,1,'AWS Parallel cluster',NULL,NULL,NULL,'slurm','openmpi'),('cirrus',256,1,'UK Tier2 HPC','cirrus Uk Tier 2',NULL,NULL,'slurm','openmpi'),('daint',1000,1,'Piz Daint CSCS',NULL,NULL,NULL,'slurm','mpich'),('egi',10,1,'EGI testbed',NULL,NULL,NULL,'torque','openmpi'),('gcp',1000,1,'Google Cloud Platform',NULL,NULL,NULL,'slurm','openmpi'),('hlrs_testbed',5,1,'SODALITE HPC testbed',NULL,NULL,NULL,'torque','mpich'),('osprey',1000,1,'HPE test cluster',NULL,NULL,NULL,'slurm','openmpi');
/*!40000 ALTER TABLE `infrastructure` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mapper`
--

DROP TABLE IF EXISTS `mapper`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mapper` (
  `map_id` int NOT NULL AUTO_INCREMENT,
  `opt_dsl_code` varchar(255) NOT NULL,
  `container_file` varchar(255) DEFAULT NULL,
  `image_type` varchar(255) DEFAULT NULL,
  `image_hub` varchar(255) DEFAULT NULL,
  `src` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`map_id`),
  KEY `opt_dsl_code_idx` (`opt_dsl_code`),
  CONSTRAINT `opt_dsl_code` FOREIGN KEY (`opt_dsl_code`) REFERENCES `optimisation` (`opt_dsl_code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mapper`
--

LOCK TABLES `mapper` WRITE;
/*!40000 ALTER TABLE `mapper` DISABLE KEYS */;
INSERT INTO `mapper` VALUES (1,'modak-pytorch-1.5-cpu-pip','modakopt/modak:pytorch-1.5-cpu-pip','docker','docker','none'),(2,'modak-pytorch-1.5-cpu-src','modakopt/modak:pytorch-1.5-cpu-src','docker','docker','none'),(3,'modak-pytorch-1.5-gpu-pip','modakopt/modak:pytorch-1.5-gpu-pip','docker','docker','none'),(4,'modak-pytorch-1.5-gpu-src','modakopt/modak:pytorch-1.5-gpu-src','docker','docker','none'),(5,'modak-pytorch-latest-cpu-pip','modakopt/modak:pytorch-latest-cpu-pip','docker','docker','none'),(6,'modak-pytorch-latest-cpu-src','modakopt/modak:pytorch-latest-cpu-src','docker','docker','none'),(7,'modak-pytorch-latest-gpu-pip','modakopt/modak:pytorch-latest-gpu-pip','docker','docker','none'),(8,'modak-tensorflow-2.1-cpu-pip','modakopt/modak:tensorflow-2.1-cpu-pip','docker','docker','none'),(9,'modak-tensorflow-2.1-cpu-src','modakopt/modak:tensorflow-2.1-cpu-src','docker','docker','none'),(10,'modak-tensorflow-2.1-gpu-pip','modakopt/modak:tensorflow-2.1-gpu-pip','docker','docker','none'),(11,'modak-tensorflow-2.1-gpu-src','modakopt/modak:tensorflow-2.1-gpu-src','docker','docker','none'),(12,'modak-tensorflow-2.4-cpu-src','modakopt/modak:tensorflow-2.4-cpu-src','docker','docker','none'),(13,'modak-tensorflow-latest-cpu-pip','modakopt/modak:tensorflow-latest-cpu-pip','docker','docker','none'),(14,'modak-tensorflow-latest-gpu-pip','modakopt/modak:tensorflow-latest-gpu-pip','docker','docker','none'),(15,'modak-tensorflow-latest-gpu-src','modakopt/modak:tensorflow-latest-gpu-src','docker','docker','none'),(16,'modak-tensorflow-ngraph-1.14','modakopt/modak:tensorflow-ngraph-1.14','docker','docker','none'),(17,'modak-test-ubuntu','modakopt/modak:test-ubuntu','docker','docker','none'),(18,'modak-ubuntu-18-04','modakopt/modak:ubuntu-18-04','docker','docker','none'),(19,'tensorflow-latest-gpu','tensorflow/tensorflow:latest-gpu','docker','docker','none'),(20,'tensorflow-latest-py3','tensorflow/tensorflow:latest-py3','docker','docker','none'),(21,'tensorflow-2.1.0-gpu-py3','tensorflow/tensorflow:2.1.0-gpu-py3','docker','docker','none'),(22,'tensorflow-2.1.0-py3','tensorflow/tensorflow:2.1.0-py3','docker','docker','none'),(23,'pytorch-latest','pytorch/pytorch:latest','docker','docker','none'),(24,'pytorch-1.5.1-cuda10.1-cudnn7-runtime','pytorch/pytorch:1.5.1-cuda10.1-cudnn7-runtime','docker','docker','none'),(33,'ethcscs_openmpi_3.1.3','ethcscs/openmpi:3.1.3','docker','docker',''),(38,'mpich_ub1804_cuda101_mpi314_gnugprof','ethcscs/mpich:ub1804_cuda101_mpi314_gnugprof','docker','docker','none'),(39,'mvapich_ub1804_cuda101_mpi22_osu','ethcscs/mvapich:ub1804_cuda101_mpi22_osu','docker','docker','none'),(48,'pottava_openmpi:1.10','pottava/openmpi:1.10','docker','docker',NULL),(54,'sodalite-hpe_modak_cp2k-openmpi','sodalite-hpe/modak:cp2k-openmpi','singularity','shub','none'),(55,'sodalite-hpe_modak_cp2k-mpich','sodalite-hpe/modak:cp2k-mpich','singularity','shub','none');
/*!40000 ALTER TABLE `mapper` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `optimisation`
--

DROP TABLE IF EXISTS `optimisation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `optimisation` (
  `opt_dsl_code` varchar(255) NOT NULL,
  `app_name` varchar(255) DEFAULT NULL,
  `target` varchar(5000) DEFAULT NULL,
  `optimisation` varchar(5000) DEFAULT NULL,
  `version` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`opt_dsl_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `optimisation`
--

LOCK TABLES `optimisation` WRITE;
/*!40000 ALTER TABLE `optimisation` DISABLE KEYS */;
INSERT INTO `optimisation` VALUES ('ethcscs_openmpi_3.1.3','openmpi','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:3.1.3,mpicc:true,mpic++:true,mpifort:true,','3.1.3'),('modak-pytorch-1.5-cpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:none|','version:1.5|','1.5'),('modak-pytorch-1.5-cpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:none|','version:1.5|','1.5'),('modak-pytorch-1.5-gpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','version:1.5|','1.5'),('modak-pytorch-1.5-gpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','version:1.5|','1.5'),('modak-pytorch-latest-cpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:none|','version:latest|','latest'),('modak-pytorch-latest-cpu-src','pytorch','enable_opt_build:true|cpu_type:x86|acc_type:none|','version:latest|','latest'),('modak-pytorch-latest-gpu-pip','pytorch','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','version:latest|','latest'),('modak-tensorflow-2.1-cpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','xla:true|version:2.1|','2.1'),('modak-tensorflow-2.1-cpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:none|','xla:true|version:2.1|','2.1'),('modak-tensorflow-2.1-gpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','xla:true|version:2.1|','2.1'),('modak-tensorflow-2.1-gpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:2.1|','2.1'),('modak-tensorflow-2.4-cpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:none|','xla:true|version:latest|','latest'),('modak-tensorflow-latest-cpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','xla:true|version:latest|','latest'),('modak-tensorflow-latest-gpu-pip','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:nvidia|','xla:true|version:latest|','latest'),('modak-tensorflow-latest-gpu-src','tensorflow','enable_opt_build:true|cpu_type:x86|acc_type:nvidia|','xla:true|version:latest|','latest'),('modak-tensorflow-ngraph-1.14','tensorflow','enable_opt_build:true|cpu_type:none|acc_type:none|','ngraph:true|version:1.14|','1.14'),('modak-test-ubuntu','test','enable_opt_build:true|cpu_type:none|acc_type:none|','test:true',NULL),('modak-ubuntu-18-04','ubuntu','enable_opt_build:true|cpu_type:none|acc_type:none|','','18.04'),('mpich_ub1804_cuda101_mpi314_gnugprof','mpich','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:3.1.4,mpic++:true,mpicc:true,','3.1.4'),('mvapich_ub1804_cuda101_mpi22_osu','mvapich','enable_opt_build:true,cpu_type:x86,acc_type:nvidia,','version:2.2,mpic++:true,mpicc:true,mpifort:true,','2.2'),('pottava_openmpi:1.10','openmpi','enable_opt_build:true,cpu_type:x86,acc_type:none','version:1.10,mpicc:true,mpic++:true,mpifort:true,','1.10'),('pytorch-1.5.1-cuda10.1-cudnn7-runtime','pytorch','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','version:1.5|','1.5'),('pytorch-latest','pytorch','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','version:latest|','latest'),('sodalite-hpe_modak_cp2k-mpich','cp2k','enable_opt_build:true,cpu_type:x86,','version:7.1.0,mpich:3.3.1,scalapack:2.1.0,fftw:3.3.8,libxsmm:1.15,openblac:0.3.9,','7.1.0'),('sodalite-hpe_modak_cp2k-openmpi','cp2k','enable_opt_build:true,cpu_type:x86,','version:7.1.0,openmpi:4.0.1,scalapack:2.1.0,fftw:3.3.8,libxsmm:1.15,openblac:0.3.9,','7.1.0'),('tensorflow-2.1.0-gpu-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:2.1|','2.1'),('tensorflow-2.1.0-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:2.1|','2.1'),('tensorflow-latest-gpu','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:nvidia|','xla:true|version:latest|','latest'),('tensorflow-latest-py3','tensorflow','enable_opt_build:false|cpu_type:x86|acc_type:none|','xla:true|version:latest|','latest'),('TF_PIP_XLA','tensorflow','cpu_type:x86,acc_type:nvidia,','xla:true,version:1.1,','1.1');
/*!40000 ALTER TABLE `optimisation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `optscript`
--

DROP TABLE IF EXISTS `optscript`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `optscript` (
  `opt_code` varchar(255) NOT NULL,
  `script_name` varchar(255) DEFAULT NULL,
  `script_loc` varchar(5000) DEFAULT NULL,
  `stage` int DEFAULT NULL,
  PRIMARY KEY (`opt_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `optscript`
--

LOCK TABLES `optscript` WRITE;
/*!40000 ALTER TABLE `optscript` DISABLE KEYS */;
INSERT INTO `optscript` VALUES ('egi','set_default_egi.sh','https://www.dropbox.com/s/97h9zkj7uxx9sc5/set_default_egi.sh?dl=1',0),('hlrs_testbed','set_default_hlrs_testbed.sh','https://www.dropbox.com/s/hpfcwwkd4zy52t9/set_default_hlrs_testbed.sh?dl=1',0),('xla','enable_xla.sh','https://www.dropbox.com/s/e6n9yb0a5601gp2/enable_xla.sh?dl=1',0);
/*!40000 ALTER TABLE `optscript` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `queue`
--

DROP TABLE IF EXISTS `queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `queue` (
  `queue_id` int NOT NULL AUTO_INCREMENT,
  `infrastructure` varchar(255) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `num_nodes` int DEFAULT NULL,
  `active` int DEFAULT NULL,
  `node_spec` varchar(255) DEFAULT NULL,
  `desc` varchar(2550) DEFAULT NULL,
  PRIMARY KEY (`queue_id`),
  KEY `infra_idx` (`infrastructure`),
  CONSTRAINT `infra` FOREIGN KEY (`infrastructure`) REFERENCES `infrastructure` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `queue`
--

LOCK TABLES `queue` WRITE;
/*!40000 ALTER TABLE `queue` DISABLE KEYS */;
/*!40000 ALTER TABLE `queue` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-09-16 17:44:31
