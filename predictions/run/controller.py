"""
Check whether modelparams exists for an area
    modelparams found:
        look for savemodel or modelparams
            run on latest data

    modelparams not found:
        check if a process is currently swarming
            exit if it is
        otherwise, start a swarm, adding a row to say already swarming
            then go back and look for model params again
"""

import sys
import os
import run
import pymysql
import pymysql.cursors
import ConfigParser
import subprocess
import predictions_run_sql
from datetime import timedelta

usage = "Usage: controller.py areaId steps modelParamsPathRoot savedModelsPathRoot"
countOfJobs = "countOfJobs"
startHour = "startHour"

configLocation = "../../config/config.ini"
config = ConfigParser.ConfigParser()
config.read(configLocation)


def main(argv):

    # TODO Change the parameters to be more defined, similar to how swarm.py is done...
    # TODO Perhaps just areaId is needed at this stage...

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

    connection = getDbConnection()

    if not modelsParamExists(areaId):
        if not currentlySwarmingOnArea(connection, areaId):
            # Publish that the swarm process has begun
            publishSwarmingStatusToDb(connection, areaId, True)

            triggerSwarmAndWait(areaId)

            # Publish that the swarm process is complete
            publishSwarmingStatusToDb(connection, areaId, False)
        else:
            print("Another process is currently swarming on area with id: " + areaId)
            print("Therefore exiting controller.py")
            exit(10)

    runOnLatestData(connection, areaId, steps, absPathAndVerify(modelParamsPath), absPath(savedModelsPath))


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


def modelsParamExists(areaId):
    # TODO define this path better, somewhere more visible...
    modelParamExpectedPath = "../swarm/area_data/area_" + areaId + "/model_params.py"
    # TODO Check that this does not have to be absolute/ is working as expected...
    return os.path.isfile(modelParamExpectedPath)


def currentlySwarmingOnArea(connection, areaId):
    currentlySwarming = False
    with connection.cursor() as cursor:
        cursor.execute(predictions_run_sql.swarmingForAreaCheck, areaId)

    row = cursor.fetchone()
    if row is not None:
        if row['in_progress'] > 0:
            currentlySwarming = True

    # Return False unless a row was returned
    # and the value was greater than 0 (i.e 1/True)
    return currentlySwarming


def publishSwarmingStatusToDb(connection, areaId, status):
    if status is True:
        inProgress = 1
    else:
        inProgress = 0

    with connection.cursor() as cursor:
        cursor.execute(predictions_run_sql.insertSwarmingForAreaRecord, areaId, inProgress)


def triggerSwarmAndWait(areaId):
    print "Starting swarm process on area with id %s, which may take awhile." % areaId
    print "Adding details of the instantiated swarm process to the database" \
          " to ensure no overlapping processes start."

    cmd = ['python ../swarm/swarm.py ' + areaId]
    swarmProcess = subprocess.Popen(cmd)

    print "Swarm process successfully started, currently waiting on swarm to complete (May take awhile)..."

    swarmProcess.wait()

    print "Swarm on area %s completed." % areaId


def runOnLatestData(connection, areaId, steps, modelParamsPath, savedModelsPath):

    # Initialise nupic/run.py
    nupic = run.Run(modelParamsPath, savedModelsPath, steps)

    #Commit prediction to the database
    try:
        rowsWithoutPredictions = getRowsWithoutPredictions(connection, areaId)

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
    connection = pymysql.connect(host=config.get('database', 'host'),
                                 user=config.get('database', 'user'),
                                 passwd=config.get('database', 'password'),
                                 db=config.get('database', 'db'),
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def savePredictionToDatabase(connection, areaId, startHour, predictedValue):
    with connection.cursor() as cursor:
        cursor.execute(predictions_run_sql.insertPredictionResult, (areaId, startHour, float(predictedValue)))


def getRowsWithoutPredictions(connection, areaId):
    rowsWithoutPredictions = []

    try:
        with connection.cursor() as cursor:
            # Get rows that that yet have predictions
            cursor.execute(predictions_run_sql.rowsWithoutPredictions, areaId)

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
