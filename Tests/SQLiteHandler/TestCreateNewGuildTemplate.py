import sqlite3
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestCreateNewGuildTemplate(unittest.TestCase):

    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def tearDown(self):
        # Close the database connection
        self.conn.close()

    def test_create_new_guild_template(self):
        # Call the create_tables method to create tables
        self.sql_handler.create_tables()

        # Call the create_new_guild_template method to create a new guild template
        guild_id = "123456789"
        guild_name = "Test Guild"
        self.sql_handler.create_new_guild_template(guild_id, guild_name)

        # Check if the guild template was created in the 'guilds' table
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT guild_id FROM guilds WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()

        # Check if the result is not None, indicating the guild template exists
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
