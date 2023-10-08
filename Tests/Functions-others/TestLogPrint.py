import unittest
import os
import re
from unittest.mock import patch
from functions.others import log_print


class TestLogPrint(unittest.TestCase):
    LOG_FILE_NAME = "test_log.txt"

    def setUp(self):
        # Clear the test log file before each test
        with open(self.LOG_FILE_NAME, "w") as log_file:
            log_file.write("")

    def tearDown(self):
        # Clean up the test log file after each test
        os.remove(self.LOG_FILE_NAME)

    @patch('sys.stdout', autospec=True)
    def test_log_print(self, mock_stdout):
        # Define a test message
        test_message = "Test message with color codes: Hello, World!"

        # Call the log_print function
        log_print(test_message, self.LOG_FILE_NAME)

        # Check if the message was printed to the console
        mock_stdout.write.assert_has_calls([
            unittest.mock.call(test_message),  # First call for the message
            # Second call for the newline character
            unittest.mock.call('\n'),
        ])

        # Check if the message was written to the log file
        with open(self.LOG_FILE_NAME, "r") as log_file:
            log_contents = log_file.read()
            # Remove color codes from the log contents for comparison
            log_contents_without_colors = re.sub(
                r'\x1b\[[0-9;]*m', '', log_contents)
            self.assertIn(test_message, log_contents_without_colors)


if __name__ == '__main__':
    unittest.main()
