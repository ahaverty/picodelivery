rowsWithoutPredictions = "CALL get_unpredicted_rows_occurred_for_area(%s)"

insertPredictionResult = "INSERT INTO hourly_prediction " \
                         "(area_id, start_hour, predicted_value) " \
                         "VALUES (%s, %s, %s)"

areaIds = "SELECT id FROM area"

swarmingForAreaCheck = "SELECT in_progress " \
                       "FROM swarm " \
                       "WHERE area_id = %s " \
                       "ORDER BY id DESC " \
                       "LIMIT 1"

insertSwarmingForAreaRecord = "INSERT INTO swarm " \
                              "(area_id, in_progress) " \
                              "VALUES (%s, %s)"

areasAggregates = "SELECT 'timestamp','numberOfDeliveries' " \
                  "UNION " \
                  "SELECT 'datetime', 'int' " \
                  "UNION " \
                  "SELECT 'T','' " \
                  "UNION " \
                  "SELECT start_hour, count_of_jobs " \
                  "FROM aggregate_hourly_jobs " \
                  "WHERE area_id = %s"
