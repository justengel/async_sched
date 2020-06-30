# schedules/task1.py
from async_sched import get_server, Schedule
import datetime


def print_task1():
    print('Hello! I am task 1 ' + str(datetime.datetime.now()))


server = get_server()

s = Schedule(seconds=15, repeat=True)
server.add('Task 1', s, print_task1)  # This will remove existing 'Task 1' and schedule a new 'Task 1'
