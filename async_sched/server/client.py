import asyncio
from typing import Union, Tuple

from serial_json import DataClass
from ..schedule import Schedule

from .messages import Quit, Update, RunCommand, ScheduleCommand, ListSchedules, StopSchedule


__all__ = ['Client',
           'quit_server_async', 'quit_server', 'update_server_async', 'update_server', 'request_schedules_async',
           'request_schedules', 'run_command_async', 'run_command', 'schedule_command_async', 'schedule_command',
           'stop_schedule_async', 'stop_schedule']


class Client(object):

    READ_SIZE = 4096

    def __init__(self, addr: Union[str, Tuple[str, int]] = None, port: int = 8000,
                 loop: asyncio.AbstractEventLoop = None):
        if not isinstance(addr, (list, tuple)):
            addr = (addr, port)
        if len(addr) == 1:
            addr = addr + (port,)

        self._loop = loop

        self.reader = None
        self.writer = None
        self._is_connected = False

        self.ip_address = addr[0]
        self.port = addr[1]

    @property
    def loop(self) -> 'asyncio.AbstractEventLoop':
        if self._loop is not None:
            return self._loop
        try:
            return asyncio.get_running_loop()
        except (RuntimeError, Exception):
            return asyncio.get_event_loop()

    @loop.setter
    def loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    async def is_connected(self):
        """Return if the client is connected"""
        return self._is_connected

    def start(self, addr: Union[str, Tuple[str, int]] = None, port: int = None, **kwargs) -> 'Client':
        """Add a task to start running the server forever."""
        self.server_task = self.loop.create_task(self.start_async(addr=addr, port=port, **kwargs), name='client')
        return self

    async def start_async(self, addr: Union[str, Tuple[str, int]] = None, port: int = None, **kwargs):
        """Start the connection."""
        if isinstance(addr, (list, tuple)):
            if len(addr) > 0:
                self.ip_address = addr[0]
            if len(addr) > 1:
                self.port = addr[1]
        elif isinstance(addr, str):
            self.ip_address = addr
        if isinstance(port, int):
            self.port = port
        self.reader, self.writer = await asyncio.open_connection(self.ip_address, self.port, **kwargs)
        return self

    async def stop_async(self):
        """Stop the connection"""
        if self.writer is not None:
            self.writer.close()
            await self.writer.wait_closed()
        self.writer = None
        self.reader = None
        return self

    async def send_quit(self):
        """Send the quit command."""
        self.writer.write(Quit().json().encode())
        await self.writer.drain()

        data = await self.reader.read(self.READ_SIZE)
        message = DataClass.from_json(data)
        print(f'{message.message}')
        return message

    async def send_update(self):
        """Send the quit command."""
        self.writer.write(Update().json().encode())
        await self.writer.drain()

        data = await self.reader.read(self.READ_SIZE)
        message = DataClass.from_json(data)
        print(f'{message.message}')
        return message

    async def request_schedules(self, print_results=True):
        """Print the list of schedules."""
        self.writer.write(ListSchedules().json().encode())
        await self.writer.drain()

        data = await self.reader.read(self.READ_SIZE)
        if not data:
            data = await self.reader.read(self.READ_SIZE)
        message = DataClass.from_json(data)

        if print_results:
            print('Running Schedules:')
            for running in message.schedules:
                print(f'  {running.name} = {running.schedule}')

        return message

    async def run_command(self, callback_name, *args, **kwargs):
        """Print the list of schedules."""
        self.writer.write(RunCommand(callback_name=callback_name, args=args, kwargs=kwargs).json().encode())
        await self.writer.drain()

        data = await self.reader.read(self.READ_SIZE)
        message = DataClass.from_json(data)
        print(f'{message.message}')
        return message

    async def schedule_command(self, name: str, schedule: Schedule, callback_name, *args, **kwargs):
        """Print the list of schedules."""
        json = ScheduleCommand(name=name, schedule=schedule,
                               callback_name=callback_name, args=args, kwargs=kwargs).json()
        self.writer.write(json.encode())
        await self.writer.drain()

        data = await self.reader.read(self.READ_SIZE)
        message = DataClass.from_json(data)
        print(f'{message.message}')
        return message

    async def stop_schedule(self, name: str):
        """Stop a running schedule."""
        self.writer.write(StopSchedule(name=name).json().encode())
        await self.writer.drain()

        data = await self.reader.read(self.READ_SIZE)
        message = DataClass.from_json(data)
        print(f'{message.message}')
        return message

    async def __aenter__(self):
        if not await self.is_connected():
            await self.start_async()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.stop_async()

    def __enter__(self):
        if not self._is_connected:
            self.loop.run_until_complete(self.start_async())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.run_until_complete(self.stop_async())

        return exc_type is not None

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


async def quit_server_async(addr: Tuple[str, int]):
    """Send a command to the server to Quit.

    Args:
        addr (tuple): Server IP address
    """
    async with Client(addr) as client:
        return await client.send_quit()


def quit_server(addr: Tuple[str, int], loop: asyncio.AbstractEventLoop = None):
    """Send a command to the server to Quit.

    Args:
        addr (tuple): Server IP address
        loop (asyncio.AbstractEventLoop)[None]: Event loop to run the async command with.
    """
    if loop is None:
        loop = asyncio.get_running_loop() or asyncio.get_event_loop()
    return loop.run_until_complete(quit_server_async(addr))


async def update_server_async(addr: Tuple[str, int], list_schedules: bool = False):
    """Send a command to the server to Update Commands by reading files in the command_path

    Args:
        addr (tuple): Server IP address
        list_schedules (bool)[False]: If True request and print the schedules that the server is running.
    """
    async with Client(addr) as client:
        msg = await client.send_update()
        if list_schedules:
            msg = await client.request_schedules()
        return msg


def update_server(addr: Tuple[str, int], list_schedules: bool = False, loop: asyncio.AbstractEventLoop = None):
    """Send a command to the server to Update Commands.

    Args:
        addr (tuple): Server IP address
        list_schedules (bool)[False]: If True request and print the schedules that the server is running.
        loop (asyncio.AbstractEventLoop)[None]: Event loop to run the async command with.
    """
    if loop is None:
        loop = asyncio.get_running_loop() or asyncio.get_event_loop()
    return loop.run_until_complete(update_server_async(addr, list_schedules))


async def request_schedules_async(addr: Tuple[str, int]):
    """Send a command to the server to Update Commands by reading files in the command_path

    Args:
        addr (tuple): Server IP address
    """
    async with Client(addr) as client:
        return await client.request_schedules()


def request_schedules(addr: Tuple[str, int], print_results: bool = True, loop: asyncio.AbstractEventLoop = None):
    """Send a command to the server to Update Commands.

    Args:
        addr (tuple): Server IP address
        print_results (bool)[True]: If true print the schedules that were returned.
        loop (asyncio.AbstractEventLoop)[None]: Event loop to run the async command with.
    """
    if loop is None:
        loop = asyncio.get_running_loop() or asyncio.get_event_loop()
    return loop.run_until_complete(request_schedules_async(addr, print_results=print_results))


async def run_command_async(addr: Tuple[str, int],
                            callback_name: str = '', *args, **kwargs):
    """Send a command to the server to run a registered callback function with the given arguments.

    Args:
        addr (tuple): Server IP address
        callback_name (str)['']: Name of the registered callback function.
        *args: Positional arguments for the callback function.
        **kwargs: Keyword Arguments for the callback function.
    """
    if not callback_name:
        raise ValueError('Invalid callback name given')

    async with Client(addr) as client:
        return await client.run_command(callback_name, *args, **kwargs)


def run_command(addr: Tuple[str, int],
                callback_name: str = '', *args, loop: asyncio.AbstractEventLoop = None, **kwargs):
    """Send a command to the server to run a registered callback function with the given arguments.

    Args:
        addr (tuple): Server IP address
        callback_name (str)['']: Name of the registered callback function.
        *args: Positional arguments for the callback function.
        **kwargs: Keyword Arguments for the callback function.
        loop (asyncio.AbstractEventLoop)[None]: Event loop to run the async command with.
    """
    if loop is None:
        loop = asyncio.get_running_loop() or asyncio.get_event_loop()
    return loop.run_until_complete(run_command_async(addr, callback_name, *args, **kwargs))


async def schedule_command_async(addr: Tuple[str, int],
                                 name: str = '', schedule: Schedule = None, callback_name: str = '', *args, **kwargs):
    """Send a command to the server to schedule a callback function to run.

    Args:
        addr (tuple): Server IP address
        name (str)['']: Name of the schedule.
        schedule (Schedule)[None]: Schedule to run the callback function with.
        callback_name (str)['']: Name of the registered callback function.
        *args: Positional arguments for the callback function.
        **kwargs: Keyword Arguments for the callback function.
    """
    if not name:
        raise ValueError('Must give a name to keep track of the schedule!')
    if schedule is None:
        raise ValueError('Invalid schedule given!')
    if not callback_name:
        raise ValueError('Invalid callback name given!')

    async with Client(addr) as client:
        return await client.schedule_command(name, schedule, callback_name, *args, **kwargs)


def schedule_command(addr: Tuple[str, int],
                     name: str = '', schedule: Schedule = None, callback_name: str = '', *args,
                     loop: asyncio.AbstractEventLoop = None, **kwargs):
    """Send a command to the server to schedule a callback function to run.

    Args:
        addr (tuple): Server IP address
        name (str)['']: Name of the schedule.
        schedule (Schedule)[None]: Schedule to run the callback function with.
        callback_name (str)['']: Name of the registered callback function.
        *args: Positional arguments for the callback function.
        **kwargs: Keyword Arguments for the callback function.
        loop (asyncio.AbstractEventLoop)[None]: Event loop to run the async command with.
    """
    if loop is None:
        loop = asyncio.get_running_loop() or asyncio.get_event_loop()
    return loop.run_until_complete(schedule_command_async(addr, name, schedule, callback_name, *args, **kwargs))


async def stop_schedule_async(addr: Tuple[str, int], name: str = ''):
    """Send a command to the server to stop running a schedule.

    Args:
        addr (tuple): Server IP address
        name (str)['']: Name of the schedule.
    """
    if not name:
        raise ValueError('Must give a name to keep track of the schedule!')

    async with Client(addr) as client:
        return await client.stop_schedule(name)


def stop_schedule(addr: Tuple[str, int], name: str = '', loop: asyncio.AbstractEventLoop = None):
    """Send a command to the server to stop running a schedule.

    Args:
        addr (tuple): Server IP address
        name (str)['']: Name of the schedule.
        loop (asyncio.AbstractEventLoop)[None]: Event loop to run the async command with.
    """
    if loop is None:
        loop = asyncio.get_running_loop() or asyncio.get_event_loop()
    return loop.run_until_complete(stop_schedule_async(addr, name))
