"""
module to run with the -m flag

python -m async_sched.client.request_schedules

"""
import argparse
from async_sched.client.client import request_schedules


__all__ = ['NAME', 'get_argparse', 'main']


NAME = 'request_schedules'


def get_argparse(parent_parser=None):
    if parent_parser is None:
        p = argparse.ArgumentParser(description='Request and list the running schedules')
    else:
        p = parent_parser.add_parser(NAME, help='Request and list the running schedules')

    p.add_argument('--host', type=str, default='127.0.0.1')
    p.add_argument('--port', type=int, default=8000)

    return p


def main(host='127.0.0.1', port=8000, **kwargs):
    request_schedules((host, port))


if __name__ == '__main__':
    P = get_argparse()
    ARGS = P.parse_args()

    KWARGS = {n: getattr(ARGS, n) for n in dir(ARGS) if not n.startswith('_') and getattr(ARGS, n, None) is not None}
    main(**KWARGS)
