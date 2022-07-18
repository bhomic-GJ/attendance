-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 17, 2022 at 05:46 PM
-- Server version: 10.4.24-MariaDB
-- PHP Version: 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Attendance`
--

-- --------------------------------------------------------

--
-- Table structure for table `ACTIVE_SCHEDULE`
--

CREATE TABLE `ACTIVE_SCHEDULE` (
  `Creator` varchar(30) NOT NULL,
  `GName` varchar(200) NOT NULL,
  `OID` varchar(30) NOT NULL,
  `Start_Time` time NOT NULL,
  `Token` varchar(256) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `ADMIN`
--

CREATE TABLE `ADMIN` (
  `ID` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `ATTENDANCE`
--

CREATE TABLE `ATTENDANCE` (
  `ID` varchar(30) NOT NULL,
  `Creator` varchar(30) NOT NULL,
  `GName` varchar(200) NOT NULL,
  `OID` varchar(30) NOT NULL,
  `Start_Time` time NOT NULL,
  `Record_Time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `GROUP`
--

CREATE TABLE `GROUP` (
  `Name` varchar(200) NOT NULL,
  `OID` varchar(30) NOT NULL,
  `Creator` varchar(30) NOT NULL,
  `Creation_Date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `GROUP_HIERARCHY`
--

CREATE TABLE `GROUP_HIERARCHY` (
  `Name` varchar(200) NOT NULL,
  `OID` varchar(30) NOT NULL,
  `Parent` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `MEMBERSHIP`
--

CREATE TABLE `MEMBERSHIP` (
  `ID` varchar(30) NOT NULL,
  `GName` varchar(200) NOT NULL,
  `OID` varchar(30) NOT NULL,
  `Membership_Date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `ORGANIZATION`
--

CREATE TABLE `ORGANIZATION` (
  `OID` varchar(30) NOT NULL,
  `Name` varchar(400) NOT NULL,
  `Address` varchar(400) DEFAULT NULL,
  `Website` varchar(2500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `SCHEDULE`
--

CREATE TABLE `SCHEDULE` (
  `Creator` varchar(30) NOT NULL,
  `GName` varchar(200) NOT NULL,
  `OID` varchar(30) NOT NULL,
  `Start_Time` time NOT NULL,
  `End_Time` time NOT NULL,
  `Commencement_Date` date NOT NULL,
  `Status` int(11) NOT NULL,
  `Frequency` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `USER`
--

CREATE TABLE `USER` (
  `ID` varchar(30) NOT NULL,
  `Name` varchar(200) NOT NULL,
  `Username` varchar(200) NOT NULL,
  `Password_Hash` varchar(1024) NOT NULL,
  `Password_Salt` varchar(256) NOT NULL,
  `Address` varchar(400) DEFAULT NULL,
  `Contact` bigint(20) DEFAULT NULL,
  `email` varchar(256) DEFAULT NULL,
  `Designation` varchar(100) DEFAULT NULL,
  `OID` varchar(30) NOT NULL,
  `OJoin_Date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ACTIVE_SCHEDULE`
--
ALTER TABLE `ACTIVE_SCHEDULE`
  ADD PRIMARY KEY (`Creator`,`GName`,`OID`,`Start_Time`);

--
-- Indexes for table `ADMIN`
--
ALTER TABLE `ADMIN`
  ADD PRIMARY KEY (`ID`);

--
-- Indexes for table `ATTENDANCE`
--
ALTER TABLE `ATTENDANCE`
  ADD PRIMARY KEY (`ID`,`Creator`,`GName`,`OID`,`Start_Time`),
  ADD KEY `Creator` (`Creator`,`GName`,`OID`,`Start_Time`);

--
-- Indexes for table `GROUP`
--
ALTER TABLE `GROUP`
  ADD PRIMARY KEY (`Name`,`OID`),
  ADD KEY `OID` (`OID`),
  ADD KEY `Creator` (`Creator`);

--
-- Indexes for table `GROUP_HIERARCHY`
--
ALTER TABLE `GROUP_HIERARCHY`
  ADD PRIMARY KEY (`Name`,`OID`),
  ADD KEY `OID` (`OID`),
  ADD KEY `Parent` (`Parent`,`OID`);

--
-- Indexes for table `MEMBERSHIP`
--
ALTER TABLE `MEMBERSHIP`
  ADD PRIMARY KEY (`ID`,`GName`,`OID`),
  ADD KEY `GName` (`GName`,`OID`);

--
-- Indexes for table `ORGANIZATION`
--
ALTER TABLE `ORGANIZATION`
  ADD PRIMARY KEY (`OID`);

--
-- Indexes for table `SCHEDULE`
--
ALTER TABLE `SCHEDULE`
  ADD PRIMARY KEY (`Creator`,`GName`,`OID`,`Start_Time`),
  ADD KEY `GName` (`GName`,`OID`);

--
-- Indexes for table `USER`
--
ALTER TABLE `USER`
  ADD PRIMARY KEY (`ID`),
  ADD UNIQUE KEY `Username` (`Username`),
  ADD UNIQUE KEY `Username_2` (`Username`),
  ADD KEY `OFK` (`OID`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `ACTIVE_SCHEDULE`
--
ALTER TABLE `ACTIVE_SCHEDULE`
  ADD CONSTRAINT `active_schedule_ibfk_1` FOREIGN KEY (`Creator`,`GName`,`OID`,`Start_Time`) REFERENCES `SCHEDULE` (`Creator`, `GName`, `OID`, `Start_Time`);

--
-- Constraints for table `ADMIN`
--
ALTER TABLE `ADMIN`
  ADD CONSTRAINT `admin_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `USER` (`ID`),
  ADD CONSTRAINT `admin_ibfk_2` FOREIGN KEY (`ID`) REFERENCES `USER` (`ID`);

--
-- Constraints for table `ATTENDANCE`
--
ALTER TABLE `ATTENDANCE`
  ADD CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `USER` (`ID`),
  ADD CONSTRAINT `attendance_ibfk_2` FOREIGN KEY (`Creator`) REFERENCES `USER` (`ID`),
  ADD CONSTRAINT `attendance_ibfk_3` FOREIGN KEY (`Creator`,`GName`,`OID`,`Start_Time`) REFERENCES `SCHEDULE` (`Creator`, `GName`, `OID`, `Start_Time`);

--
-- Constraints for table `GROUP`
--
ALTER TABLE `GROUP`
  ADD CONSTRAINT `group_ibfk_1` FOREIGN KEY (`OID`) REFERENCES `ORGANIZATION` (`OID`),
  ADD CONSTRAINT `group_ibfk_2` FOREIGN KEY (`Creator`) REFERENCES `USER` (`ID`);

--
-- Constraints for table `GROUP_HIERARCHY`
--
ALTER TABLE `GROUP_HIERARCHY`
  ADD CONSTRAINT `group_hierarchy_ibfk_1` FOREIGN KEY (`OID`) REFERENCES `ORGANIZATION` (`OID`),
  ADD CONSTRAINT `group_hierarchy_ibfk_2` FOREIGN KEY (`Name`,`OID`) REFERENCES `GROUP` (`Name`, `OID`),
  ADD CONSTRAINT `group_hierarchy_ibfk_3` FOREIGN KEY (`Parent`,`OID`) REFERENCES `GROUP` (`Name`, `OID`);

--
-- Constraints for table `MEMBERSHIP`
--
ALTER TABLE `MEMBERSHIP`
  ADD CONSTRAINT `membership_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `USER` (`ID`),
  ADD CONSTRAINT `membership_ibfk_2` FOREIGN KEY (`GName`,`OID`) REFERENCES `GROUP` (`Name`, `OID`);

--
-- Constraints for table `SCHEDULE`
--
ALTER TABLE `SCHEDULE`
  ADD CONSTRAINT `schedule_ibfk_1` FOREIGN KEY (`Creator`) REFERENCES `USER` (`ID`),
  ADD CONSTRAINT `schedule_ibfk_2` FOREIGN KEY (`GName`,`OID`) REFERENCES `GROUP` (`Name`, `OID`);

--
-- Constraints for table `USER`
--
ALTER TABLE `USER`
  ADD CONSTRAINT `OFK` FOREIGN KEY (`OID`) REFERENCES `ORGANIZATION` (`OID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
