import sqlite3
from functions.Sql_handler import SQLiteHandler
import unittest


class TestGetStreamersForUser(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_get_streamers_for_user(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a test user with streamers into the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, streamer) VALUES (?, ?)",
            ('123456789', 'TwitchStreamer1,TwitchStreamer2')
        )
        self.conn.commit()

        # Call the get_streamers_for_user method to retrieve streamers for the user
        result = self.sql_handler.get_streamers_for_user('123456789')

        # Check if the result is as expected
        expected_result = ['TwitchStreamer1', 'TwitchStreamer2']
        self.assertCountEqual(result, expected_result)

    def test_get_streamers_for_user_empty(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Call the get_streamers_for_user method for a user with no streamers
        result = self.sql_handler.get_streamers_for_user('123456789')

        # Check if the result is an empty list
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
