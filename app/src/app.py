import io
import os
import json
import docker
import matplotlib.pyplot as plt
from redis import Redis
from uuid import uuid4
from celery import Celery, Task
from flask import Flask, request, send_file
from flask_socketio import SocketIO
from prettytable import PrettyTable
from settings import (
    APP_NAME,
    APP_DEBUG,
    TOKEN_KEY,
    SID_KEY,
    DESCRIPTION_KEY,
    FLASK_HOSTNAME,
    FLASK_PORT,
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
    CONTAINER_INPUT_PATH,
    EVAL_CONTAINER,
    EVAL_NETWORK
)

FLASK_URL = 'http://%s:%d' % (FLASK_HOSTNAME, FLASK_PORT)
REDIS_URL = 'redis://%s:%d/%d' % (REDIS_HOSTNAME, REDIS_PORT, REDIS_DB)
RABBIT_URL = 'amqp://%s:%s@%s:%d' % (RABBIT_USERNAME, RABBIT_PASSWORD, RABBIT_HOSTNAME, RABBIT_PORT)
flask = Flask(__name__, static_folder='/usr/src/app/view')
socketio = SocketIO(flask, message_queue=REDIS_URL, cors_allowed_origins='*')
celery = Celery('app', backend=REDIS_URL, broker=RABBIT_URL)
redis = Redis(host=REDIS_HOSTNAME, port=REDIS_PORT, db=REDIS_DB)
client = docker.from_env()

@celery.task
def evaluate_and_save(session_id, username):
    validator_path = os.path.join(SESSIONS_PATH_HOST, session_id, VALIDATOR_NAME)
    solution_path = os.path.join(SESSIONS_PATH_HOST, session_id, '%s.py' % username)
    client.containers.run(
        EVAL_CONTAINER,
        volumes={
            validator_path: {
                'bind': os.path.join(CONTAINER_INPUT_PATH, VALIDATOR_NAME),
                'mode': 'ro'
            },
            solution_path: {
                'bind': os.path.join(CONTAINER_INPUT_PATH, SOLUTION_NAME),
                'mode': 'ro'
            }
        },
        environment={
            'SESSION_ID': session_id,
            'USERNAME': username,
            'SOCKETIO_URL': FLASK_URL
        },
        network=EVAL_NETWORK,
        auto_remove=True
    )

@flask.route('/')
def home_page():
    return flask.send_static_file('home/index.html')

@flask.route('/create')
def create_page():
    return flask.send_static_file('create/index.html')

@flask.route('/submit')
def submit_page():
    return flask.send_static_file('submit/index.html')

@flask.route('/summary')
def summary_page():
    return flask.send_static_file('summary/index.html')

@flask.errorhandler(404)
def page_not_found(e):
    return flask.send_static_file('notfound/index.html')

@flask.route('/api')
def api_help():
    x = PrettyTable()
    x.field_names = ['Method', 'Endpoint', 'Parameters', 'Description', 'Return Value']
    x.add_row(['POST', '/api/create', 'validator (File *.py)', 'Creates a new session, provided a validator script for test cases.', 'session_id'])
    x.add_row(['POST', '/api/submit/%session_id%', 'username (String), solution (File *.py), (token (String))', 'Submit and evaluate a solution to the problem.', 'task_id'])
    x.add_row(['GET', '/api/description/%session_id%', 'N/A', 'Get the description of the problem.', 'description'])
    x.add_row(['GET', '/api/summary/%session_id%', 'N/A', 'Computes a summary of all scores', 'summary'])
    x.add_row(['GET', '/api/summary/table/%session_id%', 'N/A', 'Computes a summary of all scores in a formatted table', 'summary_str'])
    x.add_row(['GET', '/api/summary/graph/%session_id%', 'N/A', 'Computes a summary of all scores in a bar plot graph.', 'PNG'])
    return '<pre>%s</pre>' % x.get_string(title='LogNice API')

@flask.route('/api/create', methods=['POST'])
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

    description = request.form.get('description', None)
    if description:
        redis.set('%s-%s-%s' % (APP_NAME, DESCRIPTION_KEY, session_id), description)

    folder_path = os.path.join(os.getcwd(), SESSIONS_PATH, session_id)
    os.makedirs(folder_path, exist_ok=True)
    file.save(os.path.join(folder_path, VALIDATOR_NAME))
    return get_success_response({
        'session_id': session_id
    })

@flask.route('/api/submit/<session_id>', methods=['POST'])
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

@flask.route('/api/description/<session_id>', methods=['GET'])
def get_session_description(session_id):
    description = redis.get('%s-%s-%s' % (APP_NAME, DESCRIPTION_KEY, session_id))
    return get_success_response({
        'description': description.decode('utf-8') if description else ''
    })

@flask.route('/api/summary/<session_id>', methods=['GET'])
def get_summary_raw(session_id):
    return get_success_response({
        'summary': summary(session_id) or {}
    })

@flask.route('/api/summary/table/<session_id>', methods=['GET'])
def get_summary_table(session_id):
    data = summary(session_id)
    if not data:
        return get_success_response({'summary_str': 'No data available yet.'})

    data = sorted(data.items(), key=lambda x: x[1]['time']['value'])
    table = PrettyTable()
    table.field_names = ['Rank', 'Username', 'CPU Time in %s' % data[0][1]['time']['unit']]
    for rank, (username, value) in enumerate(data):
        table.add_row([rank + 1, username, value['time']['value']])

    return get_success_response({
        'summary_str': table.get_string(title='[%s] Ranking' % session_id)
    })

@flask.route('/api/summary/graph/<session_id>', methods=['GET'])
def get_summary_graph(session_id):
    data = summary(session_id)
    if not data:
        return get_error_response('No successful submission yet!'), 204

    data = sorted(data.items(), key=lambda x: x[1]['time']['value'], reverse=True)
    names = [i[0] for i in data]
    times = [v['time']['value'] for k, v in data]
    pos = list(range(len(names)))

    plt.barh(pos, times, align='center')
    plt.yticks(pos, names)
    for i, (_, d) in enumerate(data):
        v, u = d['time']['value'], d['time']['unit']
        plt.text(v, i, '%d %s' % (v, u), fontsize='10')
    plt.xlim(0, times[-1] + 20)
    plt.xlabel('CPU Time in %s' % data[0][1]['time']['unit'])
    plt.title('Ranking based on CPU time')

    bytes = io.BytesIO()
    plt.savefig(bytes, format='png')
    plt.close()
    bytes.seek(0)
    return send_file(bytes, mimetype='image/PNG')

@socketio.on('register')
def on_register(data):
    session_id = data.get('session_id', None)
    username = data.get('username', None)
    if session_id and username:
        sid = request.sid
        redis.hset('%s-%s-%s' % (APP_NAME, SID_KEY, session_id), username, sid)
        redis.hset('%s-%s-%s' % (APP_NAME, SID_KEY, session_id), sid, username)
        socketio.emit('register', True, room=sid)
    else:
        socketio.emit('register', False, room=sid)

@socketio.on('unregister')
def on_unregister(data):
    session_id = data.get('session_id', None)
    username = data.get('username', None)
    if session_id and username:
        sid = request.sid
        redis.hdel('%s-%s-%s' % (APP_NAME, SID_KEY, session_id), username)
        redis.hdel('%s-%s-%s' % (APP_NAME, SID_KEY, session_id), sid)

@socketio.on('evaluated')
def on_evaluated(data):
    session_id = data['session_id']
    username = data['username']
    response = data['data']

    if response['status'] == 'success':
        result = response['result']
        if result['blocker'] is None:
            redis.hset('%s-%s' % (APP_NAME, session_id), username, json.dumps(result))

    emit_task_update(session_id, username, 'task_finished', response)

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
    socketio.run(flask, host='0.0.0.0', port=5000, debug=APP_DEBUG)
