"""
module to run with the -m flag

python -m async_sched.server --path "./schedules/"

"""
import argparse
from async_sched.server.srv import start_server


__all__ = ['NAME', 'get_argparse', 'main']


NAME = 'run'


def get_argparse(list_schedules=True, parent_parser=None):
    if parent_parser is None:
        p = argparse.ArgumentParser(description='Update the server command modules.')
    else:
        p = parent_parser.add_parser(NAME, help='Update the server command modules.')

    p.add_argument('--update_path', type=str, help='Command path that "update" imports files from.')

    p.add_argument('--host', type=str, default='127.0.0.1')
    p.add_argument('--port', type=int, default=8000)

    return p


def main(update_path: str = None, host='127.0.0.1', port=8000, **kwargs):
    # import logging
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    srv = start_server((host, port), update_path=update_path, global_server=True)
    srv.run_forever()


if __name__ == '__main__':
    P = get_argparse()
    ARGS = P.parse_args()

    KWARGS = {n: getattr(ARGS, n) for n in dir(ARGS) if not n.startswith('_') and getattr(ARGS, n, None) is not None}
    main(**KWARGS)
