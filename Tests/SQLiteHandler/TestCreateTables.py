import sqlite3
from functions.Sql_handler import SQLiteHandler
import unittest


class TestCreateTables(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_create_tables(self):
        # Call the create_tables method
        self.sql_handler.create_tables()

        # Check if the 'users' table exists
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        result = cursor.fetchone()
        self.assertIsNotNone(result)

        # Check if the 'guilds' table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='guilds';")
        result = cursor.fetchone()
        self.assertIsNotNone(result)

        # Check if the 'config' table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='config';")
        result = cursor.fetchone()
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
