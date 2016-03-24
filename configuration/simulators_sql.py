#insertJobDetailSql = "CALL add_job_detail(%s, 1, 6, 1, 0.00, %s, %s, 1, %s)"
insertJobDetailSql = "INSERT IGNORE INTO job_detail (restaurant_id, create_time, pickup_time_requested) VALUES (%s, %s, %s);"
allRestaurantIds = "SELECT id FROM restaurant"
allAreaIds = "SELECT id FROM area"
setDisableTrigger = "SET @DISABLE_TRIGGER=%s"
setDisableKeys = "ALTER TABLE job_detail DISABLE KEYS;"
setEnableKeys = "ALTER TABLE job_detail ENABLE KEYS;"
setAutocommit = "SET autocommit=%s"
setUniqueChecks = "SET unique_checks=%s"
setForeignKeyChecks = "SET foreign_key_checks=%s"
getRestaurantsAreaId = "SELECT a.area_id as id FROM restaurant r JOIN address a ON a.id = r.address_id WHERE r.id = %s"
insertIntoAggregateHourlyJobs = "INSERT INTO aggregate_hourly_jobs (area_id, start_hour, count_of_jobs) VALUES (%s, %s, %s);"
allDrivers = "SELECT * FROM driver"
getCountOfPendingJobs = "SELECT count(*) as count FROM job j " \
                        "JOIN job_detail jd on jd.id = j.job_detail_id " \
                        "WHERE jd.pickup_time_requested BETWEEN date_sub(now(), INTERVAL %s MINUTE) " \
                        "AND date_add(now(), INTERVAL %s MINUTE) AND j.status_id = 1 "

getDriversOnRecentJobs = "SELECT distinct driver_id FROM job WHERE status_id BETWEEN 2 and 3 " \
                         "AND start_time > date_sub(now(), INTERVAL %s MINUTE)"

getRecentlyActiveDrivers = "SELECT driver_id FROM driver_location " \
                           "WHERE driver_id not in " \
                           "    (SELECT distinct driver_id FROM job " \
                           "	WHERE status_id BETWEEN 2 and 3 " \
                           "	AND start_time > date_sub(now(), INTERVAL %s MINUTE) " \
                           "    ) " \
                           "AND captured > date_sub(now(), INTERVAL %s MINUTE)"
createJobDetail = "INSERT INTO job_detail (restaurant_id, customer_id, pickup_time_requested) VALUES (%s, %s, %s)"

deleteJobDetail = "DELETE FROM job_detail WHERE id = %s"

updateJob = "UPDATE job SET driver_id = %s, status_id = %s, start_time = %s WHERE job_detail_id = %s"

updateDriverLocation = "INSERT INTO driver_location (driver_id, coordinates) " \
                     "VALUES (%s,  GeomFromText('POINT(%s %s)')) " \
                     "ON DUPLICATE KEY UPDATE coordinates=VALUES(coordinates)"
createUser = "INSERT INTO user (email, first_name, last_name) VALUES (%s, %s, %s)"
createDriver = "INSERT INTO driver (user_id, first_name, last_name, mobile_number) VALUES (%s, %s, %s, %s)"