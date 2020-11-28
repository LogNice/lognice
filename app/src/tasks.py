import os
import json
import redis
import docker
from uuid import uuid4
from celery import Celery, Task
from settings import (
    APP_NAME,
    TOKEN_KEY,
    REDIS_HOSTNAME,
    REDIS_PORT,
    REDIS_DB,
    RABBIT_USERNAME,
    RABBIT_PASSWORD,
    RABBIT_HOSTNAME,
    RABBIT_PORT,
    SESSIONS_PATH_HOST,
    VALIDATOR_NAME,
    SOLUTION_NAME,
    EVALUATOR_CONTAINER,
    CONTAINER_INPUT_PATH
)

REDIS_URL = 'redis://%s:%d/%d' % (REDIS_HOSTNAME, REDIS_PORT, REDIS_DB)
RABBIT_URL = 'amqp://%s:%s@%s:%d' % (RABBIT_USERNAME, RABBIT_PASSWORD, RABBIT_HOSTNAME, RABBIT_PORT)
app = Celery('tasks', backend=REDIS_URL, broker=RABBIT_URL)
red = redis.Redis(host=REDIS_HOSTNAME, port=REDIS_PORT, db=REDIS_DB)
client = docker.from_env()

@app.task
def evaluate_and_save(session_id, username):
    validator_path = os.path.join(SESSIONS_PATH_HOST, session_id, VALIDATOR_NAME)
    solution_path = os.path.join(SESSIONS_PATH_HOST, session_id, '%s.py' % username)
    logs = client.containers.run(EVALUATOR_CONTAINER, volumes={
        validator_path: {
            'bind': os.path.join(CONTAINER_INPUT_PATH, VALIDATOR_NAME),
            'mode': 'ro'
        },
        solution_path: {
            'bind': os.path.join(CONTAINER_INPUT_PATH, SOLUTION_NAME),
            'mode': 'ro'
        }
    }, auto_remove=True)

    # write to database
    result = json.loads(logs)
    if result['blocker'] is None:
        red.hset('%s-%s' % (APP_NAME, session_id), username, logs)
    return result

@app.task
def summary(session_id):
    result = red.hgetall('%s-%s' % (APP_NAME, session_id))
    return {
        k.decode('utf-8'): json.loads(v.decode('utf-8'))
        for k, v in result.items()
    }

def is_username_available(session_id, username):
    tokens = red.hgetall('%s-%s-%s' % (APP_NAME, TOKEN_KEY, session_id))
    return username.encode('utf-8') not in tokens

def register_username(session_id, username):
    token = str(uuid4())
    red.hset('%s-%s-%s' % (APP_NAME, TOKEN_KEY, session_id), username, token)
    return token

def is_token_valid(session_id, username, token):
    db_token = red.hget('%s-%s-%s' % (APP_NAME, TOKEN_KEY, session_id), username)
    return token.encode('utf-8') == db_token
