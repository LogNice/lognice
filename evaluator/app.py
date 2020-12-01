import json
import timeit
from input.solution import Solution
from input.validator import Validator

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

    return report

def main():
    print(json.dumps(execute()))

if __name__ == '__main__':
    main()
