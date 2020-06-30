"""
module to run with the -m flag

python -m async_sched.client.run_command "print_task" "abc"

"""
import argparse
import serial_json
from async_sched.client.client import run_command


__all__ = ['NAME', 'get_argparse', 'main']


NAME = 'run_command'


def parse(value):
    try:
        return serial_json.loads(value)
    except:
        return value


def get_argparse(parent_parser=None):
    if parent_parser is None:
        p = argparse.ArgumentParser(description='Run a registered command on the server.')
    else:
        p = parent_parser.add_parser(NAME, help='Run a registered command on the server.')

    p.add_argument('callback_name', help='Registered callback name to run.')
    p.add_argument('args', nargs='*', help='Positional arguments to pass into the callback function.')
    p.add_argument('--host', type=str, default='127.0.0.1')
    p.add_argument('--port', type=int, default=8000)

    return p


def main(callback_name, args, host='127.0.0.1', port=8000, **kwargs):
    args = (parse(arg) for arg in args)
    run_command((host, port), callback_name, *args)


if __name__ == '__main__':
    P = get_argparse()
    ARGS = P.parse_args()

    KWARGS = {n: getattr(ARGS, n) for n in dir(ARGS) if not n.startswith('_') and getattr(ARGS, n, None) is not None}
    main(**KWARGS)
