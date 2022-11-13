import unittest
from api_tests import HandleRequests

class ResquestTestCase(unittest.TestCase):

    def setUp(self):
        self.handle_requests = HandleRequests('admin', 'admin')

    def test_login(self):
        print('Login')
        result = self.handle_requests.login()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()