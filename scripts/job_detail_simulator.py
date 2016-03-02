'''
For each restaurant, get the details needed (id)
Have a var set to define the date range to create jobs over
Use an array for the range of jobs that should be created for each hour/day (1 array for day, 1 for hours)
Restaurants should probably differ in size, set a restaurant with a size between some range and multiply the amount of jobs by it? 1 - 2 (Shouldn't change for the restaurant once set!!!!)
'''

import sys
import os
import traceback
import argparse
from datetime import datetime, timedelta
from random import uniform, randrange

from dateutil import rrule

from configuration import simulators_sql
from picodelivery import configHelper, databaseHelper

import logging

parser = argparse.ArgumentParser(description='Create jobs for every restaurant in the database, based on the configuration file and the dates provided.')
parser.add_argument(
    '-s', '--start',
    help="The date to begin creating jobs from, in the form (YYYY-mm-dd)",
    required=True,
)
parser.add_argument(
    '-e', '--end',
    help="The date to end creating jobs, in the form (YYYY-mm-dd)",
    required=True,
)
parser.add_argument(
    '-d', '--debug',
    help="Print lots of debugging statements",
    action="store_const", dest="loglevel", const=logging.DEBUG,
    default=logging.WARNING,
)
parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    action="store_const", dest="loglevel", const=logging.INFO,
)
args = parser.parse_args()
logging.basicConfig(level=args.loglevel)
log = logging.getLogger('job_detail_simulator')

config = configHelper.getConfig("../project_config.ini")

multiplier = float(config.get('simulator_jobs', 'multiplier'))
minSize = float(config.get('simulator_jobs', 'minSize'))
maxSize = float(config.get('simulator_jobs', 'maxSize'))

minVariance = float(config.get('simulator_jobs', 'minVariance'))
maxVariance = float(config.get('simulator_jobs', 'maxVariance'))

minWorth = float(config.get('simulator_jobs', 'minWorth'))
maxWorth = float(config.get('simulator_jobs', 'maxWorth'))

frequencyDays = config.get('simulator_jobs', 'frequencyDays').split(', ')
frequencyHours = config.get('simulator_jobs', 'frequencyHours').split(', ')


def main():
    startDate = datetime.strptime(str(args.start), '%Y-%m-%d')
    endDate = datetime.strptime(str(args.end), '%Y-%m-%d')

    log.info("Beginning simulator with parameters: %s - %s" % (startDate, endDate))

    connection = databaseHelper.getDbConnection(config)
    cursor = connection.cursor()

    restaurantIds = getRestaurantIdsFromDb(cursor)

    numberOfRestaurants = len(restaurantIds)
    totalDaysDifference = abs((endDate - startDate).days)


    estimateTotalRows = estimateTotalInsertRows(numberOfRestaurants, startDate, endDate)

    log.info("Estimating {:,} total rows, for {:,} restaurants over {:,} days.".format(int(estimateTotalRows), numberOfRestaurants, totalDaysDifference))

    if queryYesNo("Do you wish to continue?") == False:
        exit(25)    # Document exit codes

    try:
        start = datetime.now()
        log.debug("Starting at %s" % start)
        setDatabaseForBulkInserts(cursor, True)

        for restaurantId in restaurantIds:
            createJobDetailEntriesForRestaurant(cursor, restaurantId, startDate, endDate)

        setDatabaseForBulkInserts(cursor, False)

        #Must manually insert the aggregates since disabling the trigger due to performance issues
        manuallyInsertAggregateHourlyJobs(cursor, startDate, endDate)

        log.info("Committing and closing connection with database.")
        connection.commit()
        connection.close()
    except Exception, e:
        log.error("Exception occurred while creating job_details, rolling back and closing connection.")
        connection.rollback()
        connection.close()
        log.error(traceback.format_exc())

    stop = datetime.now()
    log.debug("Started simulator at %s, completed at %s, total time taken: %s" % (start, stop, stop-start))


def queryYesNo(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    question" is a string that is presented to the user.
    default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no"."""

    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def estimateTotalInsertRows(numberOfRestaurants, startDate, endDate) :
    avgSize = ((minSize + maxSize) / 2)
    avgVariance = ((minVariance + maxVariance) /2)
    avgMultiplier = multiplier * avgSize * avgVariance

    jobsPerDayAverage = []
    for dayWeight in frequencyDays:
        dayWeight = float(dayWeight)

        totalPerDay = 0
        for hourWeight in frequencyHours:
            totalPerDay += float(hourWeight)

        jobsPerDayAverage.append(dayWeight * totalPerDay * avgMultiplier)

    # Now have a rough estimate of the amount of jobs per day of the week (e.g. Monday, [0] has 80 jobs, Tuesday, [1] has 68 jobs...)

    estimateTotalRowsPerRestaurant = 0
    iterateDate = startDate
    while iterateDate < endDate:
        estimateTotalRowsPerRestaurant += jobsPerDayAverage[iterateDate.weekday()]
        iterateDate += timedelta(days=1)


    #Then multiply the result by the amount of restaurants
    return estimateTotalRowsPerRestaurant * numberOfRestaurants


def getRestaurantIdsFromDb(cursor):
    restaurantIds = []

    cursor.execute(simulators_sql.allRestaurantIds)

    row = cursor.fetchone()
    while row:
        restaurantIds.append(row['id'])
        row = cursor.fetchone()

    return restaurantIds


def setDatabaseForBulkInserts(cursor, state):
    '''
    Setup the database for bulk inserting/efficiency
    True to turn setup for bulk inserts, false to undo
    :return:
    '''

    if state:
        value = 0
        message = "DISABLING"
        able = "DISABLE"
    else:
        value = 1
        message = "ENABLING"
        able = "ENABLE"

    log.debug("%s autocommit, unique checks, and foreign key checks" % message)

    cursor.execute(simulators_sql.setDisableKeys, (able))
    cursor.execute(simulators_sql.setDisableTrigger, (value))
    cursor.execute(simulators_sql.setUniqueChecks, (value))
    cursor.execute(simulators_sql.setForeignKeyChecks, (value))

    log.debug("Finished %s autocommit, unique checks, and foreign key checks" % message)




def randomDate(start, end):
    """
    This function will return a random datetime between two datetime objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


def disperseJobsForHour(startingHour, jobCountForHour):
    '''
    Given an overall amount of orders for a restaurant,
    create randomly dispersed job times over the hour
    '''

    jobTimesInHour = []

    for i in range(jobCountForHour):
        # Get a random time for each job instance
        jobTimesInHour.append(randomDate(startingHour, startingHour + timedelta(hours=1)))

    # Sort the list by datetime and return it
    return sorted(jobTimesInHour)


def generateJobCountForHour(size, day, hour):
    # Get a count of jobs using the hour/week graph values and a random multiplier between the min and max ranges
    return int(round(size * float(frequencyDays[day]) * uniform(minVariance, maxVariance) * float(frequencyHours[hour]) * multiplier))


def createJobDetailEntriesForRestaurant(cursor, restaurantId, startDate, endDate):
    '''
    Define the size of the restaurant (e.g. Dominos sized or small chipper sized)
    Define an array for each hour (startDate -> endDate), with a value
        Each value is the total amount of deliveries the restaurant made that hour
    Using that array, randomly disperse the jobs across the hour

    :param cursor:
    :param restaurantId:
    :param startDate:
    :param endDate:
    :return:
    '''
    # Randomly choose the size of the restaurant
    size = uniform(minSize, maxSize)

    log.debug("Creating jobs for restaurant with id %s at a size of %s%%" % (restaurantId, ((size/maxSize)*100)))

    dateAndJobAmounts = []

    # Iterate through each hour between the dates, generating job counts
    for dt in rrule.rrule(rrule.HOURLY, dtstart=startDate, until=endDate):
        dateAndJobAmounts.append([dt, generateJobCountForHour(size, dt.weekday(), dt.hour)])

    jobTimesAggregated = []

    for dateAndJobAmount in dateAndJobAmounts :
        # Will need to randomly disperse the amount of orders first and create individual instances..
        dispersedJobsForHour = disperseJobsForHour(dateAndJobAmount[0], dateAndJobAmount[1])
        for jobTimeForHour in dispersedJobsForHour:
            jobTimesAggregated.append(jobTimeForHour)

    data = []
    for jobTime in jobTimesAggregated:
        data.append((restaurantId, jobTime, jobTime))

    log.debug("Adding {:,} jobs for restaurant with id {:,}".format(len(jobTimesAggregated), restaurantId))
    insertManyJobDetailEntriesToDb(cursor, data)


def insertManyJobDetailEntriesToDb(cursor, data):
    cursor.executemany(simulators_sql.insertJobDetailSql, data)


def getAreaIdsFromDatabase(cursor):
    areaIds = []

    cursor.execute(simulators_sql.allAreaIds)

    row = cursor.fetchone()
    while row:
        areaIds.append(row['id'])
        row = cursor.fetchone()

    return areaIds


def manuallyInsertAggregateHourlyJobs(cursor, startDate, endDate):
    log.info("Beginning manual inserts for aggregate hourly jobs")
    areaIds = getAreaIdsFromDatabase(cursor)

    log.debug("Found %s areas" % (len(areaIds)))

    # Iterate through each hour between the dates, generating job counts
    for dt in rrule.rrule(rrule.HOURLY, dtstart=startDate, until=endDate):
        for areaId in areaIds:
            cursor.execute(simulators_sql.insertIntoAggregateHourlyJobs, (areaId, dt, areaId, dt, dt))


if __name__ == "__main__":
    main()
