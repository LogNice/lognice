import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.environ.get('APP_NAME')
APP_DEBUG = bool(os.environ.get('APP_DEBUG', 0))

TOKEN_KEY = os.environ.get('TOKEN_KEY')
SID_KEY = os.environ.get('SID_KEY')

REDIS_HOSTNAME = os.environ.get('REDIS_HOSTNAME')
REDIS_PORT = int(os.environ.get('REDIS_PORT'))
REDIS_DB = int(os.environ.get('REDIS_DB'))

RABBIT_HOSTNAME = os.environ.get('RABBIT_HOSTNAME')
RABBIT_USERNAME = os.environ.get('RABBIT_USERNAME')
RABBIT_PASSWORD = os.environ.get('RABBIT_PASSWORD')
RABBIT_PORT = int(os.environ.get('RABBIT_PORT'))

SESSIONS_PATH = os.environ.get('SESSIONS_PATH')
SESSIONS_PATH_HOST = os.environ.get('SESSIONS_PATH_HOST')
VALIDATOR_NAME = os.environ.get('VALIDATOR_NAME')
SOLUTION_NAME = os.environ.get('SOLUTION_NAME')
EVALUATOR_CONTAINER = os.environ.get('EVALUATOR_CONTAINER')
CONTAINER_INPUT_PATH = os.environ.get('CONTAINER_INPUT_PATH')
