import unittest
import datetime
from Functions.others import generate_timestamp_string


class TestGenerateTimestampString(unittest.TestCase):
    def test_generate_timestamp_string(self):
        input_datetime_string = "2023-10-10T12:30:45Z"
        expected_output = "<t:1696941045:T>"

        result = generate_timestamp_string(input_datetime_string)

        self.assertEqual(result, expected_output)


if __name__ == '__main__':
    unittest.main()
