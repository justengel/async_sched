# schedules/task2.py
from async_sched import get_server, Schedule
import datetime

server = get_server()


@server.register_callback  # or @server.register_callback('print_task2')
def print_task2(name):
    print('Task 2 is running! ', name, str(datetime.datetime.now()))


# Uncomment after running the server, then call python -m async_sched.client update_server, then run this
@server.register_callback('async_print')  # or @server.register_callback('print_task2')
async def print_task3(name):
    print('Async Task 3 is running! ', name, str(datetime.datetime.now()))
