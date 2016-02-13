'''
For each restaurant, get the details needed (id)
Have a var set to define the date range to create jobs over
Use an array for the range of jobs that should be created for each hour/day (1 array for day, 1 for hours)
Restaurants should probably differ in size, set a restaurant with a size between some range and multiply the amount of jobs by it? 1 - 2 (Shouldn't change for the restaurant once set!!!!)
'''

import ConfigParser
import sys
from datetime import datetime, timedelta
from random import uniform, randrange

import pymysql
from dateutil import rrule

import simulators_sql
from picodelivery import logger

configLocation = "../config/config.ini"
config = ConfigParser.ConfigParser()
config.read(configLocation)

multiplier = float(config.get('simulator_jobs', 'multiplier'))
minSize = float(config.get('simulator_jobs', 'minSize'))
maxSize = float(config.get('simulator_jobs', 'maxSize'))

minVariance = float(config.get('simulator_jobs', 'minVariance'))
maxVariance = float(config.get('simulator_jobs', 'maxVariance'))

minWorth = float(config.get('simulator_jobs', 'minWorth'))
maxWorth = float(config.get('simulator_jobs', 'maxWorth'))

frequencyDays = config.get('simulator_jobs', 'frequencyDays').split(', ')
frequencyHours = config.get('simulator_jobs', 'frequencyHours').split(', ')

log = logger.setupCustomLogger(__name__)

def main(argv):
    
    if len(argv) < 2:
        usage(2)

    connection = getDbConnection()

    fromDate = datetime.strptime(argv[0], '%Y-%m-%d')
    # TODO possibly use the second argument to define how many days to insert from the fromDate..
    toDate = datetime.strptime(argv[1], '%Y-%m-%d')
    # TODO maybe limit the max days allowed to avoid any mistakes when passing in dates...

    log.info("Beginning simulator with parameters: %s - %s" % (fromDate, toDate))

    restaurantIds = getRestaurantIdsFromDb(connection)

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


def getDbConnection():
    connection = pymysql.connect(host=config.get('database', 'host'),
                                 user=config.get('database', 'user'),
                                 passwd=config.get('database', 'password'),
                                 db=config.get('database', 'db'),
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    return connection


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
    cursor.executemany(simulators_sql.insertJobDetailSql, instanceValues)


if __name__ == "__main__":
    main(sys.argv[1:])
