
"""
Validate a path in a dictionary object.
"""
def validate_path(path: str, obj: dict) -> bool:
    keys = path.split('.')
    current_obj = obj
    for key in keys:
        if key.isdigit():
            key = int(key)
            if isinstance(current_obj, list) and 0 <= key < len(current_obj):
                current_obj = current_obj[key]
            else:
                return False
        elif isinstance(current_obj, dict) and key in current_obj:
            current_obj = current_obj[key]
        else:
            return False
    return True


if __name__ == '__main__':
    from colors import Fore

    obj = {
        'a': {
            'b': {
                'c': 1,
                'test': [1, 2, 3]
            }
        }
    }

    tests = {
        'a.b.c': True,
        'a.b.test': True,
        'a.b.test.-1': False,
        'a.b.test.0': True,
        'a.b.test.1': True,
        'a.b.test.2': True,
        'a.b.test.3': False,
        'a.b.test.0.1': False,
        'a.b.test.0.1.2': False,
        'a.b.test.': False,
    }

    for path, expected in tests.items():
        TAG = f'[{Fore.GREEN}PASS{Fore.RESET}]' if validate_path(path, obj) == expected else f'[{Fore.RED}FAIL{Fore.RESET}]'
        print(f"{TAG} path: '{path}', expected: '{expected}', got: '{validate_path(path, obj)}'")