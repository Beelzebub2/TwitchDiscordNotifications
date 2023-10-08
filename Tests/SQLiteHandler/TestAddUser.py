import sqlite3
from functions.Sql_handler import SQLiteHandler
import unittest


class TestAddUser(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_add_user(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Test user data
        user_data = {
            'discord_id': '123456789',
            'streamer_list': ['TwitchStreamer1'],
            'discord_username': 'User1'
        }

        # Call the add_user method to add a new user
        result = self.sql_handler.add_user(user_data)

        # Check if the result is as expected
        expected_result = True
        self.assertEqual(result, expected_result)

        # Verify that the user exists in the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE discord_id = ?", ('123456789',))
        user_row = cursor.fetchone()
        self.assertIsNotNone(user_row)

    def test_add_user_already_exists(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Test user data
        user_data = {
            'discord_id': '123456789',
            'streamer_list': ['TwitchStreamer1'],
            'discord_username': 'User1'
        }

        # Insert a user with the same discord_id into the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, streamer, username) VALUES (?, ?, ?)",
            (user_data['discord_id'], user_data['streamer_list']
             [0], user_data['discord_username'])
        )
        self.conn.commit()

        # Call the add_user method with the same discord_id
        result = self.sql_handler.add_user(user_data)

        # Check if the result is as expected
        expected_result = False
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
