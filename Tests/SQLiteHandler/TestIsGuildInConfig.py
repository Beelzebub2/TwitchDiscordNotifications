import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestIsGuildInConfig(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_is_guild_in_config(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a guild entry into the 'guilds' table
        guild_id = "123456789"
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO guilds (guild_id, name, prefix, role_to_add) VALUES (?, ?, ?, ?)",
                       (guild_id, "Test Guild", ",", None))
        self.conn.commit()

        # Call the is_guild_in_config method to check if the guild exists
        result = self.sql_handler.is_guild_in_config(guild_id)

        # Check if the result is True, indicating the guild exists
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
