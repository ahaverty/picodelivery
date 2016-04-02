"""
Logger helper class used throughout the project
@author alanhaverty@student.dit.ie
"""

import logging
import os
import time
import datetime
st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M')


def setupCustomLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    directory = "logs"

    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # create a file handler
    handler = logging.FileHandler('logs/' + name + '_' + st + '.log')
    handler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
    return logger

