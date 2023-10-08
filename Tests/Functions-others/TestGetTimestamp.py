import datetime
import unittest
import re
from unittest.mock import patch
from Functions.others import get_timestamp


class TestGetTimestamp(unittest.TestCase):
    @patch('Functions.others.datetime')
    def test_get_timestamp(self, mock_datetime):
        mock_datetime.datetime.now.return_value = datetime.datetime(
            2023, 10, 10, 12, 30, 45)

        expected_result = "[2023-10-10 12:30:45]"
        actual_result = get_timestamp()

        actual_result = re.sub(r'\x1b\[\d+m', '', actual_result)

        self.assertEqual(actual_result, expected_result)


if __name__ == '__main__':
    unittest.main()
