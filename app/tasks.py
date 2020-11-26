import os
import json
import docker
from celery import Celery
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
cwd = os.getcwd()

@app.task
def evaluate(session_id, solution_id):
    validator_path = os.path.join(cwd, SESSIONS_PATH, session_id, '%s.py' % VALIDATOR_NAME)
    solution_path = os.path.join(cwd, SESSIONS_PATH, session_id, '%s.py' % solution_id)
    logs = client.containers.run(EVALUATOR_CONTAINER, volumes={
        validator_path: {
            'bind': os.path.join(CONTAINER_INPUT_PATH, '%s.py' % VALIDATOR_NAME),
            'mode': 'ro'
        },
        solution_path: {
            'bind': os.path.join(CONTAINER_INPUT_PATH, '%s.py' % SOLUTION_NAME),
            'mode': 'ro'
        }
    }, auto_remove=True)
    result = json.loads(logs)
    result['session_id'] = session_id
    result['solution_id'] = solution_id
    return result

@app.task
def log_result(task_id, username):
    result = app.backend.get_result(task_id)
    result['username'] = username
    key = '%s-%s/%s' % (APP_NAME, result['session_id'], result['solution_id'])
    app.backend.set(key, json.dumps(result))
