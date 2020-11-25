import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

CELERY_BACKEND = os.environ.get('CELERY_BACKEND')
CELERY_BROKER = os.environ.get('CELERY_BROKER')
SESSIONS_PATH = os.environ.get('SESSIONS_PATH')
VALIDATOR_NAME = os.environ.get('VALIDATOR_NAME')
SOLUTION_NAME = os.environ.get('SOLUTION_NAME')
EVALUATOR_CONTAINER = os.environ.get('EVALUATOR_CONTAINER')
CONTAINER_INPUT_PATH = os.environ.get('CONTAINER_INPUT_PATH')
