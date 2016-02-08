import sys
import os
import run
import pymysql
import pymysql.cursors
import predictions_run_sql
import controller
import ConfigParser
from datetime import timedelta

configLocation = "../../config/config.ini"
config = ConfigParser.ConfigParser()
config.read(configLocation)

'''
Purpose:
Called every hour using a crontab
Trigger the run (and swarm?) of all the data in the db
Run on data that has yet to be predicted upon using a select (already done in controller??)
'''

usage = "Usage: predictions-trigger.py steps modelParamsPathRoot savedModelsPathRoot"


def main(argv):
    if len(argv) < 3:
        printUsageAndExit(2)
    else:
        steps = int(argv[0])

        modelParamsPath = str(argv[1])
        savedModelsPath = str(argv[2])

    areaIds = getAreaIdsFromDatabase()

    for area in areaIds:
        print "running for area id #" + str(area)
        argv = [area, steps, modelParamsPath, savedModelsPath]
        controller.main(argv)

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
