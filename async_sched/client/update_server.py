"""
module to run with the -m flag

python -m async_sched.client.update_server --list_schedules 1

"""
import argparse
from async_sched.client.client import update_server
from async_sched.utils import DEFAULT_HOST, DEFAULT_PORT


__all__ = ['NAME', 'get_argparse', 'main']


NAME = 'update_server'


def get_argparse(module_name: str = '', list_schedules: bool = True,
                 host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, parent_parser=None):
    if parent_parser is None:
        p = argparse.ArgumentParser(description='Update the server command modules.')
    else:
        p = parent_parser.add_parser(NAME, help='Update the server command modules.')

    p.add_argument('name', type=str, default='', nargs='?',
                   help='Name of the module to import or reload. If None import/reload all.')
    p.add_argument('--module_name', type=str, default=module_name,
                   help='Name of the module to import or reload. If None import/reload all.')
    p.add_argument('--list_schedules', '-l', type=bool, default=list_schedules,
                   help='If True print the running schedules')

    p.add_argument('--host', type=str, default=host)
    p.add_argument('--port', type=int, default=port)

    return p


def main(name: str = '', module_name: str = '', list_schedules: bool = True,
         host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, **kwargs):
    if name:
        module_name = name
    update_server((host, port), module_name=module_name, list_schedules=list_schedules)


if __name__ == '__main__':
    P = get_argparse()
    ARGS = P.parse_args()

    KWARGS = {n: getattr(ARGS, n) for n in dir(ARGS) if not n.startswith('_') and getattr(ARGS, n, None) is not None}
    main(**KWARGS)
