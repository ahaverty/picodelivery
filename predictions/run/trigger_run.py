"""
Purpose:
Instantiated hourly
Trigger the run (or swarm if no modelparams exists)
for each area and its data (only its past unpredicted data) in the db
"""

import sys
import pymysql
import pymysql.cursors
import predictions_run_sql
import ConfigParser
import subprocess

configLocation = "../../config/config.ini"
config = ConfigParser.ConfigParser()
config.read(configLocation)

usage = "Usage: predictions-trigger.py"


def main(argv):
    if len(argv) < 1:
        printUsageAndExit(2)
    else:
        steps = int(argv[0])

    areaIds = getAreaIdsFromDatabase()

    for area in areaIds:
        print "running for area id #" + str(area)
        # argv = [area, steps, modelParamsPath, savedModelsPath]
        # run each controller in the background/carry on once called
        subprocess.Popen(['python controller.py', area])
        # controller.main(argv)

def printUsageAndExit(exitCode):
    print usage
    sys.exit(exitCode)

def getDbConnection():
    connection = pymysql.connect(host=config.get('database', 'host'),
                                 user=config.get('database', 'user'),
                                 passwd=config.get('database', 'password'),
                                 db=config.get('database', 'db'),
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    return connection

def getAreaIdsFromDatabase():
    areaIds = []
    connection = getDbConnection()

    try:
        with connection.cursor() as cursor:
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
