import sqlite3
from functions.Sql_handler import SQLiteHandler
import unittest


class TestDeleteUser(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_delete_user(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a test user into the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, streamer, username) VALUES (?, ?, ?)",
            ('123456789', 'TwitchStreamer1', 'User1')
        )
        self.conn.commit()

        # Call the delete_user method to delete the user
        result = self.sql_handler.delete_user('123456789')

        # Check if the result is as expected
        self.assertTrue(result)

        # Verify that the user is deleted from the 'users' table
        cursor.execute(
            "SELECT * FROM users WHERE discord_id = ?", ('123456789',))
        user_row = cursor.fetchone()
        self.assertIsNone(user_row)

    def test_delete_user_not_found(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Call the delete_user method with a discord_id that does not exist
        result = self.sql_handler.delete_user('non_existent_id')

        # Check if the result is as expected
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
