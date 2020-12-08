import os
import json
import timeit
import socketio
from input.solution import Solution
from input.validator import Validator

def notify(data):
    sio = socketio.Client()

    def on_done():
        sio.disconnect()
        sio.close()

    @sio.event
    def connect():
        sio.emit('evaluated', {
            'session_id': os.environ.get('SESSION_ID'),
            'username': os.environ.get('USERNAME'),
            'result': data
        }, callback=on_done)

    sio.connect(os.environ.get('SOCKETIO_URL'))
    sio.wait()

def execute():
    solution = Solution()
    validator = Validator()

    passed_count = 0
    blocker = None

    def to_measure():
        nonlocal passed_count
        nonlocal blocker

        passed_count = 0
        for test in validator.tests():
            input = test.get('input', {})
            output = test.get('output', None)
            answer = solution.solve(**input)
            if answer != output:
                blocker = test
                blocker['output'] = answer
                blocker['expected'] = output
                break
            passed_count += 1

    iteration = 100
    time = timeit.timeit(to_measure, number=iteration) / iteration

    report = {
        'passed': passed_count,
        'blocker': blocker
    }

    if not blocker:
        report['time'] = {
            'value': int(time * 1000000),
            'unit': 'us'
        }

    notify(report)

if __name__ == '__main__':
    execute()
