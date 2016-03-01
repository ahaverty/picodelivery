'''
For each restaurant, get the details needed (id)
Have a var set to define the date range to create jobs over
Use an array for the range of jobs that should be created for each hour/day (1 array for day, 1 for hours)
Restaurants should probably differ in size, set a restaurant with a size between some range and multiply the amount of jobs by it? 1 - 2 (Shouldn't change for the restaurant once set!!!!)
'''

import sys
import os
from datetime import datetime, timedelta
from random import uniform, randrange

from dateutil import rrule

from configuration import simulators_sql
from picodelivery import logger, configHelper, databaseHelper

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

def main(argv):
    
    if len(argv) < 2:
        usage(2)

    connection = databaseHelper.getDbConnection(config)

    fromDate = datetime.strptime(argv[0], '%Y-%m-%d')
    # TODO possibly use the second argument to define how many days to insert from the fromDate..
    toDate = datetime.strptime(argv[1], '%Y-%m-%d')
    # TODO maybe limit the max days allowed to avoid any mistakes when passing in dates...

    log.info("Beginning simulator with parameters: %s - %s" % (fromDate, toDate))

    restaurantIds = getRestaurantIdsFromDb(connection)

    numberOfRestaurants = len(restaurantIds)
    totalDaysDifference = abs((toDate - fromDate).days)
    avgSize = ((minSize + maxSize) / 2)
    avgVariance = ((minVariance + maxVariance) /2)
    avgDayWeight = (sum(float(x) for x in frequencyDays) / len(frequencyDays))
    avgHourlyWeight = (sum(float(x) for x in frequencyHours) / len(frequencyHours))

    avgJobsPerRestuarant = avgSize * avgVariance * avgDayWeight * avgHourlyWeight
    estimateTotalRows = avgJobsPerRestuarant * numberOfRestaurants * totalDaysDifference

    log.info("Estimating %s total rows, for %s restaurants over %s days." % (estimateTotalRows, numberOfRestaurants, totalDaysDifference))

    if queryYesNo("Do you wish to continue?") == False:
        exit(25)    # Document exit codes

    for restaurantId in restaurantIds:
        createJobDetailEntriesForRestaurant(connection, restaurantId, fromDate, toDate)

    log.info("Committing and closing connection with database.")
    connection.commit()
    connection.close()




def usage(exitCode):
    print "Usage: job_detail_simulator.py fromdate(YYYY-mm-dd) todate(YYYY-mm-dd)"
    print "Error, exiting..."
    log.error("Exiting program with exit code %s" % exitCode)
    exit(exitCode)


def queryYesNo(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
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


def createJobDetailEntriesForRestaurant(connection, restaurantId, fromDate, toDate):
    # Randomly choose the size of the restaurant
    size = uniform(minSize, maxSize)

    # Iterate through each hour between the dates, generating a job count and inserting
    for dt in rrule.rrule(rrule.HOURLY, dtstart=fromDate, until=toDate):
        jobCountForHour = generateJobCount(size, dt.weekday(), dt.hour)
        log.debug("#" + str(restaurantId) + " - " + str(dt) + " job count: " + str(jobCountForHour))

        # Will need to randomly disperse the amount of orders first and create individual instances..
        disperseAndInsertIndividualJobs(connection, restaurantId, dt, jobCountForHour)


def getRestaurantIdsFromDb(connection):
    restaurantIds = []

    cursor = connection.cursor()
    cursor.execute(simulators_sql.allRestaurantIds)

    row = cursor.fetchone()
    while row:
        restaurantIds.append(row['id'])
        row = cursor.fetchone()

    return restaurantIds


def generateJobCount(size, day, hour):
    # Get a count of jobs using the hour/week graph values and a random multiplier between the min and max ranges
    return int(round(size * float(frequencyDays[day]) * uniform(minVariance, maxVariance) * float(frequencyHours[hour]) * multiplier))


def randomDate(start, end):
    """
    This function will return a random datetime between two datetime objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


def disperseAndInsertIndividualJobs(connection, restaurantId, startingHour, jobCountForHour):
    '''
    Given an overall amount of orders for a restaurant in an hour,
    create randomly dispersed order instances
    and insert into the job detail table
    '''

    jobInstanceValues = []

    for i in range(jobCountForHour):
        # Get a random time for each job instance
        time = randomDate(startingHour, startingHour + timedelta(hours=1))

        # Get a random worth for the job within a range
        worth = round(uniform(minWorth, maxWorth),2)

        # List using restaurantId and two times to conform
        # to executemany() in pymsql to make transactions faster.
        jobInstanceValues.append([restaurantId, time, time, worth])

    # Sort the list by datetime
    sortedJobInstanceValues = sorted(jobInstanceValues, key=lambda jobInstanceValues: jobInstanceValues[1])

    # for jobInstance in sortedJobInstanceValues:
    #     # Insert the job instance to the DB
    insertManyJobDetailEntriesToDb(connection, sortedJobInstanceValues)


def insertManyJobDetailEntriesToDb(connection, instanceValues):
    cursor = connection.cursor()
    
    try:
        cursor.executemany(simulators_sql.insertJobDetailSql, instanceValues)
    except Exception as e:
        log.exception("executemany() raised an exeption..")
        log.error("Rolling back")
        connection.rollback()
        sys.exit(10)

if __name__ == "__main__":
    log = logger.setupCustomLogger(os.path.basename(__file__))
    main(sys.argv[1:])
