"""
The trigger run script is the main script called by the crontab
It will instantiate the controller.py script on each of the area ids found in the database
The controller.py scripts are called as subprocesses from here.

@author alanhaverty@student.dit.ie
"""

import os
import subprocess
import sys
import time
from configuration import predictions_run_sql
from picodelivery import logger, configHelper, databaseHelper

config = configHelper.getConfig("../project_config.ini")
usage = "Usage: trigger_run.py"

def main(argv):
    """
    Get all the area ids and trigger the controller.py scripts as a subprocess for each
    (A delay of 4 seconds is added between each controller to ensure that the swarm-in-progress
    flag is not added multiple times)
    :param argv:
    :return:
    """
    connection = databaseHelper.getDbConnection(config)
    areaIds = getAreaIdsFromDatabase(connection)

    for area in areaIds:
        log.info("Running controller.py for area id #%s" % area)
        # run each controller in the background/carry on once called
        subprocess.Popen('python controller.py ' + str(area), shell=True)
        time.sleep(4)  # Sleeping between each area to avoid database collisions when checking if swarming

    log.info("Exiting trigger_run.py, subprocesses may still be running in the background...")
    exit()


def printUsageAndExit(exitCode):
    print usage
    log.error("Exiting program with exit code %s" % exitCode)
    sys.exit(exitCode)


def getAreaIdsFromDatabase(connection):
    """
    Get all the area ids from the database
    :param connection:
    :return:
    """
    areaIds = []

    try:
        cursor = connection.cursor()
        cursor.execute(predictions_run_sql.areaIds)

        row = cursor.fetchone()
        while row:
            areaIds.append(row['id'])

            row = cursor.fetchone()
    finally:
        connection.close()

    return areaIds

if __name__ == "__main__":
    log = logger.setupCustomLogger(os.path.basename(__file__))
    main(sys.argv[1:])
