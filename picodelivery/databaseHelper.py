"""
Simple database helper class for returning a database connection,
taking the congfiguration from the provided config file path
@author alanhaverty@student.dit.ie
"""

import pymysql


def getDbConnection(config):
    connection = pymysql.connect(host=config.get('database', 'host'),
                                 user=config.get('database', 'user'),
                                 passwd=config.get('database', 'password'),
                                 db=config.get('database', 'db'),
                                 charset='utf8',
                                 cursorclass=pymysql.cursors.DictCursor)

    return connection
