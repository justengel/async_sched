"""
module to run with the -m flag

python -m async_sched.client.stop_schedule "Task 1" --list_schedules 1

"""
import argparse
from async_sched.client.client import stop_schedule
from async_sched.utils import DEFAULT_HOST, DEFAULT_PORT


__all__ = ['NAME', 'get_argparse', 'main']


NAME = 'stop_schedule'


def get_argparse(list_schedules: bool = True, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, parent_parser=None):
    if parent_parser is None:
        p = argparse.ArgumentParser(description='Stop running a schedule.')
    else:
        p = parent_parser.add_parser(NAME, help='Stop running a schedule.')

    p.add_argument('name', type=str, help='Name of the schedule you want to stop.')
    p.add_argument('--list_schedules', '-l', type=bool, default=list_schedules,
                   help='If True print the running schedules')

    p.add_argument('--host', type=str, default=host)
    p.add_argument('--port', type=int, default=port)

    return p


def main(list_schedules: bool = True, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, **kwargs):
    stop_schedule((host, port), list_schedules=list_schedules)


if __name__ == '__main__':
    P = get_argparse()
    ARGS = P.parse_args()

    KWARGS = {n: getattr(ARGS, n) for n in dir(ARGS) if not n.startswith('_') and getattr(ARGS, n, None) is not None}
    main(**KWARGS)
