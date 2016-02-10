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

usage = "Usage: controller.py areaId"
countOfJobs = "countOfJobs"
startHour = "startHour"

configLocation = "../../config/config.ini"
config = ConfigParser.ConfigParser()
config.read(configLocation)


def main(argv):

    # TODO Change the parameters to be more defined, similar to how swarm.py is done...
    # TODO Perhaps just areaId is needed at this stage...

    
    if len(argv) < 1:
        printUsageAndExit(2)
    else:
        try:
            areaId = int(argv[0])
            steps = 1  # TODO Hardcoding steps, need to make a decision later

            # TODO Check if this should have the python .py extension or not...
            modelParamsPath = "../swarm/area_data/area_" + str(areaId) + "/model_params"
            savedModelsPath = "../swarm/area_data/area_" + str(areaId) + "/saved_model/"

        except Exception:
            printUsageAndExit(3)

    connection = getDbConnection()

    print "Enabling autocommit, to ensure swarming status can be read across instances of controller.py"
    connection.autocommit(True)

    if not modelsParamExists(areaId):
        if not currentlySwarmingOnArea(connection, areaId):
            # Publish that the swarm process has begun
            publishSwarmingStatusToDb(connection, areaId, True)

            generateAggregateDataFileAndStructure(connection, areaId)
            triggerSwarmAndWait(areaId)

            # Publish that the swarm process is complete
            publishSwarmingStatusToDb(connection, areaId, False)
        else:
            print("Another process is currently swarming on area with id: %s" % areaId)
            print("Therefore exiting controller.py")
            exit(10)

    runOnLatestData(connection, areaId, steps, absPathAndVerify(modelParamsPath), absPath(savedModelsPath))

    connection.commit()
    connection.close()


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
    modelParamExpectedPath = "../swarm/area_data/area_" + str(areaId) + "/model_params.py"
    # TODO Check that this does not have to be absolute/ is working as expected...
    return os.path.isfile(modelParamExpectedPath)


def currentlySwarmingOnArea(connection, areaId):
    currentlySwarming = False
    cursor = connection.cursor()
    cursor.execute(predictions_run_sql.swarmingForAreaCheck, (areaId))

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

    cursor = connection.cursor()
    
    print "Adding swarm record to db for area %s, as %s" % (areaId, status)
    cursor.execute(predictions_run_sql.insertSwarmingForAreaRecord, (areaId, inProgress))


def generateAggregateDataFileAndStructure(connection, areaId):
    """
    Generate the csv file used for swarming, from the mysql db for the specified areaId
    Also setup the folder structure if not already created
    :return:
    """
    cursor = connection.cursor()
    cursor.execute(predictions_run_sql.areasAggregates, areaId)

    areaDir = "../swarm/area_data/area_" + str(areaId) + "/"
    dataFilepath = areaDir + "area_" + str(areaId) + "_aggregates.csv"

    if not os.path.exists(areaDir):
        os.makedirs(areaDir)

    f = open(dataFilepath, 'w')

    row = cursor.fetchone()
    while row:
        f.write("%s, %s" % (row['timestamp'], row['numberOfDeliveries']))  # TODO Double check that the column names conform to the union as I expect here...
        row = cursor.fetchone()

    f.close()


def triggerSwarmAndWait(areaId):
    print "Starting swarm process on area with id %s, which may take awhile." % areaId
    print "Adding details of the instantiated swarm process to the database" \
          " to ensure no overlapping processes start."

    cmd = ["python ../swarm/swarm.py " + str(areaId)]
    swarmProcess = subprocess.Popen(cmd, shell=True)

    print "Swarm process successfully started, currently waiting on swarm to complete (May take awhile)..."

    # Grab stdout line by line as it becomes available.  This will loop until
    # swarmProcess terminates.
    while swarmProcess.poll() is None:
        l = swarmProcess.stdout.readline() # This blocks until it receives a newline.
        print "swarm.py:" + l
    # When the subprocess terminates there might be unconsumed output
    # that still needs to be processed.
    print swarmProcess.stdout.read()

    swarmProcess.wait()  # TODO May not need the wait here, although probably harmless..

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
    cursor = connection.cursor()
    cursor.execute(predictions_run_sql.insertPredictionResult, (areaId, startHour, float(predictedValue)))


def getRowsWithoutPredictions(connection, areaId):
    rowsWithoutPredictions = []

    try:
        cursor = connection.cursor()
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
