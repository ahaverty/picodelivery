rowsWithoutPredictions = "CALL get_unpredicted_rows_occurred_for_area(%s)"

insertPredictionResult = "INSERT INTO hourly_prediction " \
                         "(area_id, start_hour, predicted_value) " \
                         "VALUES (%s, %s, %s)"

areaIds = "SELECT id FROM area"