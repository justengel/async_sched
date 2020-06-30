"""
module to run with the -m flag

python -m async_sched.client.update_server --list_schedules 1

"""
import argparse
from async_sched.client.client import update_server


__all__ = ['NAME', 'get_argparse', 'main']


NAME = 'update_server'


def get_argparse(list_schedules=True, parent_parser=None):
    if parent_parser is None:
        parser = argparse.ArgumentParser(description='Update the server command modules.')
    else:
        parser = parent_parser.add_parser(NAME, help='Update the server command modules.')

    parser.add_argument('--list_schedules', '-l', type=bool, default=list_schedules,
                        help='If True print the running schedules')
    return parser


def main(list_schedules=True, host='127.0.0.1', port=8000, **kwargs):
    update_server((host, port), list_schedules=list_schedules)


if __name__ == '__main__':
    P = get_argparse()
    P.add_argument('--host', type=str, default='127.0.0.1')
    P.add_argument('--port', type=int, default=8000)
    ARGS = P.parse_args()

    KWARGS = {n: getattr(ARGS, n) for n in dir(ARGS) if not n.startswith('_') and getattr(ARGS, n, None) is not None}
    main(**KWARGS)
