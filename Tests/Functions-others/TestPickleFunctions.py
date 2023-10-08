import unittest
import os
import pickle

# Import the functions to be tested
# Replace 'your_module' with the actual module name
from functions.others import pickle_variable, unpickle_variable


class TestPickleFunctions(unittest.TestCase):

    def setUp(self):
        # Create a temporary test file
        self.test_filename = "test_variables.pkl"

    def tearDown(self):
        # Remove the temporary test file
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_pickle_and_unpickle(self):
        # Test data
        test_data = [1, 2, 3, 4, 5]

        # Pickle the data to the test file
        pickle_variable(test_data, self.test_filename)

        # Unpickle the data from the test file
        loaded_data = unpickle_variable(self.test_filename)

        # Check if the loaded data is equal to the original data
        self.assertEqual(test_data, loaded_data)

    def test_default_filenames(self):
        # Pickle and unpickle with default filenames
        test_data = [1, 2, 3, 4, 5]

        # Pickle the data with the default filename
        pickle_variable(test_data)

        # Unpickle the data with the default filename
        loaded_data = unpickle_variable()

        # Check if the loaded data is equal to the original data
        self.assertEqual(test_data, loaded_data)


if __name__ == '__main__':
    unittest.main()
