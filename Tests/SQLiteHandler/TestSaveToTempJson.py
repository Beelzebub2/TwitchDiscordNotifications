import json
import os
import sqlite3
import tempfile
from Functions.Sql_handler import SQLiteHandler
import unittest


class TestSaveToTempJson(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.gettempdir()
        self.conn = sqlite3.connect(':memory:')
        self.sql_handler = SQLiteHandler(conn=self.conn)

    def test_save_to_temp_json(self):
        # Data to be saved to a temporary JSON file
        data_to_save = {
            "key1": "value1",
            "key2": "value2"
        }

        # Temporary JSON file path
        temp_json_path = os.path.join(self.temp_dir, "temp_restart_data.json")

        self.sql_handler.save_to_temp_json(data_to_save)

        # Check if the temporary JSON file exists
        self.assertTrue(os.path.exists(temp_json_path))

        # Read the content of the temporary JSON file
        with open(temp_json_path, "r") as file:
            loaded_data = json.load(file)

        # Check if the loaded data matches the original data
        self.assertEqual(loaded_data, data_to_save)


if __name__ == '__main__':
    unittest.main()
