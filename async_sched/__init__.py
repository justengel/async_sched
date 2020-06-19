
from .utils import ScheduleError
from .schedule import Schedule

try:
    from .server import get_server, set_server, Scheduler, Client, \
        Message, Error, Quit, Update, RunCommand, ScheduleCommand, RunningSchedule, ListSchedules, StopSchedule
except (ImportError, Exception) as err:
    error = err
    class ClassEnvironmentError:
        def __new__(cls, *args, **kwargs):
            raise EnvironmentError('Dependencies not installed! '
                                   'Libraries pydantic and pydantic_decoder are required!') from error

    get_server = ClassEnvironmentError
    set_server = ClassEnvironmentError
    Scheduler = ClassEnvironmentError
    Client = ClassEnvironmentError

    Message = ClassEnvironmentError
    Error = ClassEnvironmentError
    Quit = ClassEnvironmentError
    Update = ClassEnvironmentError
    RunCommand = ClassEnvironmentError
    ScheduleCommand = ClassEnvironmentError
    RunningSchedule = ClassEnvironmentError
    ListSchedules = ClassEnvironmentError
    StopSchedule = ClassEnvironmentError
