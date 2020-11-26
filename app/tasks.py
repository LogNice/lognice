import os
import json
import docker
from celery import Celery, Task
from settings import (
    APP_NAME,
    CELERY_BACKEND,
    CELERY_BROKER,
    SESSIONS_PATH,
    VALIDATOR_NAME,
    SOLUTION_NAME,
    EVALUATOR_CONTAINER,
    CONTAINER_INPUT_PATH
)

app = Celery('tasks', backend=CELERY_BACKEND, broker=CELERY_BROKER)
client = docker.from_env()

@app.task
def evaluate_and_save(session_id, solution_id, username):
    cwd = os.getcwd()
    validator_path = os.path.join(cwd, SESSIONS_PATH, session_id, VALIDATOR_NAME)
    solution_path = os.path.join(cwd, SESSIONS_PATH, session_id, '%s.py' % solution_id)
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

    # parse logs and add data
    result = json.loads(logs)
    result['username'] = username

    # write to database
    r = app.backend.redis.Redis()
    r.hset('%s-%s' % (APP_NAME, session_id), solution_id, json.dumps(result))
    return result

@app.task
def summary(session_id):
    r = app.backend.redis.Redis()
    result = r.hgetall('%s-%s' % (APP_NAME, session_id))
    return {
        k.decode('utf-8'): json.loads(v.decode('utf-8'))
        for k, v in result.items()
    }
