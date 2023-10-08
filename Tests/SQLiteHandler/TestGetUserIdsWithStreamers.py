import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestGetUserIdsWithStreamers(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_get_user_ids_with_streamers(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert test users with streamers into the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, streamer) VALUES (?, ?)",
            ('user1_id', "TwitchStreamer1,TwitchStreamer2")
        )
        cursor.execute(
            "INSERT INTO users (discord_id, streamer) VALUES (?, ?)",
            ('user2_id', 'TwitchStreamer2,TwitchStreamer3')
        )
        self.conn.commit()

        # Call the get_user_ids_with_streamers method to retrieve user IDs with their associated streamers
        result = self.sql_handler.get_user_ids_with_streamers()

        # Check if the result is as expected
        expected_result = {
            'user1_id': ["TwitchStreamer1", "TwitchStreamer2"],
            'user2_id': ["TwitchStreamer2", "TwitchStreamer3"]
        }
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
