"""
module to run with the -m flag

python -m async_sched.client "update_server" --list_schedules 1
python -m async_sched.client "quit_server"
python -m async_sched.client "request_schedules"
python -m async_sched.client "stop_schedule" "Task 1"
python -m async_sched.client "run_command" "print_task" "abc"
python -m async_sched.client "schedule_command" "Task 1" "print_task" "abc" --seconds 10

"""
import argparse
from async_sched.client import module_update, module_request, module_stop, module_run, module_schedule, module_quit


if __name__ == '__main__':

    SUB_MODULES = {module_update.NAME: module_update,
                   module_quit.NAME: module_quit,
                   module_request.NAME: module_request,
                   module_stop.NAME: module_stop,
                   module_run.NAME: module_run,
                   module_schedule.NAME: module_schedule,
                   }

    P = argparse.ArgumentParser(description='Run a client command.')
    SUBCOMMANDS = P.add_subparsers(required=True, dest='subcommand', help='Run a sub-command.')
    PARSERS = {NAME: MODULE.get_argparse(parent_parser=SUBCOMMANDS) for NAME, MODULE in SUB_MODULES.items()}
    ARGS, REMAINING = P.parse_known_args()

    SUB_MODULES[ARGS.subcommand].main(**{n: getattr(ARGS, n) for n in dir(ARGS)
                                         if not n.startswith('_') and getattr(ARGS, n, None) is not None})
