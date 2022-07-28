-- MySQL dump 10.13  Distrib 8.0.29, for Linux (x86_64)
--
-- Host: localhost    Database: attendance
-- ------------------------------------------------------
-- Server version	8.0.29-0ubuntu0.20.04.3

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
-- Table structure for table `ACTIVE_SCHEDULE`
--

DROP TABLE IF EXISTS `ACTIVE_SCHEDULE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ACTIVE_SCHEDULE` (
  `GName` varchar(200) NOT NULL,
  `OID` varchar(36) NOT NULL,
  `Start_Time` time NOT NULL,
  `Commencement_Date` date NOT NULL,
  `Token` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`GName`,`OID`,`Start_Time`,`Commencement_Date`),
  CONSTRAINT `active_schedule_ibfk_1` FOREIGN KEY (`GName`, `OID`, `Start_Time`, `Commencement_Date`) REFERENCES `SCHEDULE` (`GName`, `OID`, `Start_Time`, `Commencement_Date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ACTIVE_SCHEDULE`
--

LOCK TABLES `ACTIVE_SCHEDULE` WRITE;
/*!40000 ALTER TABLE `ACTIVE_SCHEDULE` DISABLE KEYS */;
/*!40000 ALTER TABLE `ACTIVE_SCHEDULE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ADMIN`
--

DROP TABLE IF EXISTS `ADMIN`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ADMIN` (
  `ID` varchar(36) NOT NULL,
  PRIMARY KEY (`ID`),
  CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `USER` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ADMIN`
--

LOCK TABLES `ADMIN` WRITE;
/*!40000 ALTER TABLE `ADMIN` DISABLE KEYS */;
INSERT INTO `ADMIN` VALUES ('93c5f28f-e5ac-4aba-97fc-ad0cfbf7088a'),('b266f145-4df4-4fc8-81b1-a838c46a3b6d'),('ca520502-e2c0-439c-9b7f-3829e8ac050e'),('f47da81f-f94a-4dcb-8fa6-ca61ccc736df');
/*!40000 ALTER TABLE `ADMIN` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ATTENDANCE`
--

DROP TABLE IF EXISTS `ATTENDANCE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ATTENDANCE` (
  `ID` varchar(36) NOT NULL,
  `GName` varchar(200) NOT NULL,
  `OID` varchar(36) NOT NULL,
  `Start_Time` time NOT NULL,
  `Commencement_Date` date NOT NULL,
  `Record_Time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`,`GName`,`OID`,`Start_Time`,`Commencement_Date`),
  KEY `attendance_ibfk_3` (`GName`,`OID`,`Start_Time`,`Commencement_Date`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `USER` (`ID`),
  CONSTRAINT `attendance_ibfk_3` FOREIGN KEY (`GName`, `OID`, `Start_Time`, `Commencement_Date`) REFERENCES `SCHEDULE` (`GName`, `OID`, `Start_Time`, `Commencement_Date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ATTENDANCE`
--

LOCK TABLES `ATTENDANCE` WRITE;
/*!40000 ALTER TABLE `ATTENDANCE` DISABLE KEYS */;
INSERT INTO `ATTENDANCE` VALUES ('b5dd7c1d-74af-4323-a25f-579202ef22a3','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','10:30:00','2022-07-28','2022-07-28 13:22:41'),('b5dd7c1d-74af-4323-a25f-579202ef22a3','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','20:30:00','2022-07-28','2022-07-28 20:51:12'),('f39bae3b-dfd9-434c-a13a-700245c9d990','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','10:30:00','2022-07-28','2022-07-28 13:23:19'),('f39bae3b-dfd9-434c-a13a-700245c9d990','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','20:30:00','2022-07-28','2022-07-28 20:57:35');
/*!40000 ALTER TABLE `ATTENDANCE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `GROUP`
--

DROP TABLE IF EXISTS `GROUP`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `GROUP` (
  `Name` varchar(200) NOT NULL,
  `OID` varchar(36) NOT NULL,
  `Creator` varchar(36) NOT NULL,
  `Creation_Date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Name`,`OID`),
  KEY `OID` (`OID`),
  KEY `Creator` (`Creator`),
  CONSTRAINT `group_ibfk_1` FOREIGN KEY (`OID`) REFERENCES `ORGANIZATION` (`OID`),
  CONSTRAINT `group_ibfk_2` FOREIGN KEY (`Creator`) REFERENCES `USER` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `GROUP`
--

LOCK TABLES `GROUP` WRITE;
/*!40000 ALTER TABLE `GROUP` DISABLE KEYS */;
INSERT INTO `GROUP` VALUES ('A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','f47da81f-f94a-4dcb-8fa6-ca61ccc736df','2022-07-21 18:03:25'),('B','61c8d38d-2c9e-4197-998e-0ef01eb3488c','f47da81f-f94a-4dcb-8fa6-ca61ccc736df','2022-07-21 18:03:25'),('C','61c8d38d-2c9e-4197-998e-0ef01eb3488c','f47da81f-f94a-4dcb-8fa6-ca61ccc736df','2022-07-21 18:03:25'),('D','61c8d38d-2c9e-4197-998e-0ef01eb3488c','f47da81f-f94a-4dcb-8fa6-ca61ccc736df','2022-07-21 18:03:25'),('E','61c8d38d-2c9e-4197-998e-0ef01eb3488c','f47da81f-f94a-4dcb-8fa6-ca61ccc736df','2022-07-21 18:03:25'),('F','61c8d38d-2c9e-4197-998e-0ef01eb3488c','f47da81f-f94a-4dcb-8fa6-ca61ccc736df','2022-07-21 18:03:25'),('G','61c8d38d-2c9e-4197-998e-0ef01eb3488c','f47da81f-f94a-4dcb-8fa6-ca61ccc736df','2022-07-21 18:03:25'),('H','61c8d38d-2c9e-4197-998e-0ef01eb3488c','f47da81f-f94a-4dcb-8fa6-ca61ccc736df','2022-07-21 18:03:25'),('I','61c8d38d-2c9e-4197-998e-0ef01eb3488c','f47da81f-f94a-4dcb-8fa6-ca61ccc736df','2022-07-21 18:03:25'),('J','61c8d38d-2c9e-4197-998e-0ef01eb3488c','93c5f28f-e5ac-4aba-97fc-ad0cfbf7088a','2022-07-28 16:14:48'),('Test Group 1','37eae6c0-b2dd-4b8b-9ccf-de780a844337','ca520502-e2c0-439c-9b7f-3829e8ac050e','2022-07-28 16:30:30'),('Test Group 1.1','37eae6c0-b2dd-4b8b-9ccf-de780a844337','ca520502-e2c0-439c-9b7f-3829e8ac050e','2022-07-28 16:34:18');
/*!40000 ALTER TABLE `GROUP` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `GROUP_HIERARCHY`
--

DROP TABLE IF EXISTS `GROUP_HIERARCHY`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `GROUP_HIERARCHY` (
  `Name` varchar(200) NOT NULL,
  `OID` varchar(36) NOT NULL,
  `Parent` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`Name`,`OID`),
  KEY `OID` (`OID`),
  KEY `Parent` (`Parent`,`OID`),
  CONSTRAINT `group_hierarchy_ibfk_1` FOREIGN KEY (`OID`) REFERENCES `ORGANIZATION` (`OID`),
  CONSTRAINT `group_hierarchy_ibfk_2` FOREIGN KEY (`Name`, `OID`) REFERENCES `GROUP` (`Name`, `OID`),
  CONSTRAINT `group_hierarchy_ibfk_3` FOREIGN KEY (`Parent`, `OID`) REFERENCES `GROUP` (`Name`, `OID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `GROUP_HIERARCHY`
--

LOCK TABLES `GROUP_HIERARCHY` WRITE;
/*!40000 ALTER TABLE `GROUP_HIERARCHY` DISABLE KEYS */;
INSERT INTO `GROUP_HIERARCHY` VALUES ('C','61c8d38d-2c9e-4197-998e-0ef01eb3488c','A'),('D','61c8d38d-2c9e-4197-998e-0ef01eb3488c','A'),('E','61c8d38d-2c9e-4197-998e-0ef01eb3488c','B'),('F','61c8d38d-2c9e-4197-998e-0ef01eb3488c','B'),('G','61c8d38d-2c9e-4197-998e-0ef01eb3488c','C'),('H','61c8d38d-2c9e-4197-998e-0ef01eb3488c','C'),('I','61c8d38d-2c9e-4197-998e-0ef01eb3488c','E'),('J','61c8d38d-2c9e-4197-998e-0ef01eb3488c','I'),('Test Group 1.1','37eae6c0-b2dd-4b8b-9ccf-de780a844337','Test Group 1');
/*!40000 ALTER TABLE `GROUP_HIERARCHY` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MEMBERSHIP`
--

DROP TABLE IF EXISTS `MEMBERSHIP`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MEMBERSHIP` (
  `ID` varchar(36) NOT NULL,
  `GName` varchar(200) NOT NULL,
  `OID` varchar(36) NOT NULL,
  `Membership_Date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`,`GName`,`OID`),
  KEY `GName` (`GName`,`OID`),
  CONSTRAINT `membership_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `USER` (`ID`),
  CONSTRAINT `membership_ibfk_2` FOREIGN KEY (`GName`, `OID`) REFERENCES `GROUP` (`Name`, `OID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MEMBERSHIP`
--

LOCK TABLES `MEMBERSHIP` WRITE;
/*!40000 ALTER TABLE `MEMBERSHIP` DISABLE KEYS */;
INSERT INTO `MEMBERSHIP` VALUES ('1c9984cc-6ee4-4111-ba42-327871587902','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-28 20:59:42'),('67107310-30bb-4f13-a9f0-dd2c1ea9bf0a','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-28 07:04:44'),('93c5f28f-e5ac-4aba-97fc-ad0cfbf7088a','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-28 07:04:44'),('b5dd7c1d-74af-4323-a25f-579202ef22a3','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-28 07:04:44'),('db7e8277-cf83-485e-8651-d614b269b95c','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-28 07:04:44'),('f39bae3b-dfd9-434c-a13a-700245c9d990','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-28 07:04:44');
/*!40000 ALTER TABLE `MEMBERSHIP` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ORGANIZATION`
--

DROP TABLE IF EXISTS `ORGANIZATION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ORGANIZATION` (
  `OID` varchar(36) NOT NULL,
  `Name` varchar(400) NOT NULL,
  `Address` varchar(400) DEFAULT NULL,
  `Website` varchar(2500) DEFAULT NULL,
  `Code` varchar(6) NOT NULL,
  PRIMARY KEY (`OID`),
  UNIQUE KEY `Code` (`Code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ORGANIZATION`
--

LOCK TABLES `ORGANIZATION` WRITE;
/*!40000 ALTER TABLE `ORGANIZATION` DISABLE KEYS */;
INSERT INTO `ORGANIZATION` VALUES ('37eae6c0-b2dd-4b8b-9ccf-de780a844337','AttendanceTester',NULL,NULL,'FKBMFA'),('493c89a9-e1be-497c-8fd0-e2fbdc1ffbba','University of Delhi',NULL,NULL,'M1DDZG'),('61c8d38d-2c9e-4197-998e-0ef01eb3488c','GitHub','88 Colin P Kelly Junior Street San Francisco, CA 94107 USA','https://github.com','NUL2RL'),('c8c9c7c2-e4d6-44b3-8d63-11b06e2aba1b','qftics.org',NULL,NULL,'UZFQNX'),('ddbe2a38-075a-11ed-806a-3221e19b7403','TempOrg',NULL,NULL,'ABCDEF');
/*!40000 ALTER TABLE `ORGANIZATION` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SCHEDULE`
--

DROP TABLE IF EXISTS `SCHEDULE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SCHEDULE` (
  `Creator` varchar(36) NOT NULL,
  `GName` varchar(200) NOT NULL,
  `OID` varchar(36) NOT NULL,
  `Start_Time` time NOT NULL,
  `End_Time` time NOT NULL,
  `Commencement_Date` date NOT NULL,
  `Title` varchar(200) DEFAULT NULL,
  `Status` int NOT NULL,
  `Frequency` int DEFAULT NULL,
  PRIMARY KEY (`GName`,`OID`,`Start_Time`,`Commencement_Date`),
  KEY `GName` (`GName`,`OID`),
  KEY `schedule_ibfk_1` (`Creator`),
  CONSTRAINT `schedule_ibfk_1` FOREIGN KEY (`Creator`) REFERENCES `USER` (`ID`),
  CONSTRAINT `schedule_ibfk_2` FOREIGN KEY (`GName`, `OID`) REFERENCES `GROUP` (`Name`, `OID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SCHEDULE`
--

LOCK TABLES `SCHEDULE` WRITE;
/*!40000 ALTER TABLE `SCHEDULE` DISABLE KEYS */;
INSERT INTO `SCHEDULE` VALUES ('93c5f28f-e5ac-4aba-97fc-ad0cfbf7088a','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','03:30:00','05:30:00','2022-07-29','Morning Discussion',1,7),('93c5f28f-e5ac-4aba-97fc-ad0cfbf7088a','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','06:30:00','10:30:00','2022-07-28','Presentation Discussion',0,1),('93c5f28f-e5ac-4aba-97fc-ad0cfbf7088a','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','10:30:00','13:30:00','2022-07-28','Presentation Discussion (Contd.)',0,1),('93c5f28f-e5ac-4aba-97fc-ad0cfbf7088a','A','61c8d38d-2c9e-4197-998e-0ef01eb3488c','20:30:00','21:30:00','2022-07-28','Test Schedule',0,1);
/*!40000 ALTER TABLE `SCHEDULE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `USER`
--

DROP TABLE IF EXISTS `USER`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USER` (
  `ID` varchar(36) NOT NULL,
  `Name` varchar(200) NOT NULL,
  `Username` varchar(200) NOT NULL,
  `Password_Hash` varchar(1024) NOT NULL,
  `Password_Salt` varchar(256) NOT NULL,
  `Address` varchar(400) DEFAULT NULL,
  `Contact` bigint DEFAULT NULL,
  `Email` varchar(256) DEFAULT NULL,
  `Designation` varchar(100) DEFAULT NULL,
  `OID` varchar(36) DEFAULT NULL,
  `OJoin_Date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Username` (`Username`),
  KEY `OFK` (`OID`),
  CONSTRAINT `OFK` FOREIGN KEY (`OID`) REFERENCES `ORGANIZATION` (`OID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `USER`
--

LOCK TABLES `USER` WRITE;
/*!40000 ALTER TABLE `USER` DISABLE KEYS */;
INSERT INTO `USER` VALUES ('110a4e96-088e-4e96-8693-36cc8a793668','Bhomic','bhomic.k','JDJiJDEyJGxKSFN0amhmOXNSTk9vRHppV1J5cXVlZ1BwRW5ZekZ4dk9zYk5NT29RVnFlc2daOVh0ZFpX','JDJiJDEyJGxKSFN0amhmOXNSTk9vRHppV1J5cXU=',NULL,NULL,'bhomic@kaushik.com',NULL,NULL,NULL),('1c9984cc-6ee4-4111-ba42-327871587902','Test_user1','test_1','JDJiJDEyJFA5OGRkcVJQWU5yb3JRUmNFLndNUS5sQnFXcUxTd2VielNmRUZnWTdwYlZ5M2syaVpEZ0h1','JDJiJDEyJFA5OGRkcVJQWU5yb3JRUmNFLndNUS4=',NULL,NULL,'test@user.com',NULL,'61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-28 20:50:58'),('67107310-30bb-4f13-a9f0-dd2c1ea9bf0a','DEF','DEF','JDJiJDEyJEFZZ1BQRjVtSldybklyVHUuV282di5vZHpxWEpQNVVNMERJL2JQZEUuZHJUclpncnpnS1VL','JDJiJDEyJEFZZ1BQRjVtSldybklyVHUuV282di4=',NULL,0,NULL,NULL,'61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-24 09:57:45'),('93c5f28f-e5ac-4aba-97fc-ad0cfbf7088a','U1','user1','JDJiJDEyJGFwcVJUR0hzNm96NHpOOWxKVWg5Ty5naWV4a1p1amFlaDI3YjhZZ29oV0dLcFMvdldiZC4y','JDJiJDEyJGFwcVJUR0hzNm96NHpOOWxKVWg5Ty4=','Flat No. 69, Block 420, Machii Talao Lane',9211420420,'u1@gmail.com','Temporary User','61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-26 05:02:12'),('b266f145-4df4-4fc8-81b1-a838c46a3b6d','abhi','abhi','JDJiJDEyJFRHbnhvQ3Fqb3l0ZmZxRnNYdTd5Y3V4RWs0UTE5NGtlZlE2d1NZaEMyQlJ3OU1ERUZFdElT','JDJiJDEyJFRHbnhvQ3Fqb3l0ZmZxRnNYdTd5Y3U=','ghar',1111111111,'abhi@gmail.com','CTO','c8c9c7c2-e4d6-44b3-8d63-11b06e2aba1b','2022-07-28 12:53:50'),('b5dd7c1d-74af-4323-a25f-579202ef22a3','U2','U2','JDJiJDEyJFFNZnpmSXlmS2VpWlFlSWdEMW5qUS5UYTBGRm5LeWdPVGJML010eTRUU2N1Q0VMT3kyYXBl','JDJiJDEyJFFNZnpmSXlmS2VpWlFlSWdEMW5qUS4=',NULL,0,NULL,NULL,'61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-23 09:12:44'),('ca520502-e2c0-439c-9b7f-3829e8ac050e','Sajal Maheshwari','sajal.m','JDJiJDEyJGJJNm1jL3dKNzM3WFFybkFRbEFjQXVJVFd4dUYzRDJXMEFMLlQ4dTE1cFJneDBJQkg0MlJH','JDJiJDEyJGJJNm1jL3dKNzM3WFFybkFRbEFjQXU=','Shalimar Bagh, Delhi - 110088',8840980731,'sajalmaheshwari21@gmail.com','admin tester','37eae6c0-b2dd-4b8b-9ccf-de780a844337','2022-07-28 06:13:08'),('db7e8277-cf83-485e-8651-d614b269b95c','U4','U4','JDJiJDEyJGZPeGlSWTRyVmdIcjFrb2MxU3BiZi5TeGNCM1lQUmRlOHlLdk5KL0J2NkZmdDdLOHlHU09D','JDJiJDEyJGZPeGlSWTRyVmdIcjFrb2MxU3BiZi4=',NULL,0,NULL,NULL,'61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-23 09:12:44'),('f21784ff-cc13-4b36-8d6b-d8d1c9e4996f','Bhomic Kaushik','bhomic','JDJiJDEyJEVoaXRQRHRkaFFweGQ1Y3BROGMuMHV6L2guaDRGYTFnR2FURjkwU1VyalJla094WGw2YXV1','JDJiJDEyJEVoaXRQRHRkaFFweGQ1Y3BROGMuMHU=',NULL,NULL,'bhomic.mcs21@cs.du.ac.in',NULL,NULL,NULL),('f39bae3b-dfd9-434c-a13a-700245c9d990','U3','U3','JDJiJDEyJG0wVEFSR3guWDZoRW1qc2ttMDFjUU9XQTFXNFZya29UejFhLy9lTHlzWHZQRXp1Y3ZpaHNt','JDJiJDEyJG0wVEFSR3guWDZoRW1qc2ttMDFjUU8=',NULL,0,NULL,NULL,'61c8d38d-2c9e-4197-998e-0ef01eb3488c','2022-07-23 09:12:44'),('f47da81f-f94a-4dcb-8fa6-ca61ccc736df','ABC','ABC','JDJiJDEyJFdldHRRVXZQUFVXT1l4anJVUFZTSS41Lk0wQ01aM3RYUFZUWUVtVlZaUEhieFljNjNVekNp','JDJiJDEyJFdldHRRVXZQUFVXT1l4anJVUFZTSS4=',NULL,0,'abc@gmail.com','Student','ddbe2a38-075a-11ed-806a-3221e19b7403',NULL);
/*!40000 ALTER TABLE `USER` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-07-28 21:09:24
