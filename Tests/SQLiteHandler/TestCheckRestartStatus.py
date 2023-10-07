import json
import os
import sqlite3
import tempfile
from functions.Sql_handler import SQLiteHandler
import unittest


class TestCheckRestartStatus(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.gettempdir()
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def test_check_restart_status_file_exists(self):
        temp_json_path = os.path.join(self.temp_dir, "temp_restart_data.json")

        # Data to be written to the temporary JSON file
        data_to_write = {
            "Restarted": True,
            "Streamers": ["Streamer1", "Streamer2"]
        }

        # Write the data to the temporary JSON file
        with open(temp_json_path, "w") as file:
            json.dump(data_to_write, file)

        # Call the check_restart_status method
        restarted = self.sql_handler.check_restart_status()

        # Check if the function returns True indicating a restart
        self.assertTrue(restarted)

        # Check if the data in the file was updated
        with open(temp_json_path, "r") as file:
            updated_data = json.load(file)

        # Check if the "Restarted" key is now False
        self.assertFalse(updated_data.get("Restarted", False))

    def test_check_restart_status_file_not_exists(self):
        os.remove(os.path.join(self.temp_dir, "temp_restart_data.json"))
        restarted = self.sql_handler.check_restart_status()

        # Check if the function returns False for a non-existent file
        self.assertFalse(restarted)


if __name__ == '__main__':
    unittest.main()
