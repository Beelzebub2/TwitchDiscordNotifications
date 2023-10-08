import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestGetBotOwnerId(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_get_bot_owner_id(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a bot owner ID into the 'config' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO Config (id, bot_owner_id) VALUES (?, ?)", (1, "123456789"))
        self.conn.commit()

        # Call the get_bot_owner_id method to retrieve the bot owner ID
        result = self.sql_handler.get_bot_owner_id()

        # Check if the result is as expected
        self.assertEqual(result, "123456789")


if __name__ == '__main__':
    unittest.main()
