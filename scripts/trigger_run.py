"""
Purpose:
Instantiated hourly
Trigger the run (or swarm if no modelparams exists)
for each area and its data (only its past unpredicted data) in the db
"""

import subprocess
import sys
from configuration import predictions_run_sql
from picodelivery import logger, config, databaseHelper

config = config.getConfig("../configuration/project_config.ini")
log = logger.setupCustomLogger(__name__)

usage = "Usage: trigger_run.py"

def main(argv):
    connection = databaseHelper.getDbConnection(config)
    areaIds = getAreaIdsFromDatabase(connection)

    for area in areaIds:
        log.info( "running for area id #" + str(area))
        # argv = [area, steps, modelParamsPath, savedModelsPath]
        # run each controller in the background/carry on once called
        subprocess.Popen('python controller.py ' + str(area), shell=True)
        # controller.main(argv)

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
    main(sys.argv[1:])
