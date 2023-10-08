import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestGetInfoByDiscordId(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_get_info_by_discord_id(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert test data into the 'users' table
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, streamer, username) VALUES (?, ?, ?)",
            ('123456789', 'TwitchStreamer1', 'User1')
        )
        self.conn.commit()

        # Call the get_info_by_discord_id method to retrieve data
        result = self.sql_handler.get_info_by_discord_id('123456789')

        # Check if the result is as expected
        expected_result = [(1, '123456789', 'TwitchStreamer1', 'User1')]
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
