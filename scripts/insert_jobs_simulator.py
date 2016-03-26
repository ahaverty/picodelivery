'''
Look at current time, look at whats in the job detail table and compare to whats in the simulated job detail table
Add whatever is not already in there..
'''

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

parser = argparse.ArgumentParser(
    description='Create job detail entries taking data from the simulated job detail table')
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
log = logging.getLogger('insert_jobs_simulator')
st = datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
fh = logging.FileHandler('logs/insert_jobs_simulator_' + st + '_.log')
log.addHandler(fh)

config = configHelper.getConfig("../project_config.ini")

def main():
    connection = None
    start = datetime.now()
    log.debug("Starting insert simulator at %s" % start)
    try:
        connection = databaseHelper.getDbConnection(config)
        cursor = connection.cursor()

        insertNonExistingJobDetailsFromSimulatedTable(cursor)

    except Exception, e:
        log.error(
            "Exception occurred while inserting job_details from job_details simulated table, closing connection.")
        connection.close()
        log.error(traceback.format_exc())
    finally:
        log.debug("Closing connection.")
        connection.close()

    stop = datetime.now()
    log.debug("Started insert simulator at %s, completed at %s, total time taken: %s" % (start, stop, stop - start))


def getLastSimulatedCreateTime(cursor):
    """
    Query the last inserted simulated row (Making sure not to pull the latest
    which may have been created manually since the last time the simulator ran.
    :param cursor:
    :return:
    """
    cursor.execute(simulators_sql.getLastJobDetailTimeSimulated)
    row = cursor.fetchone()
    return row['create_time']


def copySimulatedRows(cursor, fromTime):
    """
    Using the provided time and the current time, copy rows from the
    simulated_job_detail table into the job_detail table where the
    create_times fall between.
    :param cursor:
    :param fromTime: The
    :return:
    """
    cursor.execute(simulators_sql.insertFromSimulatorToJobDetail, fromTime)


def insertNonExistingJobDetailsFromSimulatedTable(cursor):
    """
    Look at the simulated data table
    Get the latest records create time by comparing and using the time of the last matching row
    Using that rows create time <-> current time, do an insert from the sim table
    :return:
    """

    lastSimulatedCreateTime = getLastSimulatedCreateTime(cursor)
    copySimulatedRows(cursor, lastSimulatedCreateTime)

if __name__ == "__main__":
    main()
