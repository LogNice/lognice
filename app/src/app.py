import os
import json
from uuid import uuid4
from flask import Flask, request
from prettytable import PrettyTable
from tasks import evaluate_and_save, summary
from settings import SESSIONS_PATH, VALIDATOR_NAME

app = Flask(__name__)

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

@app.route('/')
def hello_world():
    x = PrettyTable()
    x.field_names = ['Method', 'Endpoint', 'Parameters', 'Description', 'Return Value']
    x.add_row(['POST', '/create', 'validator (File *.py)', 'Creates a new session, provided a validator script for test cases.', 'session_id'])
    x.add_row(['POST', '/submit/%session_id%', 'username (String), solution (File *.py)', 'Submit and evaluate a solution to the problem.', 'task_id'])
    x.add_row(['GET', '/summary/%session_id%', 'N/A', 'Computes a summary of all scores', 'Dictionnary'])
    return '<pre>%s</pre>' % x.get_string(title='LogNice API')

@app.route('/create', methods=['POST'])
def create_session():
    validator_file_key = 'validator'
    if validator_file_key not in request.files:
        return get_error_response('No file provided')

    file = request.files[validator_file_key]
    if file.filename == '':
        return get_error_response('No file provided')

    if file.filename.split('.')[-1] != 'py':
        return get_error_response('Wrong file extension')

    session_id = get_uid()
    cwd = os.getcwd()
    folder_path = os.path.join(cwd, SESSIONS_PATH, session_id)
    os.makedirs(folder_path)
    file.save(os.path.join(folder_path, VALIDATOR_NAME))
    return get_success_response({
        'session_id': session_id
    })

@app.route('/submit/<session_id>', methods=['POST'])
def submit_solution(session_id):
    username = request.form.get('username', None)
    if not isinstance(username, str):
        return get_error_response('You must provide: username')

    solution_file_key = 'solution'
    if solution_file_key not in request.files:
        return get_error_response('No file provided')

    file = request.files[solution_file_key]
    if file.filename == '':
        return get_error_response('No file provided')

    if file.filename.split('.')[-1] != 'py':
        return get_error_response('Wrong file extension')

    solution_id = get_uid()
    cwd = os.getcwd()
    folder_path = os.path.join(cwd, SESSIONS_PATH, session_id)
    file.save(os.path.join(folder_path, '%s.py' % solution_id))
    result = evaluate_and_save.delay(session_id, solution_id, username)
    return get_success_response({
        'task_id': result.task_id
    })

@app.route('/summary/<session_id>', methods=['GET'])
def get_summary_raw(session_id):
    return get_success_response(summary(session_id))
