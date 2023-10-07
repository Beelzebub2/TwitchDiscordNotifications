import unittest
import os
from unittest.mock import patch
from functions.others import clear_console


class TestClearConsole(unittest.TestCase):
    @patch('os.system')
    def test_clear_console_windows(self, mock_system):
        os.name = 'nt'

        clear_console()

        expected_command = 'cls'
        mock_system.assert_called_once_with(expected_command)

    @patch('os.system')
    def test_clear_console_linux(self, mock_system):
        os.name = 'posix'

        clear_console()

        expected_command = 'clear'
        mock_system.assert_called_once_with(expected_command)


if __name__ == '__main__':
    unittest.main()
