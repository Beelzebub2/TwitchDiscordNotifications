import sqlite3
from functions.Sql_handler import SQLiteHandler
import unittest


class TestGetVersion(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_get_version(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a version into the 'config' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO Config (id, version) VALUES (?, ?)", (1, "1.0.0"))
        self.conn.commit()

        # Call the get_version method to retrieve the version
        result = self.sql_handler.get_version()

        # Check if the result is as expected
        self.assertEqual(result, "1.0.0")


if __name__ == '__main__':
    unittest.main()
