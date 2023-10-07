import sqlite3
from functions.Sql_handler import SQLiteHandler
import unittest

class TestSaveBotOwnerId(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_save_bot_owner_id(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Call the save_bot_owner_id method to save a new bot owner ID
        new_owner_id = "987654321"
        self.sql_handler.save_bot_owner_id(new_owner_id)

        # Retrieve the bot owner ID from the 'config' table
        cursor = self.conn.cursor()
        cursor.execute("SELECT bot_owner_id FROM Config WHERE id = 1")
        result = cursor.fetchone()[0]

        # Check if the retrieved bot owner ID matches the new bot owner ID
        self.assertEqual(result, new_owner_id)


if __name__ == '__main__':
    unittest.main()
