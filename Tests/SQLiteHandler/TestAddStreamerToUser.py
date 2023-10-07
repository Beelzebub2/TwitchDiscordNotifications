import sqlite3
from functions.Sql_handler import SQLiteHandler
import unittest


class TestAddStreamerToUser(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_add_streamer_to_user(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a test user into the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, streamer) VALUES (?, ?)",
            ('123456789', 'TwitchStreamer1')
        )
        self.conn.commit()

        # Call the add_streamer_to_user method to add a new streamer to the user
        result = self.sql_handler.add_streamer_to_user(
            '123456789', 'TwitchStreamer2')

        # Check if the result is as expected
        self.assertTrue(result)

        # Verify that the user's streamers have been updated in the 'users' table
        cursor.execute(
            "SELECT streamer FROM users WHERE discord_id = ?", ('123456789',))
        user_streamers = cursor.fetchone()[0].split(',')
        self.assertCountEqual(
            user_streamers, ['TwitchStreamer1', 'TwitchStreamer2'])

    def test_add_streamer_to_user_existing_streamers(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a test user with existing streamers into the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, streamer) VALUES (?, ?)",
            ('123456789', 'TwitchStreamer1,TwitchStreamer2')
        )
        self.conn.commit()

        # Call the add_streamer_to_user method to add a new streamer to the user
        result = self.sql_handler.add_streamer_to_user(
            '123456789', 'TwitchStreamer3')

        # Check if the result is as expected
        self.assertTrue(result)

        # Verify that the user's streamers have been updated in the 'users' table
        cursor.execute(
            "SELECT streamer FROM users WHERE discord_id = ?", ('123456789',))
        user_streamers = cursor.fetchone()[0].split(',')
        self.assertCountEqual(
            user_streamers, ['TwitchStreamer1', 'TwitchStreamer2', 'TwitchStreamer3'])

    def test_add_streamer_to_user_duplicate_streamer(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a test user with existing streamers into the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, streamer) VALUES (?, ?)",
            ('123456789', 'TwitchStreamer1,TwitchStreamer2')
        )
        self.conn.commit()

        # Call the add_streamer_to_user method to add a duplicate streamer to the user
        result = self.sql_handler.add_streamer_to_user(
            '123456789', 'TwitchStreamer1')

        # Check if the result is as expected
        self.assertTrue(result)

        # Verify that the user's streamers have not been duplicated in the 'users' table
        cursor.execute(
            "SELECT streamer FROM users WHERE discord_id = ?", ('123456789',))
        user_streamers = cursor.fetchone()[0].split(',')
        self.assertCountEqual(
            user_streamers, ['TwitchStreamer1', 'TwitchStreamer2'])


if __name__ == '__main__':
    unittest.main()
