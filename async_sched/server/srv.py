import os
import sys
import logging
import asyncio
from typing import Callable, Awaitable, Union, Tuple

from serial_json import DataClass, loads, dumps

try:
    from importlib import reload
except (ImportError, Exception):
    from imp import reload

from ..utils import print_exception, get_loop, call, call_async
from ..schedule import Schedule
from .messages import Message, Error, Quit, Update, RunCommand, ScheduleCommand, RunningSchedule, \
    ListSchedules, StopSchedule


__all__ = ['get_server', 'set_server', 'start_server', 'FakeScheduler', 'Scheduler']


SERVER = None


def get_server():
    global SERVER
    if SERVER is None:
        return FakeScheduler()
    return SERVER


def set_server(value):
    global SERVER
    SERVER = value


def start_server(addr: Union[str, Tuple[str, int]] = None, port: int = 8000, update_path: str = None,
                 global_server: bool = False, set_env: bool = False,
                 logger: logging.Logger = None, loop: asyncio.AbstractEventLoop = None):
    """Create a scheduler and start it as a server.

    Args:
        addr (str/tuple)[None]: Ip address or tuple of ip address, port.
        port (int)[8000]: Socket port to connect to.
        update_path (str)[None]: Path to directory that holds importable python files to run schedules with.
        global_server (bool)[False]: If True set this server as the main global server.
        set_env (bool)[False]: Set this address as the environment variable.
        logger (logging.Logger)[None]: Python logger
        loop (asyncio.AbstractEventLoop)[None]: Async event loop to run with if None use the running loop.
    """
    srv = Scheduler(addr=addr, port=port, update_path=update_path, logger=logger, loop=loop)
    if global_server:
        set_server(srv)
    if set_env:
        os.environ['ASYNC_SCHED_HOST'] = str(srv.ip_address)
        os.environ['ASYNC_SCHED_PORT'] = str(srv.port)

    srv.start()
    srv.update_commands()
    return srv


class FakeScheduler(object):
    def register_callback(self, name: str = None, func: Callable[..., Awaitable[None]] = None):
        if callable(name) and func is None:
            func = name
            name = None

        if func is None:
            def decorator(func):
                return self.register_callback(name, func)
            return decorator
        return func

    def __getattr__(self, item):
        if item == 'register_callback':
            return super().__getattr__(item)

        def fake(*args, **kwargs):
            return type(self)()
        return fake


class Scheduler(object):

    READ_SIZE = 4096

    def __init__(self, addr: Union[str, Tuple[str, int]] = None, port: int = 8000, update_path=None,
                 logger: logging.Logger = None, loop: asyncio.AbstractEventLoop = None):
        """Create a scheduler and start it as a server.

        Args:
            addr (str/tuple)[None]: Ip address or tuple of ip address, port.
            port (int)[8000]: Socket port to connect to.
            update_path (str)[None]: Path to directory that holds importable python files to run schedules with.
            logger (logging.Logger)[None]: Python logger
            loop (asyncio.AbstractEventLoop)[None]: Async event loop to run with if None use the running loop.
        """
        if not isinstance(addr, (list, tuple)):
            addr = (addr, port)
        if len(addr) == 1:
            addr = addr + (port,)

        self._loop = loop
        self.logger = logger or logging.getLogger("asyncio")

        self.update_path = update_path
        self.tasks = {}
        self.callbacks = {}
        self.server = None
        self.server_task = None

        self.ip_address = addr[0]
        self.port = addr[1]

    def update_commands(self, module_name: str = ''):
        """Read all of the files in the command path and register those commands to be able to run."""
        if self.update_path is None:
            return

        if self.update_path not in sys.path:
            sys.path.insert(0, self.update_path)

        if str(module_name).lower().endswith('.py'):
            module_name = module_name[:-3]

        for filename in os.listdir(self.update_path):
            try:
                name = os.path.splitext(filename)[0]
                if not name.startswith('_') and (not module_name or module_name == name):
                    if name in sys.modules:
                        reload(sys.modules[name])
                        self.logger.info(f'Reloaded module {name}')
                    else:
                        mod = __import__(name)  # Use get_server() to register the callback.
                        self.logger.info(f'Imported module {name}')
            except (ImportError, Exception) as err:
                print_exception(err, msg=f'Could not import {filename}')
                self.logger.info(f'Could not import {filename}')

    @property
    def loop(self) -> 'asyncio.AbstractEventLoop':
        if self._loop is not None:
            return self._loop
        return get_loop()

    @loop.setter
    def loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def register_callback(self, name: str = None, func: Callable[..., Awaitable[None]] = None):
        """Register a callback function to be callable from a received message.

        Args:
            name (str)[None]: Name of the callback function. If func the name will be populated from the func.__name__.
            func (callable)[None]: Callback function to call. If None a decorator wrapper will be returned.

        Returns:
            func (callable): If given func is None a decorator function will be returned else the given function.
        """
        if callable(name) and func is None:
            func = name
            name = None

        if func is None:
            def decorator(func):
                return self.register_callback(name, func)
            return decorator

        if name is None:
            name = func.__name__

        self.callbacks[name] = func
        return func

    async def handle_client(self, reader, writer):
        """Run the client. This code handles the communication between the client and server."""
        addr = writer.get_extra_info('peername')
        self.logger.info(f'Client connected {addr}')

        while self.is_serving() and not reader.at_eof() and not writer.is_closing():
            try:
                data = await reader.read(self.READ_SIZE)
                if not data:
                    continue
            except (TypeError, ValueError, Exception):
                break

            try:
                message = DataClass.from_json(data)
            except (TypeError, ValueError, Exception):
                self.logger.error('Invalid data received!')
                message = None
                continue

            if isinstance(message, Quit):
                self.logger.info('Quit Received')
                writer.write(Message(message='Stopping server').json().encode())
                await writer.drain()
                await self.stop_async()
                try: self.loop.stop()
                except: pass
                try: self.loop.close()
                except: pass

            elif isinstance(message, Update):
                self.logger.info(f'Update "{message.module_name}" Received')
                self.update_commands(module_name=message.module_name)

                writer.write(Message(message=f'Updated Command {message.module_name}').json().encode())
                await writer.drain()

            elif isinstance(message, ListSchedules):
                self.logger.info('List Schedules Received')
                try:
                    li = ListSchedules(schedules=[RunningSchedule(name=name, schedule=Schedule(**item[1].dict()))
                                                  for name, item in self.tasks.items()])
                    writer.write(li.json().encode())
                except Exception as err:
                    print_exception(err, msg='Cannot read the list of schedules!')
                    writer.write(Error(message='Cannot read the list of schedules!').json().encode())
                await writer.drain()

            elif isinstance(message, RunCommand):
                self.logger.info(f'Run Command "{message.callback_name}" Received')
                try:
                    cmd = self.callbacks[message.callback_name]
                    await call_async(cmd, *message.args, **message.kwargs)
                    writer.write(Message(message='Command "{}" ran successfully!'.format(message.callback_name)).json().encode())
                except Exception as err:
                    print_exception(err, msg='Could not run command "{}"'.format(message.callback_name))
                    writer.write(Error(message='Error in command "{}"'.format(message.callback_name)).json().encode())
                await writer.drain()

            elif isinstance(message, ScheduleCommand):
                self.logger.info(f'Schedule Command "{message.name}" Received')
                try:
                    s = message.schedule
                    cmd = self.callbacks[message.callback_name]
                    self.add(message.name, s, cmd, *message.args, **message.kwargs)
                    writer.write(Message(message='Scheduled Command "{}" is running!'.format(message.callback_name)).json().encode())
                except Exception as err:
                    print_exception(err, msg='Could not run command "{}"'.format(message.callback_name))
                    writer.write(Error(message='Error in command "{}"'.format(message.callback_name)).json().encode())
                await writer.drain()

            elif isinstance(message, StopSchedule):
                self.logger.info(f'Stop Schedule "{message.name}" Received')
                try:
                    self.remove(message.name)
                    writer.write(Message(message='Stopped running the schedule named "{}"!'.format(message.name)).json().encode())
                except Exception as err:
                    print_exception(err, msg='Error while stopping schedule "{}"'.format(message.name))
                    writer.write(Error(message='Error while stopping schedule "{}"'.format(message.name)).json().encode())
                await writer.drain()

            else:
                self.logger.info(f'Unknown Command Received')
                writer.write(Error(message='Unknown command given!').json().encode())
                await writer.drain()

        # Close when ending
        writer.close()
        self.logger.info(f'Client closed {addr}')

    def is_serving(self) -> bool:
        """Return if the server is running."""
        try:
            return self.server.is_serving()
        except (AttributeError, Exception):
            return False

    def start(self, addr: Union[str, Tuple[str, int]] = None, port: int = None, **kwargs) -> 'Scheduler':
        """Add a task to start running the server forever."""
        self.server_task = self.loop.create_task(self.start_async(addr=addr, port=port, **kwargs), name='server')
        return self

    async def start_async(self, addr: Union[str, Tuple[str, int]] = None, port: int = None, **kwargs):
        """Start running the server forever."""
        if isinstance(addr, (list, tuple)):
            if len(addr) > 0:
                self.ip_address = addr[0]
            if len(addr) > 1:
                self.port = addr[1]
        elif isinstance(addr, str):
            self.ip_address = addr
        if isinstance(port, int):
            self.port = port
        self.server = await asyncio.start_server(self.handle_client, self.ip_address, self.port, loop=self.loop, **kwargs)

        addr = self.server.sockets[0].getsockname()
        self.logger.info(f'Started Serving on {addr}')

        try:
            async with self.server:
                await self.server.serve_forever()
        finally:
            self.logger.info(f'Stopped serving on {addr}')

    def stop(self):
        """Stop running the server."""
        self.logger.info('Attempting to stop the server')
        try:
            self.server.close()
        except (AttributeError, Exception):
            pass
        try:
            self.server_task.stop()
        except (AttributeError, Exception):
            pass

        return self

    async def stop_async(self):
        """Stop the server from running."""
        return self.stop()

    def add(self, name: str, schedule: Schedule, callback: Callable[..., Awaitable[None]] = None, *args, **kwargs):
        """Add a schedule to run.

        Args:
            name (str): Name of the schedule
            schedule (Schedule): Schedule to run.
            callback (callable/awaitable): Function to run on the given schedule.
            *args (tuple/object): Positional arguments to pass into the callback function.
            **kwargs (dict/object): Keyword arguments to pass into the callback function.
        """
        # Remove any old tasks with the same name
        self.remove(name)

        # Start a new task
        task = self.loop.create_task(schedule.run_async(callback, *args, **kwargs), name=name)
        self.tasks[name] = [task, schedule]

    def remove(self, name: str):
        """Remove and stop running a schedule.

        Args:
            name (str): Name of the schedule
        """
        try:
            task, sched = self.tasks.pop(name)
            try:
                task.cancel()
            except:
                pass
            try:
                sched.stop()
            except:
                pass
        except (KeyError, Exception):
            pass

    # ========== Loop Functions ==========
    def create_task(self, coro, *, name=None):
        """Create a task to run on the loop"""
        return self.loop.create_task(coro, name=name)

    def run_until_complete(self, future):
        """Start running the asyncio event loop until the given future is complete."""
        return self.loop.run_until_complete(future)

    def run_forever(self):
        """Start running the asyncio event loop forever."""
        return self.loop.run_forever()

    def get_debug(self) -> bool:
        """Return if the asyncio loop is logging."""
        return self.loop.get_debug()

    def set_debug(self, value: bool):
        """Set if the asyncio loop should be logging."""
        self.loop.set_debug(value)
