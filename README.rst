===========
async_sched
===========

Use async to have functions run on a schedule.

Example
=======

Async Sched can run tasks on a schedule. It can also receive new tasks (in limited fashion) and change the running
schedules without stopping the service.

::

    scheduler.py
    schedules/
        task1.py
        task2.py


.. code-block:: python

    # scheduler.py
    import async_sched

    srv = async_sched.start_server(('127.0.0.1', 8000),
                                   update_path='./schedules',
                                   global_server=True)

    # srv.add('3 Second', async_sched.Schedule(seconds=3), print, 'Hello 3 seconds')

    srv.run_forever()


Task 1 in the schedules directory will automatically be imported. Because `start_server` sets the server as an
accessible attribute with `get_server` we can dynamically add schedules.

.. code-block:: python

    # schedules/task1.py
    from async_sched import get_server, Schedule
    import datetime


    def print_task1():
        print('Hello! I am task 1 ' + str(datetime.datetime.now()))

    s = Schedule(seconds=30, repeat=True)

    # This will remove an existing 'Task 1' and schedule a new 'Task 1'
    server = get_server()
    server.add('Task 1', s, print_task1)


In the task 2 file we are not scheduling any commands, but we are registering a callback function that can be run
from a client later.

.. code-block:: python

    # schedules/task2.py
    from async_sched import get_server, Schedule
    import datetime

    server = get_server()


    @server.register_callback  # or @server.register_callback('print_task2')
    def print_task2(name):
        print('Task 2 is running! ', name, str(datetime.datetime.now()))


Now run the scheduler server to listen to remote commands and manage the running schedules.

    python scheduler.py

    # or python -m async_sched.server.run --path "schedules" --host "127.0.0.1" --port 8000


Use a client to print the running schedules.


    python -m async_sched.client.request_schedules --host "127.0.0.1" --port 8000

Reload the files in the `./schedules/` directory.

    python -m async_sched.client.update server --host "127.0.0.1" --port 8000

Stop a schedule that is running.

    python -m async_sched.client.stop_schedule "Task 1" --host "127.0.0.1" --port 8000

Run a registered callback function.

    python -m async_sched.client run_command "print_task2" "hello" --host "127.0.0.1" --port 8000

Schedule a registered command.

    python -m async_sched.client schedule_command "print_task2" "hello" --seconds 10 --host "127.0.0.1" --port 8000
