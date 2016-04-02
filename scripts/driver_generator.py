"""
Script to generate fake drivers using faker factory
@author alanhaverty@student.dit.ie
"""

from faker import Factory
from configuration import simulators_sql
from picodelivery import configHelper, databaseHelper

config = configHelper.getConfig("../project_config.ini")


def main():
    connection = None
    try:
        fake = Factory.create('en_GB')
        connection = databaseHelper.getDbConnection(config)
        cursor = connection.cursor()
        amount = 300
        # The amount of fake drivers to create

        createDummyDrivers(cursor, fake, amount)

        print "Committing"
        connection.commit()

    finally:
        print "Closing connection"
        connection.close()


def createUser(cursor, email, firstName, lastName):
    """
    Add the user to the database and return the inserted id
    :param cursor:
    :param email:
    :param firstName:
    :param lastName:
    :return:
    """
    cursor.execute(simulators_sql.createUser, (email, firstName, lastName))
    return cursor.lastrowid


def createDriver(cursor, userId, firstName, lastName, mobileNumber):
    """
    Add the driver to the db
    :param cursor:
    :param userId:
    :param firstName:
    :param lastName:
    :param mobileNumber:
    :return:
    """
    cursor.execute(simulators_sql.createDriver, (userId, firstName, lastName, mobileNumber))
    # return cursor.lastrowid


def createDummyDrivers(cursor, fake, amount):
    """
    Loop on creating dummy drivers with user rows attached
    :param cursor:
    :param fake:
    :param amount:
    :return:
    """
    for i in range(amount):
        firstName = fake.first_name()
        lastName = fake.last_name()
        userId = createUser(cursor, fake.safe_email(), firstName, lastName)
        createDriver(cursor, userId, firstName, lastName, fake.phone_number())


if __name__ == "__main__":
    main()