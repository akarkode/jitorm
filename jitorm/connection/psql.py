import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseConnection:
    def __init__(self, config):
        self.conn = None
        self.config = config
        self.database_type = "postgresql"

    def connect(self):
        if self.conn is None:
            self.conn = psycopg2.connect(**self.config)
            self.conn.autocommit = False

    def commit(self):
        if self.conn:
            self.conn.commit()
        
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, query, params=None):
        cursor = None
        try:
            self.connect()
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            self.conn.commit()
        except psycopg2.DatabaseError as e:
            print(f"Database error: {e}")
            if self.conn:
                self.conn.rollback()
        finally:
            if cursor:
                cursor.close()

    def executemany(self, query, params):
        cursor = None
        try:
            self.connect()
            cursor = self.conn.cursor()
            cursor.executemany(query, params)
            self.commit()
        except psycopg2.DatabaseError as e:
            print(f"Database error: {e}")
        finally:
            if cursor:
                cursor.close()
