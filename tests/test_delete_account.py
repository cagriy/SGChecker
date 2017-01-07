from __future__ import print_function

import json
from unittest import TestCase

import redis

from main import sgcheck_api


class TestDelete_account(TestCase):
    def setUp(self):
        self.app = sgcheck_api.app.test_client()

        self.r = redis.StrictRedis(
            host=sgcheck_api.REDIS_HOST,
            port=6379,
            db=0)

    def test_delete_account(self):
        request = json.dumps({'key': 'testkey'})
        self.r.set('testkey', 'testsecret')
        response = self.app.post('/api/delete',
                                 data=request,
                                 headers={"content-type": "application/json"}
                                 )
        print(response.data)
        self.assertIn('200 OK', str(response))
        self.assertIsNone(self.r.get('testkey'))

    def test_delete_account_syntax_missing(self):
        request = json.dumps({'something': 'testsecret'})
        response = self.app.post('/api/delete',
                                 data=request,
                                 headers={"content-type": "application/json"}
                                 )
        print(response.data)
        response_json = json.loads(response.data)
        self.assertIn('200 OK', str(response))
        self.assertEqual(response_json['Status'], 'Failed')
        self.assertEqual(response_json['Error'], 'Invalid use. Key must be specified.')

    def test_delete_account_syntax_blank(self):
        request = json.dumps({'key': '', 'secret': ''})
        response = self.app.post('/api/delete',
                                 data=request,
                                 headers={"content-type": "application/json"}
                                 )
        print(response.data)
        response_json = json.loads(response.data)
        self.assertIn('200 OK', str(response))
        self.assertEqual(response_json['Status'], 'Failed')
        self.assertEqual(response_json['Error'], 'Invalid use. Key must have non-zero length.')

    def test_delete_account_no_key(self):
        request = json.dumps({'key': 'averyuglykey', 'secret': 'testsecret'})
        response = self.app.post('/api/delete',
                                 data=request,
                                 headers={"content-type": "application/json"}
                                 )
        print(response.data)
        response_json = json.loads(response.data)
        self.assertIn('200 OK', str(response))
        self.assertEqual(response_json['Status'], 'Failed')
        self.assertEqual(response_json['Error'], 'Key not found in key store.')
