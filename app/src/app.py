import os
import io
import json
from uuid import uuid4
import matplotlib.pyplot as plt
from flask import Flask, request, send_file
from prettytable import PrettyTable
from tasks import evaluate_and_save, summary, is_username_available, register_username, is_token_valid
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
    x.add_row(['POST', '/submit/%session_id%', 'username (String), solution (File *.py), (token (String))', 'Submit and evaluate a solution to the problem.', 'task_id'])
    x.add_row(['GET', '/summary/%session_id%', 'N/A', 'Computes a summary of all scores', 'Dictionnary'])
    x.add_row(['GET', '/summary/table/%session_id%', 'N/A', 'Computes a summary of all scores in a PrettyTable', 'PrettyTable'])
    x.add_row(['GET', '/summary/graph/%session_id%', 'N/A', 'Computes a summary of all scores in a Horizontal Bar Matplotlib graph', 'PNG'])
    return '<pre>%s</pre>' % x.get_string(title='LogNice API')

@app.route('/create', methods=['POST'])
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
    os.makedirs(folder_path)
    file.save(os.path.join(folder_path, VALIDATOR_NAME))
    return get_success_response({
        'session_id': session_id
    })

@app.route('/submit/<session_id>', methods=['POST'])
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

@app.route('/summary/<session_id>', methods=['GET'])
def get_summary_raw(session_id):
    data = summary(session_id)
    return get_success_response(data if data else 'No successful submission yet!')

@app.route('/summary/table/<session_id>', methods=['GET'])
def get_summary_table(session_id):
    data = summary(session_id)
    if not data:
        return get_success_response('No successful submission yet!')

    data = sorted(data.items(), key=lambda x: x[1]['time']['value'])
    x = PrettyTable()
    x.field_names = ['Rank','Username', f"CPU Time in {data[0][1]['time']['unit']}"]
    for i, (key, value) in enumerate(data):
        username = key
        time = value['time']['value']
        x.add_row([i+1, username, time])

    return '<pre>%s</pre>' % x.get_string(title=f"{session_id} Ranking")

@app.route('/summary/graph/<session_id>', methods=['GET'])
def get_summary_graph(session_id):
    data = summary(session_id)
    if not data:
        return get_success_response('No successful submission yet!')

    data = sorted(data.items(), key=lambda x: x[1]['time']['value'], reverse=True)
    fig = plt.figure()
    players = [i[0] for i in data]
    time = [v['time']['value'] for k, v in data]
    pos = list(range(len(players)))

    plt.barh(pos, time, align='center', color='green')
    plt.yticks(pos,(players))
    for i, v in enumerate(time):
        plt.text(v, i, f"{str(v)} {data[0][1]['time']['unit']}", fontweight = 'bold', fontsize = '10')
    plt.xlim(0, time[-1]+time[0])
    plt.xlabel(f"CPU Time in {data[0][1]['time']['unit']}")
    plt.title('Ranking based on CPU time')
    bytes = io.BytesIO()
    plt.savefig(bytes, format='png')
    bytes.seek(0)

    return send_file(bytes, mimetype='image/PNG')
