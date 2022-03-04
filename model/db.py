import mysql.connector


connection = None


def dbQuery(preparedQuery, parameters):
    try:
        cursor = connection.cursor(prepared=True)

        cursor.execute(preparedQuery, parameters)
        #connection.commit()
        return cursor.fetchall()
    except mysql.connector.Error as error:
        print("parameterized query failed {}".format(error))


