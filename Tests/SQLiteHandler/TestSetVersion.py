import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestSetVersion(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_set_version(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Call the set_version method to set a new version
        new_version = "1.0.0"
        self.sql_handler.set_version(new_version)

        # Retrieve the version from the 'config' table
        cursor = self.conn.cursor()
        cursor.execute("SELECT version FROM Config WHERE id = 1")
        result = cursor.fetchone()[0]

        # Check if the result is as expected
        self.assertEqual(result, new_version)


if __name__ == '__main__':
    unittest.main()
