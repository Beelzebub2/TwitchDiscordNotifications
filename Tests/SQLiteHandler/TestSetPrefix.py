import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestSetPrefix(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_set_prefix(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Call the set_prefix method to set a new prefix
        new_prefix = "!"
        self.sql_handler.set_prefix(new_prefix)

        # Retrieve the prefix from the 'config' table
        cursor = self.conn.cursor()
        cursor.execute("SELECT prefix FROM Config WHERE id = 1")
        result = cursor.fetchone()[0]

        # Check if the result is as expected
        self.assertEqual(result, new_prefix)


if __name__ == '__main__':
    unittest.main()
