import mysql.connector

from client import MyClient

connection = mysql.connector.connect(
    host=MyClient.config["mysql-hostname"],
    database=MyClient.config["mysql-database"],
    user=MyClient.config["mysql-user"],
    password=MyClient.config["mysql-password"]
)


def dbQuery(preparedQuery, parameters):
    try:
        cursor = connection.cursor(prepared=True)

        cursor.execute(preparedQuery, parameters)
        connection.commit()
        return cursor.fetchall()
    except mysql.connector.Error as error:
        print("parameterized query failed {}".format(error))


