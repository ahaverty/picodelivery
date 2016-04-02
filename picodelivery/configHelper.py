"""
Simple config helper class for getting the configuration as an object
taking from the provided file path location
@author alanhaverty@student.dit.ie
"""

import ConfigParser


def getConfig(configLocation):
    config = ConfigParser.ConfigParser()
    config.read(configLocation)
    return config
