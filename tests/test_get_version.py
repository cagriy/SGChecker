import json
from unittest import TestCase

from main import sgcheck_api


class TestGet_version(TestCase):
    def setUp(self):
        self.app = sgcheck_api.app.test_client()

    def test_get_version(self):
        response = json.loads(self.app.get('/api/version').data)
        self.assertEqual(response['SGCheckAPIVersion'], sgcheck_api.__version__)

