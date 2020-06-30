"""
module to run with the -m flag

python -m async_sched.client.quit_server

"""
import argparse
from async_sched.client.client import quit_server
from async_sched.utils import DEFAULT_HOST, DEFAULT_PORT


__all__ = ['NAME', 'get_argparse', 'main']


NAME = 'quit_server'


def get_argparse(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, parent_parser=None):
    if parent_parser is None:
        p = argparse.ArgumentParser(description='Quit the server')
    else:
        p = parent_parser.add_parser(NAME, help='Quit the server')

    p.add_argument('--host', type=str, default='127.0.0.1')
    p.add_argument('--port', type=int, default=8000)

    return p


def main(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, **kwargs):
    quit_server((host, port))


if __name__ == '__main__':
    P = get_argparse()
    ARGS = P.parse_args()

    KWARGS = {n: getattr(ARGS, n) for n in dir(ARGS) if not n.startswith('_') and getattr(ARGS, n, None) is not None}
    main(**KWARGS)
