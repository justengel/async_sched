import asyncio
from typing import Union

from serial_json import DataClass
from ..schedule import Schedule

from .messages import Quit, Update, RunCommand, ScheduleCommand, ListSchedules, StopSchedule


__all__ = ['Client']


class Client(object):

    READ_SIZE = 4096

    def __init__(self, ip_address: str = None, port: int = 8000, loop: asyncio.AbstractEventLoop = None):
        self._loop = loop

        self.reader = None
        self.writer = None
        self._is_connected = False

        self.ip_address = ip_address
        self.port = port

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

    def start(self, ip_addr: str = None, port: int = None) -> 'Client':
        """Add a task to start running the server forever."""
        self.server_task = self.loop.create_task(self.start_async(ip_addr, port), name='client')
        return self

    async def start_async(self, ip_address: str = None, port: int = None):
        """Start the connection."""
        if ip_address is not None:
            self.ip_address = ip_address
        if port is not None:
            self.port = port
        self.reader, self.writer = await asyncio.open_connection(self.ip_address, self.port)
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
        print(f'{message.message!r}')

    async def send_update(self):
        """Send the quit command."""
        self.writer.write(Update().json().encode())
        await self.writer.drain()

        data = await self.reader.read(self.READ_SIZE)
        message = DataClass.from_json(data)
        print(f'{message.message!r}')

    async def request_schedules(self):
        """Print the list of schedules."""
        self.writer.write(ListSchedules().json().encode())
        await self.writer.drain()

        data = await self.reader.read(self.READ_SIZE)
        if not data:
            data = await self.reader.read(self.READ_SIZE)
        message = DataClass.from_json(data)
        print('Running Schedules:')
        for running in message.schedules:
            print(f'{running.name} = {running.schedule}')

    async def run_command(self, callback_name, *args, **kwargs):
        """Print the list of schedules."""
        self.writer.write(RunCommand(callback_name=callback_name, args=args, kwargs=kwargs).json().encode())
        await self.writer.drain()

        data = await self.reader.read(self.READ_SIZE)
        message = DataClass.from_json(data)
        print(f'{message.message!r}')

    async def schedule_command(self, name: str, schedule: Schedule, callback_name, *args, **kwargs):
        """Print the list of schedules."""
        json = ScheduleCommand(name=name, schedule=schedule,
                               callback_name=callback_name, args=args, kwargs=kwargs).json()
        self.writer.write(json.encode())
        await self.writer.drain()

        data = await self.reader.read(self.READ_SIZE)
        message = DataClass.from_json(data)
        print(f'{message.message!r}')

    async def stop_schedule(self, name: str):
        """Stop a running schedule."""
        self.writer.write(StopSchedule(name=name).json().encode())
        await self.writer.drain()

        data = await self.reader.read(self.READ_SIZE)
        message = DataClass.from_json(data)
        print(f'{message.message!r}')

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
