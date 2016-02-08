'''
For each restaurant, get the details needed (id)
Have a var set to define the date range to create jobs over
Use an array for the range of jobs that should be created for each hour/day (1 array for day, 1 for hours)
Restaurants should probably differ in size, set a restaurant with a size between some range and multiply the amount of jobs by it? 1 - 2 (Shouldn't change for the restaurant once set!!!!)
'''

import sys
from random import uniform, randrange
from dateutil import rrule
from datetime import datetime, timedelta
import pymysql

import dbconfig

from job_frequencies import day as DAY
from job_frequencies import hour as HOUR

multiplier = 1
minSize = 1.3
maxSize = 1.8

minVariance = 0.8
maxVariance = 1.2

minWorth = 4
maxWorth = 8

def main(argv):
    connection = getDbConnection()

    fromDate = datetime.strptime(argv[0], '%Y-%m-%d')
    # TODO possibly use the second argument to define how many days to insert from the fromDate..
    toDate = datetime.strptime(argv[1], '%Y-%m-%d')
    # TODO maybe limit the max days allowed to avoid any mistakes when passing in dates...

    restaurantIds = getRestaurantIdsFromDb(connection)

    for restaurantId in restaurantIds:
        createJobDetailEntriesForRestaurant(connection, restaurantId, fromDate, toDate)

    connection.commit()
    connection.close()


def usage(exitCode):
    # TODO
    pass
    exit(exitCode)


def getDbConnection():
    connection = pymysql.connect(host=dbconfig.host,
                                 user=dbconfig.user,
                                 passwd=dbconfig.password,
                                 db=dbconfig.db,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    return connection


def createJobDetailEntriesForRestaurant(connection, restaurantId, fromDate, toDate):
    # Randomly choose the size of the restaurant
    size = uniform(minSize, maxSize)

    # Iterate through each hour between the dates, generating a job count and inserting
    for dt in rrule.rrule(rrule.HOURLY, dtstart=fromDate, until=toDate):
        jobCountForHour = generateJobCount(size, dt.weekday(), dt.hour)
        print "#" + str(restaurantId) + " - " + str(dt) + " job count: " + str(jobCountForHour)

        # Will need to randomly disperse the amount of orders first and create individual instances..
        disperseAndInsertIndividualJobs(connection, restaurantId, dt, jobCountForHour)


def getRestaurantIdsFromDb(connection):
    restaurantIds = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM restaurant")

    row = cursor.fetchone()
    while row:
        restaurantIds.append(row['id'])
        row = cursor.fetchone()

    return restaurantIds


def generateJobCount(size, day, hour):
    # Get a count of jobs using the hour/week graph values and a random multiplier between the min and max ranges
    return int(round(size * DAY[day] * uniform(minVariance, maxVariance) * HOUR[hour] * multiplier))

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
    insertJobDetailSql = "INSERT INTO job_detail " \
                         "(restaurant_id," \
                         "status_id," \
                         "dropoff_address_id," \
                         "prepaid," \
                         "payment_due," \
                         "create_time," \
                         "pickup_time_requested," \
                         "package_size," \
                         "estimated_worth)" \
                         "VALUES (%s, 1, 6, 1, 0.00, %s, %s, 1, %s)"

    cursor = connection.cursor()
    cursor.executemany(insertJobDetailSql, instanceValues)
    #TODO remove temporary commit from here...
    connection.commit()


if __name__ == "__main__":
    main(sys.argv[1:])
