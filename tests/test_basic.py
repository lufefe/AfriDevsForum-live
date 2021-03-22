import unittest

import flaskblog


class TestHelloWorld(unittest.TestCase):

    def setUp(self):
        self.app = flaskblog.app.test_client()
        self.app.testing = True

    def test_status_code(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_message(self):
        response = self.app.get('/')
        message = flaskblog.wrap_html('Hello DockerCon 2018!')
        self.assertEqual(response.data, message)


if __name__ == '__main__':
    unittest.main()
