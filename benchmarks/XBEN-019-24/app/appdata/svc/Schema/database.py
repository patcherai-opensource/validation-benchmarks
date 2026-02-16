"""
VaultKeeper - Database Connection Model
Handles MySQL/MariaDB connectivity
"""

class Database:
    def __init__(self, host, user, password, dbname, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.dbname = dbname
        self.port = port
        self._connection = None

    def connect(self):
        """Establish database connection"""
        try:
            import pymysql
            self._connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.dbname,
                port=self.port,
                charset='utf8mb4'
            )
        except Exception as e:
            raise Exception("Could not connect to database.")

    def select(self, query, params=None):
        """Execute SELECT query"""
        if self._connection is None:
            self.connect()
        cursor = self._connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute(self, query, params=None):
        """Execute INSERT/UPDATE/DELETE query"""
        if self._connection is None:
            self.connect()
        cursor = self._connection.cursor()
        cursor.execute(query, params or ())
        self._connection.commit()
        cursor.close()

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None
