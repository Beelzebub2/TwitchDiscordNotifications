import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestRemoveGuild(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_remove_guild(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Insert a guild entry into the 'guilds' table
        guild_id = "123456789"
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO guilds (guild_id, name, prefix, role_to_add) VALUES (?, ?, ?, ?)",
                       (guild_id, "Test Guild", "!", None))
        self.conn.commit()

        # Call the remove_guild method to remove the guild
        self.sql_handler.remove_guild(guild_id)

        # Check if the guild entry was removed from the 'guilds' table
        cursor.execute(
            "SELECT guild_id FROM guilds WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()

        # Check if the result is None, indicating the guild was removed
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
