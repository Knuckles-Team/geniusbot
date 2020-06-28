import pypyodbc as pyodbc


# This class will make database calls to the UXID Dev DB
class MSSQLAPI:
    conn = None
    cursor = None
    server = None
    database = None

    def __init__(self, server, database):
        self.server = server
        self.database = database
        try:
            self.conn = pyodbc.connect('Driver={SQL Server};' +
                                       f'Server={self.server};' +
                                       f'Database={self.database};' +
                                       f'Trusted_Connection=yes;')
            self.cursor = self.conn.cursor()
        except(UnicodeError, pyodbc.DatabaseError) as e:
            print("Error Connecting to Database, ", e)

    def get_query(self, query):
        queried_list = []
        self.cursor.execute(query)
        for row in self.cursor:
            queried_list.append(str(row))
        return queried_list

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
