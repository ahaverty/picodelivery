"""
The controller takes in an area id and either makes the next prediction(s) it can,
using the available aggregated count of jobs from the database
passing it through NuPIC
OR
Triggers a swarm on the data if there is enough data to swarm upon
(Swarming is how NuPIC trains a model)

Overview of the controller:
Get area id as a parameter
Check whether modelparams file exists for the area
    modelparams found:
        look for savemodel or modelparams
            predict latest data and save

    modelparams not found:
        check if a process is currently swarming
            exit if it is
        otherwise, start a swarm, and store swarm progress to the db
            then go back and look for model params again, making a prediction.

@author alanhavert@student.dit.ie
"""

import os
import subprocess
import sys
from datetime import timedelta

import picodelivery.prediction.run
from configuration import predictions_run_sql
from picodelivery import logger, configHelper, databaseHelper

usage = "Usage: controller.py areaId"
countOfJobs = "countOfJobs"
startHour = "startHour"

config = configHelper.getConfig("../project_config.ini")

swarmLimit = int(config.get('simulator_jobs', 'swarmLimit'))
swarmMinimum = int(config.get('simulator_jobs', 'swarmMinimum'))


def main(argv):
    if len(argv) < 1:
        printUsageAndExit(2)
    else:
        try:
            areaId = int(argv[0])
            steps = 1

            modelParamsPath = "../area_data/area_" + str(areaId) + "/model_params.py"
            savedModelsPath = "../area_data/area_" + str(areaId) + "/saved_model/"

        except Exception:
            printUsageAndExit(3)

    connection = databaseHelper.getDbConnection(config)

    print "Enabling autocommit, to ensure swarming status can be read across instances of controller.py"
    connection.autocommit(True)

    if not modelsParamExists(areaId):
        # delay triggering of each area to avoid collisions on this check
        if not swarmInProgress(connection):

            # check there is enough data to swarm on first.
            if hasEnoughRowsToSwarm(connection, areaId, swarmMinimum):
                # Publish that the swarm process has begun to the db
                publishSwarmingStatusToDb(connection, areaId, True)

                # Generate a csv of the data to use in the swarm
                generateAggregateDataFileAndStructure(connection, areaId, swarmLimit)
                triggerSwarmAndWait(areaId)

                # Publish that the swarm process is complete
                publishSwarmingStatusToDb(connection, areaId, False)
            else:
                log.warning("Not enough rows to swarm on area %s. Exiting controller.py" % areaId)
                sys.exit(15)
        else:
            log.warning("Another process is currently swarming, only one swarm can run at a time. [%s]" % areaId)
            log.warning("Therefore exiting controller.py")
            sys.exit(10)

    #Trigger NuPIC to predict on the latest area aggregated data
    runOnLatestData(connection, areaId, steps, absPathAndVerify(modelParamsPath), absPath(savedModelsPath))

    log.info("Committing and closing the database connection.")
    connection.commit()
    connection.close()


def printUsageAndExit(exitCode):
    print usage
    log.error("Exiting program with exit code %s" % exitCode)
    sys.exit(exitCode)


def absPath(path):
    """
    Get the absolute path of the provided relative path
    :param path:
    :return:
    """
    return str(os.path.abspath(path))


def absPathAndVerify(path):
    """
    Get the absolute path and verify it exists or exit program
    :param path:
    :return:
    """
    absolutePath = absPath(path)
    if os.path.exists(absolutePath):
        return absolutePath
    else:
        print "%s is not an absolute path that exists. Exiting controller.py." % absolutePath
        exit(3)


def modelsParamExists(areaId):
    """
    Check if the model parameter file exists and return true or false
    :param areaId:
    :return: True if model params exists, false otherwise
    """
    modelParamExpectedPath = "../area_data/area_" + str(areaId) + "/model_params.py"
    return os.path.isfile(modelParamExpectedPath)


def hasEnoughRowsToSwarm(connection, areaId, minimumRows=1000):
    """
    Check if the area has the minimum amount of rows to perform a swarm
    (Too few rows in a swarm will result in a weak model)
    :param areaId:
    :param minimumRows:
    :return:
    """
    cursor = connection.cursor()
    cursor.execute(predictions_run_sql.areaHasEnoughRowsToSwarm, (areaId))
    row = cursor.fetchone()
    areaRowCount = row['count']
    if areaRowCount >= minimumRows:
        return True
    else:
        log.warning("Area %s has only %s rows of data." % (areaId, areaRowCount))
        return False

def swarmInProgress(connection, hoursBeforeIgnoring=4):
    '''
    Check if a swarm is currently marked as 'in progress' in the database.
    :param connection:
    :param hoursBeforeIgnoring: The maximum hours before ignoring the
    'currently running swarm' row. This means that if a swarm seems to be
    running for x hours, it has probably failed, and never wrote that
    it was finished, to the database. Therefore, allowing a new swarm to
    begin, avoiding an endless loop bug.
    :return:
    '''
    currentlySwarming = False
    cursor = connection.cursor()
    cursor.execute(predictions_run_sql.swarmingCheck, hoursBeforeIgnoring)

    row = cursor.fetchone()
    if row is not None:
        if row['in_progress'] > 0:
            currentlySwarming = True
    else:
        log.warning("Returned None row from swarm table, this should only occur when the swarm table "
                    "is empty on the very first swarm run.")

    # Return False unless a row was returned
    # and the value was greater than 0 (i.e 1/True)
    return currentlySwarming


def publishSwarmingStatusToDb(connection, areaId, status):
    """
    Publish that a swarm is in progress to the db, to ensure no other process
    starts the same swarm. (NuPIC recommends only running one swarm at a time)
    :param connection:
    :param areaId:
    :param status:
    :return:
    """
    if status is True:
        inProgress = 1
    else:
        inProgress = 0

    cursor = connection.cursor()

    log.info("Adding swarm record to db for area %s, as %s" % (areaId, status))
    cursor.execute(predictions_run_sql.insertSwarmingForAreaRecord, (areaId, inProgress))


def generateAggregateDataFileAndStructure(connection, areaId, limit):
    """
    Generate the csv file used for swarming, from the mysql db for the specified areaId
    Also setup the folder structure if not already created
    :return:
    """
    cursor = connection.cursor()
    cursor.execute(predictions_run_sql.areasAggregates, (areaId, limit))

    areaDir = "../area_data/area_" + str(areaId) + "/"
    dataFilepath = areaDir + "area_" + str(areaId) + "_aggregates.csv"

    if not os.path.exists(areaDir):
        os.makedirs(areaDir)

    f = open(dataFilepath, 'w')

    try:
        row = cursor.fetchone()
        while row:
            f.write("%s, %s\n" % (row['timestamp'], row['numberOfDeliveries']))
            row = cursor.fetchone()
    finally:
        f.close()
        log.info("Created aggregate file at %s" % dataFilepath)


def triggerSwarmAndWait(areaId):
    """
    Trigger a swarm, using the swarm.py script and wait for it to finish
    :param areaId:
    :return:
    """
    log.info("Starting swarm process on area with id %s, which may take awhile." % areaId)
    log.info("Adding details of the instantiated swarm process to the database "
             "to ensure no overlapping processes start.")

    cmd = ["sudo python swarm.py " + str(areaId)]
    swarmProcess = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    log.info("Swarm process successfully started, currently waiting on swarm to complete (May take awhile)...")
    log.warning("Note: Only one swarm should run at a time.")

    # Grab stdout line by line as it becomes available.  This will loop until
    # swarmProcess terminates.
    while swarmProcess.poll() is None:
        l = swarmProcess.stdout.readline()  # This blocks until it receives a newline.
        log.info("[swarm.py]: %s" % l)
    # When the subprocess terminates there might be unconsumed output
    # that still needs to be processed.
    print swarmProcess.stdout.read()

    # TODO implement better error handling and checking exit code..

    log.info("Swarm on area %s completed." % areaId)


def runOnLatestData(connection, areaId, steps, modelParamsPath, savedModelsPath):
    """
    Initialise NuPIC to predict on an areas latest aggregated data.
    Save model to file once completed
    :param connection:
    :param areaId:
    :param steps:
    :param modelParamsPath:
    :param savedModelsPath:
    :return:
    """

    # Initialise nupic/run.py
    nupic = picodelivery.prediction.run.Run(modelParamsPath, savedModelsPath, steps)

    try:
        rowsWithoutPredictions = getRowsWithoutPredictions(connection, areaId)

        for row in rowsWithoutPredictions:
            predictedHour = row[startHour] + timedelta(hours=steps)
            predictedCountOfJobs = nupic.predict(row[startHour], row[countOfJobs])

            log.debug(
                "row@StartHour:{}\tPredictedHour:{}\trow@CountOfJobs:{}\tPredictedCountOfJobs:{}".format(row[startHour],
                                                                                                         predictedHour,
                                                                                                         row[
                                                                                                             countOfJobs],
                                                                                                         predictedCountOfJobs))

            savePredictionToDatabase(connection, areaId, predictedHour, predictedCountOfJobs)
    finally:
        # Save the model once complete
        log.info("Saving the nupic model to file.")
        nupic.saveModel()


def savePredictionToDatabase(connection, areaId, startHour, predictedValue):
    """
    Save a predicted row to the database
    :param connection:
    :param areaId:
    :param startHour:
    :param predictedValue:
    :return:
    """
    cursor = connection.cursor()
    cursor.execute(predictions_run_sql.insertPredictionResult, (areaId, startHour, float(predictedValue)))


def getRowsWithoutPredictions(connection, areaId):
    """
    Get any rows that are yet to have predictions made
    :param connection:
    :param areaId:
    :return:
    """
    rowsWithoutPredictions = []

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

    return rowsWithoutPredictions


if __name__ == "__main__":
    log = logger.setupCustomLogger(sys.argv[0])
    main(sys.argv[1:])
