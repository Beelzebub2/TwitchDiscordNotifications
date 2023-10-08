import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestGetTime(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_get_time(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a time into the 'config' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO Config (id, time) VALUES (?, ?)", (1, "12:00 PM"))
        self.conn.commit()

        # Call the get_time method to retrieve the time
        result = self.sql_handler.get_time()

        # Check if the result is as expected
        self.assertEqual(result, "12:00 PM")


if __name__ == '__main__':
    unittest.main()
