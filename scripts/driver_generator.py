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

        createDummyDrivers(cursor, fake, amount)

        print "Committing"
        connection.commit()

    finally:
        print "Closing connection"
        connection.close()


def createUser(cursor, email, firstName, lastName):
    cursor.execute(simulators_sql.createUser, (email, firstName, lastName))
    return cursor.lastrowid


def createDriver(cursor, userId, firstName, lastName, mobileNumber):
    cursor.execute(simulators_sql.createDriver, (userId, firstName, lastName, mobileNumber))
    # return cursor.lastrowid


def createDummyDrivers(cursor, fake, amount):
    for i in range(amount):
        firstName = fake.first_name()
        lastName = fake.last_name()
        userId = createUser(cursor, fake.safe_email(), firstName, lastName)
        createDriver(cursor, userId, firstName, lastName, fake.phone_number())


if __name__ == "__main__":
    main()