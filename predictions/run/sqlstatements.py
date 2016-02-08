rowsWithoutPredictions = "SELECT count_of_jobs, start_hour" \
                         " FROM aggregate_hourly_jobs" \
                         " WHERE DATE_ADD(start_hour, INTERVAL %s HOUR)" \
                         " NOT IN" \
                         " (SELECT start_hour" \
                         " FROM hourly_prediction " \
                         " WHERE area_id = %s)" \
                         " AND area_id = %s;"

insertPredictionResult = "INSERT INTO hourly_prediction " \
                         "(area_id, start_hour, predicted_value) " \
                         "VALUES (%s, %s, %s)"

areaIds = "SELECT id FROM area"