"""
module to run with the -m flag

python -m async_sched.client.schedule_command "Task 1" "print_task" "abc" --seconds 10

"""
import argparse
import serial_json
from serial_json import Weekdays
from async_sched import Schedule
from async_sched.client.client import schedule_command


__all__ = ['NAME', 'get_argparse', 'main']


NAME = 'schedule_command'


def parse(value):
    try:
        return serial_json.loads(value)
    except:
        return value


def get_argparse(days=0, hours=0, minutes=0, seconds=0, milliseconds=0, microseconds=0, weeks=0, weekdays='',
                 repeat=False, at=None, start_on=None, end_on=None, next_run=None, parent_parser=None):
    if parent_parser is None:
        p = argparse.ArgumentParser(description='Schedule one of the registered commands to run.')
    else:
        p = parent_parser.add_parser(NAME, help='Schedule one of the registered commands to run.')

    p.add_argument('name', type=str, help='Name to assign the schedule you are running.')
    p.add_argument('callback_name', type=str, help='Registered callback name to run.')
    p.add_argument('args', type=object, nargs='*', help='Positional arguments to pass into the callback function.')

    # Schedule args
    p.add_argument('--days', type=int, default=days, help='Schedule field')
    p.add_argument('--hours', type=int, default=hours, help='Schedule field')
    p.add_argument('--minutes', type=int, default=minutes, help='Schedule field')
    p.add_argument('--seconds', type=float, default=seconds, help='Schedule field')
    p.add_argument('--milliseconds', type=int, default=milliseconds, help='Schedule field')
    p.add_argument('--microseconds', type=int, default=microseconds, help='Schedule field')
    p.add_argument('--weeks', type=int, default=weeks, help='Schedule field')
    p.add_argument('--weekdays', type=str, default=weekdays, help='Schedule field comma separate weekday names.')
    p.add_argument('--repeat', type=bool, default=repeat, help='Schedule field')
    p.add_argument('--at', type=str, default=at, help='Schedule field')
    p.add_argument('--start_on', type=str, default=start_on, help='Schedule field')
    p.add_argument('--end_on', type=str, default=end_on, help='Schedule field')
    p.add_argument('--next_run', type=str, default=next_run, help='Schedule field')

    p.add_argument('--host', type=str, default='127.0.0.1')
    p.add_argument('--port', type=int, default=8000)

    return p


def main(name, callback_name, args, days=0, hours=0, minutes=0, seconds=0, milliseconds=0, microseconds=0, weeks=0,
         weekdays='', repeat=False, at=None, start_on=None, end_on=None, next_run=None,
         host='127.0.0.1', port=8000, **kwargs):

    args = (parse(arg) for arg in args)
    weekdays = Weekdays(str(weekdays).split(','))

    s = Schedule(days=days, hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds,
                 microseconds=microseconds, weeks=weeks, weekdays=weekdays, repeat=repeat, at=at,
                 start_on=start_on, end_on=end_on, next_run=next_run)

    schedule_command((host, port), name, s, callback_name, *args)


if __name__ == '__main__':
    P = get_argparse()
    ARGS = P.parse_args()

    KWARGS = {n: getattr(ARGS, n) for n in dir(ARGS) if not n.startswith('_') and getattr(ARGS, n, None) is not None}
    main(**KWARGS)
