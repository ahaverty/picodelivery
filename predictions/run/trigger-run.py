import sys
import os
import run
import pymysql
import pymysql.cursors
import dbconfig
import sqlstatements
import controller
from datetime import timedelta

'''
Purpose:
Called every hour using a crontab
Trigger the run (and swarm?) of all the data in the db
Run on data that has yet to be predicted upon using a select (already done in controller??)
'''

usage="Usage: predictions-trigger.py steps modelParamsPathRoot savedModelsPathRoot"


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
    connection = pymysql.connect(host=dbconfig.host,
                                 user=dbconfig.user,
                                 passwd=dbconfig.password,
                                 db=dbconfig.db,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    return connection

def getAreaIdsFromDatabase():
    areaIds = []
    connection = getDbConnection()

    try:
        with connection.cursor() as cursor:
            # Get rows that that yet have predictions
            cursor.execute(sqlstatements.areaIds)

            row = cursor.fetchone()
            while row:
                areaIds.append(row['id'])

                row = cursor.fetchone()
    finally:
        connection.close()

    return areaIds

if __name__ == "__main__":
    main(sys.argv[1:])
