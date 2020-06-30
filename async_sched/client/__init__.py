from async_sched.client import quit_server as module_quit
from async_sched.client import request_schedules as module_request
from async_sched.client import run_command as module_run
from async_sched.client import schedule_command as module_schedule
from async_sched.client import stop_schedule as module_stop
from async_sched.client import update_server as module_update

from .client import Client, \
    quit_server_async, quit_server, update_server_async, update_server, request_schedules_async, \
    request_schedules, run_command_async, run_command, schedule_command_async, schedule_command, \
    stop_schedule_async, stop_schedule

# The other modules in this package exist for the "-m" python flag
# `python -m async_sched.client.request_schedules --host "12.0.0.1" --port 8000`


__all__ = ['Client',
           'quit_server_async', 'quit_server', 'update_server_async', 'update_server', 'request_schedules_async',
           'request_schedules', 'run_command_async', 'run_command', 'schedule_command_async', 'schedule_command',
           'stop_schedule_async', 'stop_schedule',

           'module_quit', 'module_request', 'module_run', 'module_schedule', 'module_stop', 'module_update']
