import os
import json
import docker
from celery import Celery
from settings import (
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
    result = client.containers.run(EVALUATOR_CONTAINER, volumes={
        validator_path: {
            'bind': os.path.join(CONTAINER_INPUT_PATH, '%s.py' % VALIDATOR_NAME),
            'mode': 'ro'
        },
        solution_path: {
            'bind': os.path.join(CONTAINER_INPUT_PATH, '%s.py' % SOLUTION_NAME),
            'mode': 'ro'
        }
    }, auto_remove=True)
    return json.loads(result)
