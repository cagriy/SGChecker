from __future__ import print_function

import json
from unittest import TestCase

import jsonpickle
import redis

from main import sgcheck_api


class TestAdd_account(TestCase):
    def setUp(self):
        self.app = sgcheck_api.app.test_client()

        self.r = redis.StrictRedis(
            host=sgcheck_api.REDIS_HOST,
            port=6379,
            db=0)

    def test_add_account(self):
        request = json.dumps({'key': 'testkey', 'secret': 'testsecret'})
        response = self.app.post('/api/add',
                                 data=request,
                                 headers={"content-type": "application/json"}
                                 )
        print (response.data)
        frozen = self.r.get('testkey')
        dummy_account = jsonpickle.decode(frozen)
        self.assertIn('200 OK', str(response))
        self.assertEqual(dummy_account.secret, 'testsecret')
        self.assertIsNotNone(dummy_account.created)
        self.assertFalse(dummy_account.setup)

        self.r.delete('testkey')

    def test_add_account_syntax_missing(self):
        request = json.dumps({'secret': 'testsecret'})
        response = self.app.post('/api/add',
                                 data=request,
                                 headers={"content-type": "application/json"}
                                 )
        print(response.data)
        response_json = json.loads(response.data)
        self.assertIn('200 OK', str(response))
        self.assertEqual(response_json['Status'], 'Failed')
        self.assertEqual(response_json['Error'], 'Invalid use. Both key and secret must be specified.')

    def test_add_account_syntax_blank(self):
        request = json.dumps({'key': '', 'secret': 'testsecret'})
        response = self.app.post('/api/add',
                                 data=request,
                                 headers={"content-type": "application/json"}
                                 )
        print(response.data)
        response_json = json.loads(response.data)
        self.assertIn('200 OK', str(response))
        self.assertEqual(response_json['Status'], 'Failed')
        self.assertEqual(response_json['Error'], 'Invalid use. Both key and secret must have non-zero length.')

