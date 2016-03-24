'''
Get all the drivers (Except for ones that I control? Where id > than some val TODO...
Give each a work schedule (not too predictable either, vary per week...)
Give each a random starting point within the demo bounds... Persist this val, to use at the start of each shift
At the start of a shift, setPos in db and locally store,
look for jobs and start giveuptimer
    while giveuptimer not up and shift not over
        if job found
            attempt accept after x random seconds/mins
                if accept success
                    do job with some randomness
                    repeat if shift not over, setting loc each time
                if accept fail, go back up to the start of the while

**giveuptimer is there to prevent driver looking for jobs in the middle of the night.... or day.. possibly a smarter solution to this?... define schedules better?...
'''

from configuration import simulators_sql
from picodelivery import configHelper, databaseHelper
from datetime import datetime, timedelta
from random import randint

import logging

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger('driver_simulator')

config = configHelper.getConfig("../project_config.ini")


def main():
    # amountOfUpcomingJobs should equal the amount of drivers
    # Presume 4/5 drivers currently on jobs will pickup another job
    # Presume 4/5 recently active drivers will pickup a new job

    # Weigh up the equation by adding new drivers to the mix
    # amountOfUpcomingJobs = (driversOnJobs.length * (4/5)) + (recentlyActiveDriversNotOnJobs.length * (4/5)) + x
    # x is the number of needed drivers to satisfy the amount of jobs
    # x should be first varied, between 0.8ish and 1.2ish to add realism

    connection = None
    try:
        connection = databaseHelper.getDbConnection(config)
        cursor = connection.cursor()

        minutes = 15
        lookBack = 30

        presumption = (4.0 / 5.0)

        testJobs = setupTestData(cursor, minutes)

        amountOfPendingJobs = getAmountOfPendingJobs(cursor, minutes)
        driversOnJobs = getDriversCurrentlyOnJobs(cursor, lookBack)
        recentlyActiveDriversNotOnJobs = getRecentlyActiveDriversNotOnJobs(cursor, lookBack, lookBack)

        print "pending jobs: %s" % amountOfPendingJobs
        print "drivers on jobs: %s" % len(driversOnJobs)
        print "recently active drivers not on jobs: %s" % len(recentlyActiveDriversNotOnJobs)
        print "presumption: %s" % presumption

        print "presuming %s of drivers on jobs will stay working" % (len(driversOnJobs) * presumption)
        print "presuming %s of recently active drivers will continue working" % (
        len(recentlyActiveDriversNotOnJobs) * presumption)

        newDriversRequired = int(amountOfPendingJobs - (
        (len(driversOnJobs) * presumption) + (len(recentlyActiveDriversNotOnJobs) * presumption)))
        print "require new drivers: " + str(newDriversRequired)

    finally:
        # TODO commit!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        removeTestData(cursor, testJobs)
        print "Closing connection"
        connection.close()


def deleteJobDetail(cursor, jobDetailId):
    cursor.execute(simulators_sql.deleteJobDetail, jobDetailId)


def createJob(cursor, restaurantId, customerId, requestedTime=datetime.now()):
    cursor.execute(simulators_sql.createJobDetail, (restaurantId, customerId, requestedTime))
    cursor.fetchall()
    return cursor.lastrowid


def updateJob(cursor, jobDetailId, driverId, statusId, startTime):
    cursor.execute(simulators_sql.updateJob, (driverId, statusId, startTime, jobDetailId))


def updateDriverLocation(cursor, driverId, lat=1, lng=1):
    cursor.execute(simulators_sql.updateDriverLocation, (driverId, lng, lat))


def setupTestData(cursor, minutes):
    # Need some test job data... then:
    # Setup some drivers on jobs
    # Drivers not on jobs but active

    restaurantId = 354
    customerId = 10
    timeBetweenJobLegs = 7  # The time between accepting, pickup and delivery (test purposes only)
    amountOfActiveJobs = 15
    amountOfPendingJobs = 10

    driverIdsStart = 5

    amountOfRecentActiveDrivers = 5
    activeDriverIds = range(driverIdsStart + amountOfActiveJobs + 1,
                            driverIdsStart + amountOfActiveJobs + 1 + amountOfRecentActiveDrivers)
    timeVariance = [0, minutes]
    activeJobs = []
    pendingJobs = []
    allCreatedJobs = []

    driverId = driverIdsStart
    # Create previous job requests with drivers currently fulfilling
    for i in range(amountOfActiveJobs):
        minutesOffset = randint(timeBetweenJobLegs, timeVariance[1])
        requestedTime = datetime.now() - timedelta(minutes=minutesOffset)
        jobDetailId = createJob(cursor, restaurantId, customerId, requestedTime)
        activeJobs.append(jobDetailId)
        updateJob(cursor, jobDetailId, driverId, 2, requestedTime + timedelta(minutes=timeBetweenJobLegs))
        updateDriverLocation(cursor, driverId)
        driverId += 1

    # Create job requests yet to be accepted..
    for i in range(amountOfPendingJobs):
        minutesOffset = randint(timeVariance[0], timeVariance[1])
        requestedTime = datetime.now() + timedelta(minutes=minutesOffset)
        pendingJobs.append(createJob(cursor, restaurantId, customerId, requestedTime))

    # Simulate some recently active drivers locations, ensuring they are different to the ones used above.
    for i in activeDriverIds:
        updateDriverLocation(cursor, i)

    allCreatedJobs.extend(pendingJobs)
    allCreatedJobs.extend(activeJobs)

    return allCreatedJobs


def removeTestData(cursor, jobIds):
    for jobId in jobIds:
        print "Deleting job with id = %s" % jobId
        deleteJobDetail(cursor, jobId)


def getAmountOfPendingJobs(cursor, minutes):
    cursor.execute(simulators_sql.getCountOfPendingJobs, (minutes, minutes))
    row = cursor.fetchone()
    return row['count']


def getDriversCurrentlyOnJobs(cursor, minutes):
    cursor.execute(simulators_sql.getDriversOnRecentJobs, minutes)
    return cursor.fetchall()


def getRecentlyActiveDriversNotOnJobs(cursor, jobsSince, minutes):
    # TODO minutes here should probably not match.. need to look at what makes sense..
    cursor.execute(simulators_sql.getRecentlyActiveDrivers, (jobsSince, minutes))
    return cursor.fetchall()


if __name__ == "__main__":
    main()
