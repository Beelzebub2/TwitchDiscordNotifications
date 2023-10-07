import sqlite3
from functions.Sql_handler import SQLiteHandler
import unittest


class TestGetAllStreamers(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_get_all_streamers(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert test users with streamers into the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, streamer) VALUES (?, ?)",
            ('user1_id', 'TwitchStreamer1,TwitchStreamer2')
        )
        cursor.execute(
            "INSERT INTO users (discord_id, streamer) VALUES (?, ?)",
            ('user2_id', 'TwitchStreamer2,TwitchStreamer3')
        )
        self.conn.commit()

        # Call the get_all_streamers method to retrieve all streamers
        result = self.sql_handler.get_all_streamers()

        # Check if the result is as expected
        expected_result = ['TwitchStreamer1',
                           'TwitchStreamer2', 'TwitchStreamer3']
        self.assertCountEqual(result, expected_result)

    def test_get_all_streamers_empty(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Call the get_all_streamers method when there are no streamers in the 'users' table
        result = self.sql_handler.get_all_streamers()

        # Check if the result is an empty list
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
