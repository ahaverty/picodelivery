#insertJobDetailSql = "CALL add_job_detail(%s, 1, 6, 1, 0.00, %s, %s, 1, %s)"
insertJobDetailSql = "INSERT IGNORE INTO job_detail (restaurant_id, create_time, pickup_time_requested) VALUES (%s, %s, %s);"
allRestaurantIds = "SELECT id FROM restaurant"
allAreaIds = "SELECT id FROM area"
setDisableTrigger = "SET @DISABLE_TRIGGER=%s"
setDisableKeys = "ALTER TABLE 'job_detail' %s KEYS;"
setAutocommit = "SET autocommit=%s"
setUniqueChecks = "SET unique_checks=%s"
setForeignKeyChecks = "SET foreign_key_checks=%s"
insertIntoAggregateHourlyJobs = "INSERT INTO aggregate_hourly_jobs " \
                                "(area_id, start_hour, count_of_jobs) " \
                                "VALUES " \
                                "(%s, %s, (SELECT count(*) FROM job_detail j " \
                                "JOIN restaurant r ON j.restaurant_id = r.id " \
                                "JOIN address a ON a.id = r.address_id " \
                                "WHERE a.area_id = %s " \
                                "AND j.pickup_time_requested BETWEEN %s AND date_add(%s, INTERVAL 1 HOUR)));"
