from __future__ import print_function
from datetime import datetime
from flask import Flask, request, jsonify

from version import __version__

import json
import jsonpickle
import redis
import os

app = Flask(__name__)

REDIS_HOST = os.environ['REDIS_HOST']

print("Version : " + __version__)
print("Redis Host : " + REDIS_HOST)


class AWSAccount:
    def __init__(self, key):
        self.key = key


@app.route('/api/version')
def get_version():
    version = {'SGCheckAPIVersion': __version__}
    return jsonify(**version)


@app.route('/api/add', methods=['GET', 'POST'])
def add_account():
    content = request.get_json(silent=True)
    r = redis.StrictRedis(
        host=REDIS_HOST,
        port=6379,
        db=0)
    error_message = ''
    if 'key' not in content or 'secret' not in content:
        error_message = 'Invalid use. Both key and secret must be specified.'
    elif content['key'] == '' or content['secret'] == '':
        error_message = 'Invalid use. Both key and secret must have non-zero length.'
    if error_message != '':
        return json.dumps({'Status': 'Failed', 'Error': error_message})

    aws_account = AWSAccount(content['key'])
    aws_account.secret = content['secret']
    aws_account.setup = False
    aws_account.created = datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")
    result = r.set(content['key'], jsonpickle.encode(aws_account))
    if result:
        return json.dumps({'Status': 'Ok'})
    else:
        return json.dumps({'Status': 'Failed', 'Error': 'Redis error.'})


@app.route('/api/delete', methods=['GET', 'POST'])
def delete_account():
    content = request.get_json(silent=True)
    r = redis.StrictRedis(
        host=REDIS_HOST,
        port=6379,
        db=0)

    error_message = ''
    if 'key' not in content:
        error_message = 'Invalid use. Key must be specified.'
    elif content['key'] == '':
        error_message = 'Invalid use. Key must have non-zero length.'
    if error_message != '':
        return json.dumps({'Status': 'Failed', 'Error': error_message})
    if r.get(content['key']) is None:
        return json.dumps({'Status': 'Failed', 'Error': 'Key not found in key store.'})
    else:
        result = r.delete(content['key'])

    if result:
        return json.dumps({'Status': 'Ok'})
    else:
        return json.dumps({'Status': 'Failed', 'Error': 'Redis error.'})


if __name__ == '__main__':
    app.run(
        port=5000
    )

