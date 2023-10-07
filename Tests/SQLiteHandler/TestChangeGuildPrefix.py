import sqlite3
from functions.Sql_handler import SQLiteHandler
import unittest


class TestChangeGuildPrefix(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_change_guild_prefix(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a guild entry with a prefix into the 'guilds' table
        guild_id = "123456789"
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO guilds (guild_id, name, prefix, role_to_add) VALUES (?, ?, ?, ?)",
                       (guild_id, "Test Guild", "!", None))
        self.conn.commit()

        # Call the change_guild_prefix method to change the guild's prefix
        new_prefix = "#"
        self.sql_handler.change_guild_prefix(guild_id, new_prefix)

        # Retrieve the updated prefix from the 'guilds' table
        cursor.execute(
            "SELECT prefix FROM guilds WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()

        # Check if the result is as expected
        self.assertEqual(result[0], new_prefix)


if __name__ == '__main__':
    unittest.main()
