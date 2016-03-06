"""
Purpose:
Instantiated hourly
Trigger the run (or swarm if no modelparams exists)
for each area and its data (only its past unpredicted data) in the db
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
    connection = databaseHelper.getDbConnection(config)
    areaIds = getAreaIdsFromDatabase(connection)

    for area in areaIds:
        log.info("Running controller.py for area id #%s" % area)
        # run each controller in the background/carry on once called
        subprocess.Popen('python controller.py ' + str(area), shell=True)
        time.sleep(2)  # Sleeping between each area to avoid database collisions when checking if swarming

    log.info("Exiting trigger_run.py, subprocesses may still be running in the background...")
    exit()


def printUsageAndExit(exitCode):
    print usage
    log.error("Exiting program with exit code %s" % exitCode)
    sys.exit(exitCode)


def getAreaIdsFromDatabase(connection):
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
