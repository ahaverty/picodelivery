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
        amount = 500
        centerLat=53.342034
        centerLng=-6.271479

        createDummyCustomers(cursor, fake, amount, centerLat, centerLng)

        print "Committing"
        connection.commit()

    finally:
        print "Closing connection"
        connection.close()


def createCustomer(cursor, firstName, lastName, addressId, mobileNumber):
    cursor.execute(simulators_sql.createCustomer, (firstName, lastName, addressId, mobileNumber))
    return cursor.lastrowid


def createAddress(cursor, street, lat, lng):
    mapPoint = "POINT(%s %s)" % (lng, lat)
    cursor.execute(simulators_sql.createAddress, (street, mapPoint))
    return cursor.lastrowid


def createDummyCustomers(cursor, fake, amount, centerLat, centerLng):
    for i in range(amount):
        firstName = fake.first_name()
        lastName = fake.last_name()
        latitude=str(fake.geo_coordinate(center=centerLat, radius=0.02))
        longitude=str(fake.geo_coordinate(center=centerLng, radius=0.03))
        address=fake.street_address()
        addressId = createAddress(cursor, address, latitude, longitude)
        createCustomer(cursor, firstName, lastName, addressId, fake.phone_number())


if __name__ == "__main__":
    main()