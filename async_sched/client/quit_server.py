"""
module to run with the -m flag

python -m async_sched.client.quit_server

"""
import argparse
from async_sched.client.client import quit_server


__all__ = ['NAME', 'get_argparse', 'main']


NAME = 'quit_server'


def get_argparse(parent_parser=None):
    if parent_parser is None:
        parser = argparse.ArgumentParser(description='Quit the server')
    else:
        parser = parent_parser.add_parser(NAME, help='Quit the server')

    return parser


def main(host='127.0.0.1', port=8000, **kwargs):
    quit_server((host, port))


if __name__ == '__main__':
    P = get_argparse()
    P.add_argument('--host', type=str, default='127.0.0.1')
    P.add_argument('--port', type=int, default=8000)
    ARGS = P.parse_args()

    KWARGS = {n: getattr(ARGS, n) for n in dir(ARGS) if not n.startswith('_') and getattr(ARGS, n, None) is not None}
    main(**KWARGS)
