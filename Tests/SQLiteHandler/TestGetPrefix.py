import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestGetPrefix(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_get_prefix(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a prefix into the 'config' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO Config (id, prefix) VALUES (?, ?)", (1, "!"))
        self.conn.commit()

        # Call the get_prefix method to retrieve the prefix
        result = self.sql_handler.get_prefix()

        # Check if the result is as expected
        self.assertEqual(result, "!")


if __name__ == '__main__':
    unittest.main()
