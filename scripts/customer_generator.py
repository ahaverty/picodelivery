"""
Script to generate fake customers using Faker factory
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
        amount = 500
        # Define a center point, where customers addresses are later bound around a radius
        centerLat=53.342034
        centerLng=-6.271479

        createDummyCustomers(cursor, fake, amount, centerLat, centerLng)

        print "Committing"
        connection.commit()

    finally:
        print "Closing connection"
        connection.close()


def createCustomer(cursor, firstName, lastName, addressId, mobileNumber):
    """
    Insert the customers details to the database
    :param cursor:
    :param firstName:
    :param lastName:
    :param addressId:
    :param mobileNumber:
    :return:
    """
    cursor.execute(simulators_sql.createCustomer, (firstName, lastName, addressId, mobileNumber))
    return cursor.lastrowid


def createAddress(cursor, street, lat, lng):
    """
    Insert the address details to the database and return the inserted row id
    :param cursor:
    :param street:
    :param lat:
    :param lng:
    :return:
    """
    mapPoint = "POINT(%s %s)" % (lng, lat)
    cursor.execute(simulators_sql.createAddress, (street, mapPoint))
    return cursor.lastrowid


def createDummyCustomers(cursor, fake, amount, centerLat, centerLng):
    """
    Loop creating fake customer details and addresses.
    :param cursor:
    :param fake:
    :param amount:
    :param centerLat:
    :param centerLng:
    :return:
    """
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