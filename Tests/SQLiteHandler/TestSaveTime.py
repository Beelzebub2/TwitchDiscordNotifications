import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestSaveTime(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_save_time(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Call the save_time method to save a new time
        new_time = "3:00 PM"
        self.sql_handler.save_time(new_time)

        # Retrieve the time from the 'config' table
        cursor = self.conn.cursor()
        cursor.execute("SELECT time FROM Config WHERE id = 1")
        result = cursor.fetchone()[0]

        # Check if the retrieved time matches the new time
        self.assertEqual(result, new_time)


if __name__ == '__main__':
    unittest.main()
