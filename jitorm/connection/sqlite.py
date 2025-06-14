import sqlite3

class DatabaseConnection:
    def __init__(self, config):
        self.conn = None
        self.config = config
        self.database_type = "sqlite"

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.config["database"])
            self.conn.row_factory = sqlite3.Row

    def commit(self):
        if self.conn:
            self.conn.commit()
        
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, query, params=None):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
            self.conn.rollback()
        finally:
            cursor.close()

    def executemany(self, query, params):
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.executemany(query, params)
            self.commit()
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")
        finally:
            self.close()
