import sys
import os
import run
import pymysql
import pymysql.cursors
import dbconfig
import sqlstatements
from datetime import timedelta

usage="Usage: controller.py areaId steps modelParamsPathRoot savedModelsPathRoot"
countOfJobs = "countOfJobs"
startHour = "startHour"


def main(argv):
    if len(argv) < 4:
        printUsageAndExit(2)
    else:
        try:
            areaId = int(argv[0])
            steps = int(argv[1])

            modelParamsPath = argv[2] + "/area" + str(areaId) + "_model_params.py"
            savedModelsPath = argv[3] + "/" + str(areaId)
        except Exception:
            printUsageAndExit(3)

        runOnLatestData(areaId, steps, absPathAndVerify(modelParamsPath), absPath(savedModelsPath))

def printUsageAndExit(exitCode):
    print usage
    sys.exit(exitCode)

def absPath(path):
    return str(os.path.abspath(path))

def absPathAndVerify(path):
    absolutePath = absPath(path)
    if os.path.exists(absolutePath):
        return absolutePath
    else:
        print "%s is not an absolute path that exists. Exiting controller.py." % absolutePath
        exit(3)

def runOnLatestData(areaId, steps, modelParamsPath, savedModelsPath):

    # Initialise nupic/run.py
    nupic = run.Run(modelParamsPath, savedModelsPath, steps)

    #Commit prediction to the database
    try:
        connection = getDbConnection()
        rowsWithoutPredictions = getRowsWithoutPredictions(connection, steps, areaId)

        for row in rowsWithoutPredictions:
            predictedHour = row[startHour] + timedelta(hours=steps)
            predictedCountOfJobs = nupic.predict(row[startHour], row[countOfJobs])

            print("row@StartHour:{}\tPredictedHour:{}\trow@CountOfJobs:{}\tPredictedCountOfJobs:{}".format(row[startHour], predictedHour, row[countOfJobs], predictedCountOfJobs))

            savePredictionToDatabase(connection, areaId, predictedHour, predictedCountOfJobs)
    finally:
        connection.commit()
        connection.close()

    # Save the model once complete
    nupic.saveModel()

def getDbConnection():
    connection = pymysql.connect(host=dbconfig.host,
                                 user=dbconfig.user,
                                 passwd=dbconfig.password,
                                 db=dbconfig.db,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    return connection

def savePredictionToDatabase(connection, areaId, startHour, predictedValue):
    with connection.cursor() as cursor:
        cursor.execute(sqlstatements.insertPredictionResult, (areaId, startHour, float(predictedValue)))



def getRowsWithoutPredictions(connection, steps, areaId):
    rowsWithoutPredictions = []

    try:
        with connection.cursor() as cursor:
            # Get rows that that yet have predictions
            cursor.execute(sqlstatements.rowsWithoutPredictions, (steps, areaId, areaId))

            row = cursor.fetchone()
            while row:
                aggregatedJobRow = {
                    countOfJobs: row['count_of_jobs'],
                    startHour: row['start_hour']
                }
                rowsWithoutPredictions.append(aggregatedJobRow)

                row = cursor.fetchone()
    finally:
        connection.close()

    return rowsWithoutPredictions

if __name__ == "__main__":
    main(sys.argv[1:])
