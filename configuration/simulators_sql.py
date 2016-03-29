insertJobDetailSql = "INSERT IGNORE INTO %s (restaurant_id, create_time, pickup_time_requested) VALUES (%s, %s, %s);"
allRestaurantIds = "SELECT id FROM restaurant"
allAreaIds = "SELECT id FROM area"
setDisableTrigger = "SET @DISABLE_TRIGGER=%s"
setDisableKeys = "ALTER TABLE %s DISABLE KEYS;"
setEnableKeys = "ALTER TABLE %s ENABLE KEYS;"
setAutocommit = "SET autocommit=%s"
setUniqueChecks = "SET unique_checks=%s"
setForeignKeyChecks = "SET foreign_key_checks=%s"
getRestaurantsAreaId = "SELECT a.area_id as id FROM restaurant r JOIN address a ON a.id = r.address_id WHERE r.id = %s"
insertIntoAggregateHourlyJobs = "INSERT INTO %s (area_id, start_hour, count_of_jobs) VALUES (%s, %s, %s);"


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
createAddress = "INSERT INTO address (street, map_point) VALUES (%s, GEOMFROMTEXT(%s))"
createCustomer = "INSERT INTO customer (first_name, last_name, address_id, mobile_number) VALUES (%s, %s, %s, %s)"
getLastJobDetailTimeSimulated = "SELECT create_time from job_detail WHERE (create_time, restaurant_id) in (select create_time, restaurant_id from simulated_job_detail) ORDER BY create_time desc limit 1;"
insertFromSimulatorToJobDetail = "INSERT INTO job_detail " \
                                 "(restaurant_id, customer_id, create_time, pickup_time_requested, estimated_worth) " \
                                 "SELECT restaurant_id, customer_id, create_time, pickup_time_requested, estimated_worth " \
                                 "FROM simulated_job_detail " \
                                 "WHERE create_time BETWEEN " \
                                 "%s AND sysdate()"

updateJobStatusesAndTimes = "SET @DRIVER_MIN = 36; SET @DRIVER_MAX = 345; " \
                            "SET @MIN_START = 30; SET @MAX_START = 90; " \
                            "SET @MIN_COLLECT = 180; SET @MAX_COLLECT = 600; " \
                            "SET @MIN_DELIVER = 200; SET @MAX_DELIVER = 600; " \
                            "UPDATE job " \
                            "SET start_time =  " \
                            "DATE_ADD(create_time, INTERVAL (@START_INTERVAL := ROUND(RAND() * (@MAX_START - @MIN_START) + @MIN_START)) SECOND), " \
                            "status_id = 2, " \
                            "driver_id = ROUND(RAND() * (@DRIVER_MAX - @DRIVER_MIN) + @DRIVER_MIN) " \
                            "WHERE status_id = 1 " \
                            "AND create_time < DATE_SUB(now(), INTERVAL @MAX_START SECOND); " \
                            "UPDATE job " \
                            "SET payload_collected_time = " \
                            "DATE_ADD(start_time, INTERVAL (ROUND(RAND() * (@MAX_COLLECT - @MIN_COLLECT) + @MIN_COLLECT)) SECOND), " \
                            "status_id = 3 " \
                            "WHERE status_id = 2 " \
                            "AND start_time < DATE_SUB(now(), INTERVAL @MAX_COLLECT SECOND) " \
                            "AND driver_id BETWEEN @DRIVER_MIN AND @DRIVER_MAX; " \
                            "UPDATE job " \
                            "SET end_time = " \
                            "DATE_ADD(payload_collected_time, INTERVAL (ROUND(RAND() * (@MAX_DELIVER - @MIN_DELIVER) + @MIN_DELIVER)) SECOND), " \
                            "status_id = 4 " \
                            "WHERE status_id = 3  " \
                            "AND driver_id BETWEEN @DRIVER_MIN AND @DRIVER_MAX " \
                            "AND payload_collected_time < DATE_SUB(now(), INTERVAL @MAX_DELIVER SECOND);"

getAreaJobRateFromSimAgg = "SELECT count_of_jobs/(60/%s) as rate, area_id " \
                           "from simulated_aggregate_hourly_jobs " \
                           "where start_hour = DATE_FORMAT(now(), %s)"

getRandomDrivers = "select id from driver " \
                   "order by rand() " \
                   "limit %s;"

touchDriverPosition = "INSERT INTO driver_location (driver_id, coordinates) " \
                      "VALUES (%s, (SELECT centroid(area) from area where id = %s))" \
                      "ON DUPLICATE KEY UPDATE coordinates=VALUES(coordinates)"
