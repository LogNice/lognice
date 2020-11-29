import os
import json
import docker
from redis import Redis
from uuid import uuid4
from celery import Celery, Task
from flask import Flask, request
from flask_socketio import SocketIO
from prettytable import PrettyTable
from settings import (
    APP_NAME,
    TOKEN_KEY,
    SID_KEY,
    REDIS_HOSTNAME,
    REDIS_PORT,
    REDIS_DB,
    RABBIT_USERNAME,
    RABBIT_PASSWORD,
    RABBIT_HOSTNAME,
    RABBIT_PORT,
    SESSIONS_PATH,
    SESSIONS_PATH_HOST,
    VALIDATOR_NAME,
    SOLUTION_NAME,
    EVALUATOR_CONTAINER,
    CONTAINER_INPUT_PATH
)

REDIS_URL = 'redis://%s:%d/%d' % (REDIS_HOSTNAME, REDIS_PORT, REDIS_DB)
RABBIT_URL = 'amqp://%s:%s@%s:%d' % (RABBIT_USERNAME, RABBIT_PASSWORD, RABBIT_HOSTNAME, RABBIT_PORT)
flask = Flask(__name__)
socketio = SocketIO(flask, message_queue=REDIS_URL)
celery = Celery('app', backend=REDIS_URL, broker=RABBIT_URL)
redis = Redis(host=REDIS_HOSTNAME, port=REDIS_PORT, db=REDIS_DB)
client = docker.from_env()

@celery.task
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
        redis.hset('%s-%s' % (APP_NAME, session_id), username, logs)

    # notify client
    emit_task_update(session_id, username, 'task_finished', result)

    return result

@flask.route('/')
def hello_world():
    x = PrettyTable()
    x.field_names = ['Method', 'Endpoint', 'Parameters', 'Description', 'Return Value']
    x.add_row(['POST', '/create', 'validator (File *.py)', 'Creates a new session, provided a validator script for test cases.', 'session_id'])
    x.add_row(['POST', '/submit/%session_id%', 'username (String), solution (File *.py), (token (String))', 'Submit and evaluate a solution to the problem.', 'task_id'])
    x.add_row(['GET', '/summary/%session_id%', 'N/A', 'Computes a summary of all scores', 'Dictionnary'])
    return '<pre>%s</pre>' % x.get_string(title='LogNice API')

@flask.route('/create', methods=['POST'])
def create_session():
    validator_file_key = 'validator'
    if validator_file_key not in request.files:
        return get_error_response('No file provided'), 400

    file = request.files[validator_file_key]
    if file.filename == '':
        return get_error_response('No file provided'), 400

    if file.filename.split('.')[-1] != 'py':
        return get_error_response('Wrong file extension'), 400

    session_id = get_uid()
    cwd = os.getcwd()
    folder_path = os.path.join(cwd, SESSIONS_PATH, session_id)
    os.makedirs(folder_path, exist_ok=True)
    file.save(os.path.join(folder_path, VALIDATOR_NAME))
    return get_success_response({
        'session_id': session_id
    })

@flask.route('/submit/<session_id>', methods=['POST'])
def submit_solution(session_id):
    username = request.form.get('username', None)
    token = request.form.get('token', None)

    if not username:
        return get_error_response('No username provided'), 400

    if username.find(' ') != -1:
        return get_error_response('Username cannot contain spaces'), 400

    should_register = False
    if not is_username_available(session_id, username):
        if not token:
            return get_error_response('Username is not available. Please use your token if that username belongs to you.'), 403
        if not is_token_valid(session_id, username, token):
            return get_error_response('Invalid token for username.'), 403
    else:
        should_register = True

    solution_file_key = 'solution'
    if solution_file_key not in request.files:
        return get_error_response('No file provided'), 400

    file = request.files[solution_file_key]
    if file.filename == '':
        return get_error_response('No file provided'), 400

    if file.filename.split('.')[-1] != 'py':
        return get_error_response('Wrong file extension'), 400

    file.save(os.path.join(
        os.getcwd(),
        SESSIONS_PATH,
        session_id,
        '%s.py' % username
    ))

    task = evaluate_and_save.delay(session_id, username)

    response = {
        'task_id': task.task_id
    }

    if should_register:
        response['token'] = register_username(session_id, username)

    return get_success_response(response)

@flask.route('/summary/<session_id>', methods=['GET'])
def get_summary_raw(session_id):
    return get_success_response(summary(session_id))

@socketio.on('register')
def register(data):
    session_id = data.get('session_id', None)
    username = data.get('username', None)
    if session_id and username:
        sid = request.sid
        redis.hset('%s-%s-%s' % (APP_NAME, SID_KEY, session_id), username, sid)
        redis.hset('%s-%s-%s' % (APP_NAME, SID_KEY, session_id), sid, username)

@socketio.on('unregister')
def unregister(data):
    session_id = data.get('session_id', None)
    username = data.get('username', None)
    if session_id and username:
        sid = request.sid
        redis.hdel('%s-%s-%s' % (APP_NAME, SID_KEY, session_id), username)
        redis.hdel('%s-%s-%s' % (APP_NAME, SID_KEY, session_id), sid)

def get_error_response(message):
    return json.dumps({
        'status': 'error',
        'message': message
    })

def get_success_response(result):
    return json.dumps({
        'status': 'success',
        'result': result
    })

def get_uid():
    return str(uuid4())[:5]

def emit_task_update(session_id, username, key, data):
    sid = redis.hget('%s-%s-%s' % (APP_NAME, SID_KEY, session_id), username)
    if sid:
        sid = sid.decode('utf-8')
        socketio.emit(key, data, room=sid)

def summary(session_id):
    result = redis.hgetall('%s-%s' % (APP_NAME, session_id))
    return {
        k.decode('utf-8'): json.loads(v.decode('utf-8'))
        for k, v in result.items()
    }

def is_username_available(session_id, username):
    tokens = redis.hgetall('%s-%s-%s' % (APP_NAME, TOKEN_KEY, session_id))
    return username.encode('utf-8') not in tokens

def register_username(session_id, username):
    token = str(uuid4())
    redis.hset('%s-%s-%s' % (APP_NAME, TOKEN_KEY, session_id), username, token)
    return token

def is_token_valid(session_id, username, token):
    db_token = redis.hget('%s-%s-%s' % (APP_NAME, TOKEN_KEY, session_id), username)
    return token.encode('utf-8') == db_token

if __name__ == '__main__':
    socketio.run(flask, host='0.0.0.0', port=5000, debug=True)
