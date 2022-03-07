import mysql.connector


connection = None


def dbQuery(preparedQuery, parameters, commit=False, fetch=True):
    try:
        cursor = connection.cursor(prepared=True)

        cursor.execute(preparedQuery, parameters)
        if commit:
            connection.commit()
        if fetch:
            return cursor.fetchall()
        else:
            return None
    except mysql.connector.Error as error:
        print("parameterized query failed {}".format(error))


