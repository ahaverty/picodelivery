#!/usr/bin/python
'''
Update the job times and statuses to simulate drivers accepting and completing jobs.
Also update the areas with recent online drivers to allow simulating the heatmap algorithm
'''

from configuration import simulators_sql
from picodelivery import configHelper, databaseHelper
from datetime import datetime, timedelta
from random import randint
import math

import logging

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger('driver_simulator')

config = configHelper.getConfig("../project_config.ini")


def main():
    # Setup 'period', how often this program is ran per hour (e.g 1=every minute, 2=once every two minutes), to determine how often new drivers should be added
    period = 1

    connection = None
    try:
        connection = databaseHelper.getDbConnection(config)
        cursor = connection.cursor()

        updateJobStatusesAndTimes(cursor)
        rateOfJobs = getRateOfJobsFromSimulationAggTable(cursor, period)

        for rate in rateOfJobs:
            jobRate = float(rate['rate'])
            areaId = rate['area_id']
            amountOfNewDrivers = randint(0, math.ceil(jobRate * float(4.0 / 5.0)))
            # Quick algorithm to randomise the amount of drivers added per period, based on the simulated rate of jobs an area has per period
            # print "Area %s has a rate of %s jobs per %s minute, adding %s drivers.." % (areaId, jobRate, period, amountOfNewDrivers)
            touchNewDriversIntoArea(cursor, areaId, amountOfNewDrivers)

        connection.commit()
    finally:
        connection.close()


def getRateOfJobsFromSimulationAggTable(cursor, period):
    dateFormat = "%Y-%m-%d %H:00:00"
    cursor.execute(simulators_sql.getAreaJobRateFromSimAgg, (period, dateFormat))
    return cursor.fetchall()


def updateJobStatusesAndTimes(cursor):
    '''
    Run updates on the job table, giving random time values, drivers, and statuses based on when the job was created etc
    All in one script to cut down on execution time
    :param cursor:
    :return:
    '''
    # TODO abstract the values to config
    cursor.execute(simulators_sql.updateJobStatusesAndTimes)


def getRandomDrivers(cursor, amount):
    cursor.execute(simulators_sql.getRandomDrivers, (amount))
    return cursor.fetchall()

def touchNewDriversIntoArea(cursor, areaId, amountOfDrivers):
    #get amount of random driver ids first.. (preferably ones not on jobs
    #Then update their locations to the centroid of the areas polygon (WATCH ASHTOWN CENTROID IS OUTSIDE OF POLY..)
    randomDrivers = getRandomDrivers(cursor, amountOfDrivers)

    for driver in randomDrivers:
        # Insert or update the last know location for driver in an area.
        cursor.execute(simulators_sql.touchDriverPosition, (driver['id'], areaId))

if __name__ == "__main__":
    main()

