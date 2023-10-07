import sqlite3
from functions.Sql_handler import SQLiteHandler
import unittest


class TestGetGuildPrefix(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_get_guild_prefix(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a guild entry with a prefix into the 'guilds' table
        guild_id = "123456789"
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO guilds (guild_id, name, prefix, role_to_add) VALUES (?, ?, ?, ?)",
                       (guild_id, "Test Guild", "!", None))
        self.conn.commit()

        # Call the get_guild_prefix method to retrieve the guild's prefix
        result = self.sql_handler.get_guild_prefix(guild_id)

        # Check if the result is as expected
        self.assertEqual(result, "!")


if __name__ == '__main__':
    unittest.main()
