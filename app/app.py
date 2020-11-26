import os
import json
import base64
from uuid import uuid4
from flask import Flask, request
from prettytable import PrettyTable
from tasks import evaluate, log_result, summary
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

@app.route('/')
def hello_world():
    x = PrettyTable()
    x.field_names = ['Method', 'Endpoint', 'Parameters', 'Description', 'Return Value']
    x.add_row(['POST', '/create', 'validator <File(.py)>', 'Creates a new session, provided a validator script for test cases.', 'session_id'])
    return x.get_html_string()

# @app.route('/test')
# def test_image():
#     img = open('test.png', 'rb').read()
#     b64 = base64.b64encode(img).decode('utf-8')
#     return '<img src="data:image/png;base64, %s"></img>' % b64

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

    session_id = str(uuid4())
    cwd = os.getcwd()
    folder_path = os.path.join(cwd, SESSIONS_PATH, session_id)
    os.makedirs(folder_path)
    file.save(os.path.join(folder_path, VALIDATOR_NAME))
    return get_success_response({
        'session_id': session_id
    })

@app.route('/submit/<session_id>', methods=['POST'])
def submit_solution(session_id):
    solution_file_key = 'solution'
    if solution_file_key not in request.files:
        return get_error_response('No file provided')

    file = request.files[solution_file_key]
    if file.filename == '':
        return get_error_response('No file provided')

    if file.filename.split('.')[-1] != 'py':
        return get_error_response('Wrong file extension')

    solution_id = str(uuid4())
    cwd = os.getcwd()
    folder_path = os.path.join(cwd, SESSIONS_PATH, session_id)
    file.save(os.path.join(folder_path, f"{solution_id}.py"))
    res = evaluate.delay(session_id, solution_id)
    return get_success_response({
        'task_id': res.task_id
    })


@app.route('/save', methods=['POST'])
def save_task_result():
    if not request.data:
        return get_error_response('No task json provided')

    body = request.get_json()
    for key in ['task_id', "username"]:
        if not body.get(key) or not isinstance(body.get(key), str):
            return get_error_response('Incorrect json')

    log_result(body["task_id"], body["username"])
    return get_success_response("Task result saved in redis.")

@app.route('/summary/<session_id>', methods=['GET'])
def get_summary(session_id):
    return get_success_response({
        'session_summary': summary(session_id)
    })
