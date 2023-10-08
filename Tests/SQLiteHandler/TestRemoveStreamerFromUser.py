import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestRemoveStreamerFromUser(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_remove_streamer_from_user(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a test user with streamers into the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, streamer) VALUES (?, ?)",
            ('123456789', 'TwitchStreamer1,TwitchStreamer2')
        )
        self.conn.commit()

        # Call the remove_streamer_from_user method to remove a streamer
        result = self.sql_handler.remove_streamer_from_user(
            '123456789', 'TwitchStreamer2')

        # Check if the result is as expected
        self.assertTrue(result)

        # Verify that the user's streamers have been updated in the 'users' table
        cursor.execute(
            "SELECT streamer FROM users WHERE discord_id = ?", ('123456789',))
        user_streamers = cursor.fetchone()[0].split(',')
        self.assertCountEqual(user_streamers, ['TwitchStreamer1'])

    def test_remove_streamer_from_user_not_found(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a test user with streamers into the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, streamer) VALUES (?, ?)",
            ('123456789', 'TwitchStreamer1,TwitchStreamer2')
        )
        self.conn.commit()

        # Call the remove_streamer_from_user method to remove a streamer that doesn't exist
        result = self.sql_handler.remove_streamer_from_user(
            '123456789', 'TwitchStreamer3')

        # Check if the result is as expected (should be False)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
