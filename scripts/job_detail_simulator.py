"""

Simulator which creates job details (driver requests)
Simulator looks at all the restaurants in the database
Decides on a size for the restaurant (ie. small, med, large..)
Then creates jobs dispersed in a random manor, using the configuration as a
reference on which hours and days are busiest (job rate curve)

Overview:
For each restaurant, get the details needed (id)
Have a var set to define the date range to create jobs over
Use an array for the range of jobs that should be created for each hour/day (1 array for day, 1 for hours)
Restaurants should probably differ in size, set a restaurant
with a size between some range and multiply the amount of jobs by it?

@author alanhaverty@student.dit.ie
"""


import sys
import traceback
import argparse
import time
from datetime import datetime, timedelta
from random import uniform, randrange

from collections import defaultdict
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
    '-y', '--yes',
    help="Run script, answering yes to all questions as default",
    action='store_true'
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
st = datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
fh = logging.FileHandler('logs/job_detail_simulator_' + st + '_.log')
log.addHandler(fh)

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

jobDetailTable = config.get('simulator_jobs', 'jobDetailTable')
aggregateHourlyJobsTable = config.get('simulator_jobs', 'aggregateHourlyJobsTable')



def main():
    startDate = datetime.strptime(str(args.start), '%Y-%m-%d')
    endDate = datetime.strptime(str(args.end), '%Y-%m-%d')

    log.info("Beginning simulator with parameters: %s - %s" % (startDate, endDate))

    connection = databaseHelper.getDbConnection(config)
    cursor = connection.cursor()

    restaurantIds = getAllRestaurantIdsFromDb(cursor)

    numberOfRestaurants = len(restaurantIds)
    totalDaysDifference = abs((endDate - startDate).days)

    # Get an estimation on how many rows and how long the script will take to complete
    estimateTotalRows = estimateTotalInsertRows(numberOfRestaurants, startDate, endDate)

    log.info("Estimating {:,} total rows, for {:,} restaurants over {:,} days.".format(int(estimateTotalRows), numberOfRestaurants, totalDaysDifference))

    # If the yes argument was not provided, first check if the user wants to continue
    if not args.yes:
        if not queryYesNo("Do you wish to continue?"):
            exit(25)    # Document exit codes

    start = datetime.now()
    try:
        # TODO Add a check if rows exist in either table before beginning.
        log.debug("Starting at %s" % start)
        setDatabaseForBulkInserts(cursor, True)

        areaHourlyJobCount = defaultdict(list)

        count = 0
        averageTimePerRestaurant = None
        for restaurantId in restaurantIds:
            restaurantStartTime = datetime.now()
            createJobDetailEntriesForRestaurant(cursor, restaurantId, startDate, endDate, areaHourlyJobCount)
            restaurantEndTime = restaurantStartTime - datetime.now()
            if averageTimePerRestaurant is None:
                averageTimePerRestaurant = restaurantEndTime
            averageTimePerRestaurant = (timedelta(seconds =(averageTimePerRestaurant + restaurantEndTime).total_seconds() / 2))
            remainingRestaurants = (len(restaurantIds) - count)
            log.debug("Estimating %s until finished creating jobdetails for the remaining %s restaurants" % (timedelta(seconds = remainingRestaurants * averageTimePerRestaurant.total_seconds()), remainingRestaurants))
            count += 1


        createJobsCompleteTime = datetime.now()
        log.debug("Completed creating job detail entries at %s, taking a total time of %s" % (createJobsCompleteTime, createJobsCompleteTime - start))

        #Must manually insert the aggregates since disabling the trigger due to performance issues
        manuallyInsertAggregateHourlyJobs(cursor, areaHourlyJobCount)

        aggregationCompleteTime = datetime.now()
        log.debug("Completed manually aggregating job detail entries at %s, taking a total time of %s" % (aggregationCompleteTime, aggregationCompleteTime - createJobsCompleteTime))

        setDatabaseForBulkInserts(cursor, False)

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
    """
    Estimate of how many rows will be inserted into the database
    Handy to debug before running the long script!
    :param numberOfRestaurants:
    :param startDate:
    :param endDate:
    :return:
    """
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


def getAllRestaurantIdsFromDb(cursor):
    """
    Get the ids of all the restaurants from the database
    :param cursor:
    :return:
    """
    restaurantIds = []

    cursor.execute(simulators_sql.allRestaurantIds)

    row = cursor.fetchone()
    while row:
        restaurantIds.append(row['id'])
        row = cursor.fetchone()

    return restaurantIds


def setDatabaseForBulkInserts(cursor, state):
    """
    Setup the database for bulk inserting/efficiency
    i.e. disable triggers and keys to avoid more work for the db
    (Triggers should also be simulated elsewhere)
    :param cursor:
    :param state: True to turn setup for bulk inserts, false to undo
    :return:
    """

    if state:
        value = 0
        message = "DISABLING"
        keys = simulators_sql.setDisableKeys
    else:
        value = 1
        message = "ENABLING"
        keys = simulators_sql.setEnableKeys

    log.debug("%s keys, aggregate trigger, unique checks, and foreign key checks" % message)

    cursor.execute(keys, (jobDetailTable))
    cursor.execute(simulators_sql.setDisableTrigger, (value))
    cursor.execute(simulators_sql.setUniqueChecks, (value))
    cursor.execute(simulators_sql.setForeignKeyChecks, (value))

    log.debug("Finished %s keys, aggregate trigger, unique checks, and foreign key checks" % message)


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


def createJobDetailEntriesForRestaurant(cursor, restaurantId, startDate, endDate, areaHourlyJobCount):
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
    # TODO save size somewhere

    areaId = getRestaurantsAreaId(cursor, restaurantId)

    log.debug("Creating jobs for restaurant with id %s in area %s at a size of %s%%" % (restaurantId, areaId, ((size/maxSize)*100)))

    restaurantDateAndJobCounts = []
    # Iterate through each hour between the dates, generating job counts
    for dt in rrule.rrule(rrule.HOURLY, dtstart=startDate, until=endDate):
        restaurantDateAndJobCounts.append([dt, generateJobCountForHour(size, dt.weekday(), dt.hour)])

    insertData = []
    for restaurantDateAndJobCount in restaurantDateAndJobCounts:
        # Add the total jobs per hour to the area counter array
        existed = False
        for areaDateAndJobCount in areaHourlyJobCount[areaId]:
            # Check if the hour already exists for the area
            if restaurantDateAndJobCount[0] == areaDateAndJobCount[0]:
                existed = True
                # Add to the existing total
                areaDateAndJobCount[1] += restaurantDateAndJobCount[1]
        # If the area didn't have the hour already, add it now
        if not existed:
            areaHourlyJobCount[areaId].append(restaurantDateAndJobCount)

        # Randomly disperse the amount of orders, then sort by date
        dispersedJobsForHour = disperseJobsForHour(restaurantDateAndJobCount[0], restaurantDateAndJobCount[1])
        for jobTime in dispersedJobsForHour:
            # Add the job times and the restaurant into an array as per the executemany()
            insertData.append((jobDetailTable, restaurantId, jobTime, jobTime))


    log.debug("Adding {:,} jobs for restaurant with id {:,}".format(len(insertData), restaurantId))
    insertManyJobDetailEntriesToDb(cursor, insertData)


def insertManyJobDetailEntriesToDb(cursor, data):
    cursor.executemany(simulators_sql.insertJobDetailSql, data)


def getRestaurantsAreaId(cursor, restaurantId):
    """
    Gets the areaid of the area in which the restaurant resides.
    :param cursor:
    :param restaurantId:
    :return:
    """
    cursor.execute(simulators_sql.getRestaurantsAreaId, restaurantId)

    row = cursor.fetchone()
    while row:
        return row['id']


def getAreaIdsFromDatabase(cursor):
    """
    Get all the area ids from the database
    :param cursor:
    :return:
    """
    areaIds = []

    cursor.execute(simulators_sql.allAreaIds)

    row = cursor.fetchone()
    while row:
        areaIds.append(row['id'])
        row = cursor.fetchone()

    return areaIds


def manuallyInsertAggregateHourlyJobs(cursor, areaHourlyJobCount):
    """
    Manually insert the aggregates job counts that the triggers would have done otherwise
    (Triggers were disabled for efficiency, therefore need to insert these rows in bulk manually now)
    :param cursor:
    :param areaHourlyJobCount:
    :return:
    """
    log.info("Beginning manual inserts for aggregate hourly jobs")
    log.debug("Found %s areas" % (len(areaHourlyJobCount)))

    data = []
    for key in areaHourlyJobCount:
        for hour in areaHourlyJobCount[key]:
            data.append((aggregateHourlyJobsTable, int(key), hour[0], hour[1]))

        log.debug("Adding %s aggregated rows for area %s" % (len(data), key))
        # Executing aggregation in batches of areas.
        cursor.executemany(simulators_sql.insertIntoAggregateHourlyJobs, data)

        # Empty the array for reuse with next area
        del data[:]


if __name__ == "__main__":
    main()
