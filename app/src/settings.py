import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.environ.get('APP_NAME')
APP_DEBUG = bool(os.environ.get('APP_DEBUG', 0))

FLASK_HOSTNAME = os.environ.get('FLASK_HOSTNAME')
FLASK_PORT = int(os.environ.get('FLASK_PORT'))

REDIS_HOSTNAME = os.environ.get('REDIS_HOSTNAME')
REDIS_PORT = int(os.environ.get('REDIS_PORT'))
REDIS_DB = int(os.environ.get('REDIS_DB'))

RABBIT_HOSTNAME = os.environ.get('RABBIT_HOSTNAME')
RABBIT_USERNAME = os.environ.get('RABBIT_USERNAME')
RABBIT_PASSWORD = os.environ.get('RABBIT_PASSWORD')
RABBIT_PORT = int(os.environ.get('RABBIT_PORT'))

TOKEN_KEY = os.environ.get('TOKEN_KEY')
SID_KEY = os.environ.get('SID_KEY')
SESSIONS_PATH = os.environ.get('SESSIONS_PATH')
SESSIONS_PATH_HOST = os.environ.get('SESSIONS_PATH_HOST')
VALIDATOR_NAME = os.environ.get('VALIDATOR_NAME')
SOLUTION_NAME = os.environ.get('SOLUTION_NAME')
CONTAINER_INPUT_PATH = os.environ.get('CONTAINER_INPUT_PATH')

EVAL_CONTAINER = os.environ.get('EVAL_CONTAINER')
EVAL_NETWORK = os.environ.get('EVAL_NETWORK')
