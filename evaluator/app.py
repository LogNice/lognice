import json
from input.solution import Solution
from input.validator import Validator

def execute():
    solution = Solution()
    validator = Validator()

    passed_count = 0
    blocker = None
    for test in validator.tests():
        input = test.get('input', {})
        output = test.get('output', None)
        if solution.solve(**input) != output:
            blocker = test
            break
        passed_count += 1

    return {
        'passed': passed_count,
        'blocker': blocker
    }

def main():
    print(json.dumps(execute()))

if __name__ == '__main__':
    main()
