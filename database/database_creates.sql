CREATE DATABASE  IF NOT EXISTS `picodelivery` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `picodelivery`;
-- MySQL dump 10.13  Distrib 5.7.9, for Win64 (x86_64)
--
-- Host: picodelivery.westeurope.cloudapp.azure.com    Database: picodelivery
-- ------------------------------------------------------
-- Server version	5.6.28-0ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `address`
--

DROP TABLE IF EXISTS `address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `address` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `street` varchar(200) NOT NULL,
  `city_id` int(11) DEFAULT NULL,
  `map_point` point NOT NULL,
  `area_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `city_id_idx` (`city_id`),
  KEY `address_fk_area_id` (`area_id`),
  CONSTRAINT `address_ibfk_1` FOREIGN KEY (`area_id`) REFERENCES `area` (`id`),
  CONSTRAINT `city_id` FOREIGN KEY (`city_id`) REFERENCES `city` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=965 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`pico_admin`@`%`*/ /*!50003 TRIGGER ins_address_add_area BEFORE INSERT ON address
FOR EACH ROW
BEGIN

	SET NEW.area_id =
		(SELECT id
		FROM area
		WHERE st_contains(area, NEW.map_point)
    );
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`pico_admin`@`%`*/ /*!50003 TRIGGER upd_address_add_area BEFORE UPDATE ON address
FOR EACH ROW
BEGIN

	IF NEW.map_point <> OLD.map_point THEN
		SET NEW.area_id =
			(SELECT id
			FROM area
			WHERE st_contains(area, NEW.map_point)
		);
	END IF;

END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `administrator`
--

DROP TABLE IF EXISTS `administrator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `administrator` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `user_id_idx` (`user_id`),
  CONSTRAINT `administrator_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `aggregate_hourly_jobs`
--

DROP TABLE IF EXISTS `aggregate_hourly_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `aggregate_hourly_jobs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `area_id` int(11) NOT NULL,
  `count_of_jobs` int(11) NOT NULL,
  `start_hour` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `area_id_idx` (`area_id`),
  CONSTRAINT `aggregate_hourly_jobs_area_id` FOREIGN KEY (`area_id`) REFERENCES `area` (`id`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=34718 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `area`
--

DROP TABLE IF EXISTS `area`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `area` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `area` polygon NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `city`
--

DROP TABLE IF EXISTS `city`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `city` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(60) NOT NULL,
  `country_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `country_id_idx` (`country_id`),
  CONSTRAINT `country_id` FOREIGN KEY (`country_id`) REFERENCES `country` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `country`
--

DROP TABLE IF EXISTS `country`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `country` (
  `id` int(11) NOT NULL,
  `name` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `customer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(70) DEFAULT NULL,
  `last_name` varchar(70) DEFAULT NULL,
  `address_id` int(11) NOT NULL,
  `mobile_number` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `c_fk_address_id_idx` (`address_id`),
  CONSTRAINT `c_fk_address_id` FOREIGN KEY (`address_id`) REFERENCES `address` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=543 DEFAULT CHARSET=latin1 COMMENT='	';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `driver`
--

DROP TABLE IF EXISTS `driver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `driver` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL COMMENT 'On insert, create a user too with data from this table?',
  `active` tinyint(4) NOT NULL DEFAULT '1',
  `first_name` varchar(45) NOT NULL,
  `last_name` varchar(45) NOT NULL,
  `address_id` int(11) DEFAULT NULL,
  `mobile_number` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `user_id_idx` (`user_id`),
  KEY `address_id_idx` (`address_id`),
  CONSTRAINT `driver_address_id` FOREIGN KEY (`address_id`) REFERENCES `address` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `driver_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=347 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `driver_location`
--

DROP TABLE IF EXISTS `driver_location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `driver_location` (
  `driver_id` int(11) NOT NULL,
  `coordinates` point NOT NULL,
  `captured` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`driver_id`),
  UNIQUE KEY `driver_id_idx` (`driver_id`),
  CONSTRAINT `driver_location_driver_id_fk` FOREIGN KEY (`driver_id`) REFERENCES `driver` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `feedback_on_driver`
--

DROP TABLE IF EXISTS `feedback_on_driver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `feedback_on_driver` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_id` int(11) NOT NULL,
  `rating` int(11) NOT NULL,
  `comment` longtext,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `task_id_idx` (`task_id`),
  CONSTRAINT `feedback_on_driver_task_id` FOREIGN KEY (`task_id`) REFERENCES `job` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `feedback_on_restaurant`
--

DROP TABLE IF EXISTS `feedback_on_restaurant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `feedback_on_restaurant` (
  `id` int(11) NOT NULL,
  `task_id` int(11) NOT NULL,
  `restaurant_rating` int(11) NOT NULL,
  `customer_rating` int(11) NOT NULL,
  `restaurant_comment` longtext,
  `customer_comment` longtext,
  PRIMARY KEY (`id`),
  KEY `task_id_idx` (`task_id`),
  CONSTRAINT `feedback_on_restaurant_task_id` FOREIGN KEY (`task_id`) REFERENCES `job` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hourly_prediction`
--

DROP TABLE IF EXISTS `hourly_prediction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hourly_prediction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `area_id` int(11) NOT NULL,
  `start_hour` datetime NOT NULL,
  `predicted_value` decimal(10,6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `uq_hourly_prediction` (`area_id`,`start_hour`),
  KEY `area_id_idx` (`area_id`),
  CONSTRAINT `hourly_prediction_area_id` FOREIGN KEY (`area_id`) REFERENCES `area` (`id`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22022 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `job`
--

DROP TABLE IF EXISTS `job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `job` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `job_detail_id` int(11) NOT NULL,
  `driver_id` int(11) DEFAULT NULL,
  `status_id` int(11) NOT NULL DEFAULT '1',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `start_time` datetime DEFAULT NULL,
  `payload_collected_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `job_detail_id_idx` (`job_detail_id`),
  KEY `driver_id_idx` (`driver_id`),
  KEY `status_id_idx` (`status_id`),
  CONSTRAINT `job_driver_id` FOREIGN KEY (`driver_id`) REFERENCES `driver` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `job_job_detail_id` FOREIGN KEY (`job_detail_id`) REFERENCES `job_detail` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `job_status_id` FOREIGN KEY (`status_id`) REFERENCES `status` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1630949 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `job_detail`
--

DROP TABLE IF EXISTS `job_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `job_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `restaurant_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL DEFAULT '-1',
  `tip_text` longtext,
  `prepaid` tinyint(1) NOT NULL DEFAULT '1',
  `payment_due` decimal(5,2) NOT NULL DEFAULT '0.00',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `pickup_time_requested` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `package_size` int(11) NOT NULL DEFAULT '1',
  `estimated_worth` decimal(5,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `restaurant_id_idx` (`restaurant_id`),
  KEY `job_detail_customer_id_idx` (`customer_id`),
  CONSTRAINT `job_detail_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `job_detail_restaurant_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurant` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=1681913 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`pico_admin`@`%`*/ /*!50003 TRIGGER aggregate_hourly_job_count_and_add_initial_job AFTER INSERT ON `job_detail` FOR EACH ROW
BEGIN
	DECLARE v_area_id integer;
	DECLARE v_existing_count integer;
	-- First, get the addresses location (Possibly use a trigger to build a table to define where all the addresses are located in areas?)
    -- Then the time the job was created
    -- Then check if an a row for that area and > hr <hr+1 exists
    -- If not, insert a new row
    -- Update the row by adding to the count of jobs

IF @DISABLE_TRIGGER IS NULL THEN

    SELECT a.area_id into v_area_id
	FROM restaurant r
    JOIN address a ON r.address_id = a.id
	WHERE r.id = new.restaurant_id;

    SET @v_previous_hour = (SELECT start_hour
	FROM picodelivery.aggregate_hourly_jobs
	WHERE area_id = v_area_id
	ORDER BY id DESC
	LIMIT 1);

    #Setup a var that equals NEW.time to the hour xx:00:00
    SET @job_detail_nearest_hour = DATE_FORMAT(new.pickup_time_requested, "%Y-%m-%d %H:00:00");

    SET @cursor_hour = date_add(@v_previous_hour, INTERVAL 1 hour);

	WHILE (@cursor_hour < @job_detail_nearest_hour) DO
		INSERT INTO picodelivery.aggregate_hourly_jobs
		(area_id, count_of_jobs, start_hour)
		VALUES (v_area_id, 0, @cursor_hour);

		SET @cursor_hour = date_add(@cursor_hour, INTERVAL 1 hour);
	END WHILE;


	SELECT count(*) into v_existing_count
	FROM aggregate_hourly_jobs
	WHERE start_hour = @job_detail_nearest_hour
	AND area_id = v_area_id;

	IF ( v_existing_count > 0 ) THEN
		UPDATE aggregate_hourly_jobs
		SET count_of_jobs = count_of_jobs + 1
		WHERE start_hour = @job_detail_nearest_hour
		AND area_id = v_area_id;
	ELSE
		INSERT INTO aggregate_hourly_jobs
		(area_id, count_of_jobs, start_hour) VALUES
		(v_area_id, 1, @job_detail_nearest_hour);
	END IF;

    INSERT INTO job
    (job_detail_id, create_time)
    VALUES
    (NEW.id, NEW.create_time);

END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `location_hint`
--

DROP TABLE IF EXISTS `location_hint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `location_hint` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `address_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `hint_text` longtext,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `address_id_idx` (`address_id`),
  KEY `user_id_idx` (`user_id`),
  CONSTRAINT `location_hint_address_id` FOREIGN KEY (`address_id`) REFERENCES `address` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `location_hint_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `restaurant`
--

DROP TABLE IF EXISTS `restaurant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `restaurant` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `address_id` int(11) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `user_id` int(11) DEFAULT '1',
  `mobile_number` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `address_id_UNIQUE` (`address_id`),
  KEY `user_id_idx` (`user_id`),
  KEY `address_id_idx` (`address_id`),
  CONSTRAINT `restaurant_address_id` FOREIGN KEY (`address_id`) REFERENCES `address` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `restaurant_user_id` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=355 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `simulated_aggregate_hourly_jobs`
--

DROP TABLE IF EXISTS `simulated_aggregate_hourly_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `simulated_aggregate_hourly_jobs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `area_id` int(11) NOT NULL,
  `count_of_jobs` int(11) NOT NULL,
  `start_hour` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `area_id_idx` (`area_id`),
  CONSTRAINT `sim_aggregate_hourly_jobs_area_id` FOREIGN KEY (`area_id`) REFERENCES `area` (`id`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32056 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `simulated_job_detail`
--

DROP TABLE IF EXISTS `simulated_job_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `simulated_job_detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `restaurant_id` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL DEFAULT '-1',
  `tip_text` longtext,
  `prepaid` tinyint(1) NOT NULL DEFAULT '1',
  `payment_due` decimal(5,2) NOT NULL DEFAULT '0.00',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `pickup_time_requested` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `package_size` int(11) NOT NULL DEFAULT '1',
  `estimated_worth` decimal(5,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `sim_id_UNIQUE` (`id`),
  KEY `sim_restaurant_id_idx` (`restaurant_id`),
  KEY `sim_job_detail_customer_id_idx` (`customer_id`),
  CONSTRAINT `sim_job_detail_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `sim_job_detail_restaurant_id` FOREIGN KEY (`restaurant_id`) REFERENCES `restaurant` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2378531 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `status`
--

DROP TABLE IF EXISTS `status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` varchar(45) NOT NULL,
  `next_step` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `swarm`
--

DROP TABLE IF EXISTS `swarm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `swarm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `row_created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `in_progress` tinyint(4) NOT NULL DEFAULT '1',
  `area_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `fk_area_id_idx` (`area_id`),
  CONSTRAINT `fk_area_id` FOREIGN KEY (`area_id`) REFERENCES `area` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8 COMMENT='Table to track the progress of swarming of areas.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `first_name` varchar(45) NOT NULL,
  `last_name` varchar(45) NOT NULL,
  `username` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=335 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'picodelivery'
--

--
-- Dumping routines for database 'picodelivery'
--
/*!50003 DROP PROCEDURE IF EXISTS `acceptJobAsDriver` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`pico_admin`@`%` PROCEDURE `acceptJobAsDriver`(in v_job_detail_id int, in v_user_email varchar(200))
BEGIN
SET @driverId = (SELECT d.id FROM driver d
    JOIN user u ON u.id= d.user_id
    WHERE u.email LIKE v_user_email);

IF(@driverId > 0) THEN
	UPDATE job
    SET driver_id = @driverId,
    status_id = 2,
    start_time = now()
    WHERE job_detail_id = v_job_detail_id
    AND status_id = 1
    ;
END IF;

    SELECT IF(count(*)=1,true,false) as accepted FROM job
    WHERE status_id = 2
    AND job_detail_id = v_job_detail_id
    AND driver_id = (
    	SELECT d.id FROM driver d
        JOIN user u ON u.id= d.user_id
        WHERE u.email LIKE v_user_email);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `add_job_detail` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`pico_admin`@`%` PROCEDURE `add_job_detail`(
IN v_restaurant_id INT,
IN v_status_id INT,
IN v_dropoff_address_id INT,
IN v_prepaid boolean,
IN v_payment_due double,
IN v_create_time datetime,
IN v_pickup_time_requested datetime,
IN v_package_size int,
IN v_estimated_worth double)
BEGIN
	INSERT INTO job_detail
	(restaurant_id,
	status_id,
	dropoff_address_id,
	prepaid,
	payment_due,
	create_time,
	pickup_time_requested,
	package_size,
	estimated_worth)
	VALUES (
    v_restaurant_id,
	v_status_id,
	v_dropoff_address_id,
	v_prepaid,
	v_payment_due,
	v_create_time,
	v_pickup_time_requested,
	v_package_size,
	v_estimated_worth
	);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `add_prediction` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`pico_admin`@`%` PROCEDURE `add_prediction`(IN v_area_id INT, IN v_start_hour DATETIME, IN v_predicted_value INT)
BEGIN
	SELECT @existing_count := count(*)
    FROM  hourly_prediction
    WHERE area_id = v_area_id
    AND start_hour = v_start_hour
    AND predicted_value = v_predicted_value;

    IF @existing_count = 0 THEN
		INSERT INTO hourly_prediction
        (area_id, start_hour, predicted_value)
        VALUES (v_area_id, v_start_hour, v_predicted_value);
	ELSE
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Prediction already exists for the row attempted to insert upon.';
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_areas_and_current_opacities` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`pico_admin`@`%` PROCEDURE `get_areas_and_current_opacities`()
BEGIN
	DECLARE total DOUBLE;
	SELECT sum(predicted_value) into total
	FROM hourly_prediction
	WHERE start_hour > now();

    if (total = 0) then
		SET total = 1;
	END IF;

	Select a.id, AsText(a.area) as area, (hp.predicted_value/total) as opacity
	From hourly_prediction hp
	JOIN area a ON hp.area_id = a.id
	WHERE start_hour > now()
	AND hp.id in
	(SELECT MAX(id)
	FROM hourly_prediction
	GROUP BY area_id);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `get_unpredicted_rows_occurred_for_area` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8 */ ;
/*!50003 SET character_set_results = utf8 */ ;
/*!50003 SET collation_connection  = utf8_general_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`pico_admin`@`%` PROCEDURE `get_unpredicted_rows_occurred_for_area`(IN v_area_id INT)
BEGIN
SELECT start_hour, count_of_jobs
	FROM aggregate_hourly_jobs
	WHERE area_id = v_area_id
    AND start_hour < DATE_FORMAT(now(), "%Y-%m-%d %H:00:00")
	AND DATE_ADD(start_hour, INTERVAL 1 HOUR) NOT IN (
	  SELECT start_hour
	  FROM hourly_prediction
	  WHERE area_id = v_area_id
	);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-04-02  4:06:46
