
from .utils import get_loop, ScheduleError
from .schedule import Schedule, RepeatSchedule

try:
    from .server import get_server, set_server, start_server, Scheduler, \
        Message, Error, Quit, Update, RunCommand, ScheduleCommand, RunningSchedule, ListSchedules, StopSchedule

except (ImportError, Exception) as srverr:
    srv_error = srverr

    class ClassEnvironmentError:
        def __new__(cls, *args, **kwargs):
            raise EnvironmentError('Dependencies not installed! '
                                   'Libraries serial_json are required!') from srv_error

    get_server = ClassEnvironmentError
    set_server = ClassEnvironmentError
    start_server = ClassEnvironmentError
    Scheduler = ClassEnvironmentError

    Message = ClassEnvironmentError
    Error = ClassEnvironmentError
    Quit = ClassEnvironmentError
    Update = ClassEnvironmentError
    RunCommand = ClassEnvironmentError
    ScheduleCommand = ClassEnvironmentError
    RunningSchedule = ClassEnvironmentError
    ListSchedules = ClassEnvironmentError
    StopSchedule = ClassEnvironmentError


try:
    from .client import Client, \
        quit_server_async, quit_server, update_server_async, update_server, request_schedules_async, \
        request_schedules, run_command_async, run_command, schedule_command_async, schedule_command, \
        stop_schedule_async, stop_schedule

except (ImportError, Exception) as err:
    client_error = err

    class ClassEnvironmentError:
        def __new__(cls, *args, **kwargs):
            raise EnvironmentError('Dependencies not installed! '
                                   'Libraries serial_json are required!') from client_error

    Client = ClassEnvironmentError
    quit_server_async = quit_server = ClassEnvironmentError
    update_server_async = update_server = ClassEnvironmentError
    request_schedules_async = request_schedules = ClassEnvironmentError
    run_command_async = run_command = ClassEnvironmentError
    schedule_command_async = schedule_command = ClassEnvironmentError
    stop_schedule_async = stop_schedule = ClassEnvironmentError
