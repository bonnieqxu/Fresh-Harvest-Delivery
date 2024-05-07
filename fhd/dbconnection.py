import fhd.connect as connect
import mysql.connector

# For database connection
dbconn = None
connection = None


def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser,
                                         password=connect.dbpass, host=connect.dbhost,
                                         database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


# depot names
def query_depot_names():
    cursor = getCursor()
    cursor.execute("SELECT location_name FROM depot")
    depot_names = [row[0] for row in cursor.fetchall()]

    cursor.close()
    return depot_names