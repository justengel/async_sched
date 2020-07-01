import time
import inspect
import asyncio
import datetime
import logging
from typing import Union, Callable, Awaitable, Tuple, Optional, ClassVar

from serial_json import DataClass, field, field_property, MISSING, \
    Weekdays, weekdays_property, weekdays_attr_property, \
    datetime_property, time_property, timedelta_attr_property, seconds_property, make_datetime

from .utils import call, call_async, get_loop


__all__ = ['Schedule', 'RepeatSchedule']


class Schedule(DataClass):
    """Schedule a service to run.

    Example:

        Run async

        ..code-block:: python

            import asyncio
            import async_sched

            loop = asyncio.get_event_loop()

            async def print_sched(sched):
                print(sched)

            seconds = async_sched.Schedule(seconds=1)
            loop.create_task(seconds.run_async(print_sched, seconds))

            minutes = async_sched.Schedule(seconds=2)
            loop.create_task(minutes.run_async(print_sched, minutes))

            loop.run_forever()

        Run synchronous.

        ..code-block:: python

            def hello():
                print('hello')

            sched = Schedule(seconds=5)

            while True:
                sched.wait()
                hello()
                time.sleep(1)

    Args:
        days (int)[0]: Number of days when the next run should happen.
        hours (int)[0]: Number of hours when the next run should happen.
        minutes (int)[0]: Number of minutes when the next run should happen.
        seconds (int)[0]: Number of seconds when the next run should happen.
        milliseconds (int)[0]: Number of milliseconds when the next run should happen.
        microseconds (int)[0]: Number of microseconds when the next run should happen.
        weeks (int)[0]: Number of weeks for the interval
        interval (datetime.timedetla)[None]: Timedelta property for the time values.

        weekdays (Weekdays)[Weekdays()]: List of weekdays to run on.
        sundays (bool)[None]: Allow the schedule to run on sundays. If all weekdays are None allow all weekdays.
        mondays (bool)[None]: Allow the schedule to run on mondays. If all weekdays are None allow all weekdays.
        tuesdays (bool)[None]: Allow the schedule to run on tuesdays. If all weekdays are None allow all weekdays.
        wednesdays (bool)[None]: Allow the schedule to run on wednesdays. If all weekdays are None allow all weekdays.
        thursdays (bool)[None]: Allow the schedule to run on thursdays. If all weekdays are None allow all weekdays.
        fridays (bool)[None]: Allow the schedule to run on fridays. If all weekdays are None allow all weekdays.
        saturdays (bool)[None]: Allow the schedule to run on saturdays. If all weekdays are None allow all weekdays.

        repeat (bool)[True]: If True repeat the schedule else run once.
        at (Time/str)[None]: Time of day when the schedule should run.
        start_on (DateTime/str)[datetime.datetime.now()]: Date and time on which to start on.
        end_on (DateTime/str)[None]: Date and time on which to end on.
        last_run (DateTime/str)[None]: Date and time to make the next_run from.
        next_run (DateTime/str)[None]: Manually set the next run time.
    """
    days: int = field(0, skip_repr=0, skip_dict=0)
    hours: int = field(0, skip_repr=0, skip_dict=0)
    minutes: int = field(0, skip_repr=0, skip_dict=0)
    milliseconds: int = field(0, skip_repr=0, skip_dict=0)
    microseconds: int = field(0, skip_repr=0, skip_dict=0)
    seconds: Union[int, float] = seconds_property('seconds', skip_repr=0, skip_dict=0)
    weeks: int = field(0, skip_repr=0, skip_dict=0)
    interval: datetime.timedelta = timedelta_attr_property(required=False, repr=False, dict=False)

    weekdays: Weekdays = weekdays_property('weekdays', default_factory=Weekdays,
                                           skip_repr=Weekdays(), skip_dict=Weekdays())
    sunday: bool = weekdays_attr_property('weekdays', 'sunday', repr=False, dict=False)
    monday: bool = weekdays_attr_property('weekdays', 'monday', repr=False, dict=False)
    tuesday: bool = weekdays_attr_property('weekdays', 'tuesday', repr=False, dict=False)
    wednesday: bool = weekdays_attr_property('weekdays', 'wednesday', repr=False, dict=False)
    thursday: bool = weekdays_attr_property('weekdays', 'thursday', repr=False, dict=False)
    friday: bool = weekdays_attr_property('weekdays', 'friday', repr=False, dict=False)
    saturday: bool = weekdays_attr_property('weekdays', 'saturday', repr=False, dict=False)

    repeat: bool = False
    at: datetime.time = time_property('at', allow_none=True, required=False, skip_repr=None, skip_dict=None)
    start_on: datetime.datetime = datetime_property('start_on', default_factory=datetime.datetime.now, repr=False)
    end_on: datetime.datetime = datetime_property('end_on', allow_none=True, required=False, skip_repr=None, skip_dict=None)
    last_run: datetime.datetime = datetime_property('last_run', allow_none=True, required=False, repr=False, skip_dict=None)
    _next_run: Union[datetime.datetime, None] = field(default=None, repr=False, skip_dict=None)

    logger: logging.Logger = field(default=logging.getLogger('asyncio'), repr=False, dict=False, hash=False, compare=False)

    @field_property(default=None)
    def next_run(self) -> Union[datetime.datetime, None]:
        # Check end on
        now = datetime.datetime.now()
        if self.past_end(now):
            return None

        # Check for a set next run
        elif getattr(self, '_next_run', None) is not None:
            return self._next_run

        return self.create_run_time()

    @next_run.setter
    def next_run(self, value: Union[datetime.datetime, str, None]):
        if value is not None:
            value = make_datetime(value)
        self._next_run = value

    def run_in(self, now: datetime.datetime = None) -> Union[float, int]:
        """Return the number of seconds to wait until this should run."""
        if now is None:
            now = datetime.datetime.now()

        next_run = self.next_run
        if next_run is None:
            return -1
        elif now > next_run:
            return 0

        wait_time = (next_run - now).total_seconds()
        return wait_time

    def can_run(self, now: datetime.datetime = None) -> bool:
        """Return if this schedule can run now."""
        return self.run_in(now) == 0

    def past_end(self, now: datetime.datetime = None) -> bool:
        """Return if this datetime is past the end_on datetime and should stop running"""
        if now is None:
            now = datetime.datetime.now()
        return self.end_on and now >= self.end_on

    def wait(self, now: datetime.datetime = None) -> 'Schedule':
        """Wait until it is time to run."""
        time.sleep(self.run_in(now))
        return self

    async def wait_async(self, now: datetime.datetime = None) -> 'Schedule':
        """Asynchronous Wait until it is time to run."""
        await asyncio.sleep(self.run_in(now))
        return self

    def __await__(self) -> 'Schedule':
        yield from self.wait_async().__await__()
        return self

    def reschedule(self, now: datetime.datetime = None) -> 'Schedule':
        """Reset to get the next run time."""
        if now is None:
            now = datetime.datetime.now()

        # Setup the run times
        self.last_run = now
        self.next_run = None
        if not self.repeat:
            self.end_on = self.last_run
        return self

    async def reschedule_async(self, now: datetime.datetime = None) -> 'Schedule':
        """Reset to get the next run time."""
        return self.reschedule(now)

    def call(self, callback: Callable = None, *args, **kwargs) -> object:
        """Wait for the schedule and run the callback"""
        self.wait()
        self.reschedule()

        task = asyncio.Task.current_task().get_name()
        self.logger.info(f'Running Task "{task}" with {self}')

        try:
            return call(callback, *args, **kwargs)
        except Exception as err:
            self.logger.critical(f'Error in Task "{task}": {err}')

    async def call_async(self, callback: Callable[..., Awaitable[None]] = None, *args, **kwargs) -> object:
        """Run the set callback and setup repeat if set."""
        await self.wait_async()
        await self.reschedule_async()

        task = asyncio.Task.current_task().get_name()
        self.logger.info(f'Running Task "{task}" with {self}')

        try:
            return await call_async(callback, *args, **kwargs)
        except Exception as err:
            self.logger.critical(f'Error in Task "{task}": {err}')

    def run(self, callback: Callable = None, *args, **kwargs) -> 'Schedule':
        """Loop until and call this function until the schedule ends."""
        while not self.past_end():
            self.call(callback, *args, **kwargs)
        return self

    async def run_async(self, callback: Callable[..., Awaitable[None]] = None, *args, **kwargs) -> 'Schedule':
        """Generator to keep running this schedule repeatedly."""
        while not self.past_end():
            await self.call_async(callback, *args, **kwargs)
        return self

    def start_task(self, callback: Callable[..., Awaitable[None]] = None, *args,
                   loop: asyncio.AbstractEventLoop = None, task_name: str = None,
                   **kwargs) -> 'asyncio.Task':
        """Start running this schedule as a task."""
        if loop is None:
            loop = get_loop()
        task = loop.create_task(self.run_async(callback, *args, **kwargs), name=task_name)
        return task

    def allowed_weekdays(self) -> Tuple[str]:
        """Return if all of the days of the week are None."""
        return tuple(self.weekdays)

    def is_allowed_weekday(self, dt: datetime.datetime) -> bool:
        """Return if the given datetime is on an allowed weekday."""
        return dt.weekday() in self.weekdays
        # return dt.strftime('%As').lower() in self.weekdays

    def make_at(self, dt: Union[datetime.datetime, datetime.timedelta]) -> datetime.datetime:
        """Make the given datetime run at the set "at" time if the "at" time was set."""
        if isinstance(dt, datetime.timedelta):
            today = datetime.datetime.today()
            return datetime.datetime(year=today.year, month=today.month, day=today.day,
                            hour=0, minute=0, second=0, microsecond=0) + dt
        else:
            return datetime.datetime(year=dt.year, month=dt.month, day=dt.day,
                            hour=self.at.hour, minute=self.at.minute, second=self.at.second,
                            microsecond=self.at.microsecond)

    def create_run_time(self) -> Union[datetime.datetime, None]:
        """Make the next_run datetime."""
        from_dt = self.last_run or self.start_on or datetime.datetime.now()
        dt = from_dt

        # Increment the interval and make at time
        dt = dt + self.interval
        if self.at is not None:
            dt = self.make_at(dt)

        # Check if allowed on this weekday
        i = 0
        while not self.is_allowed_weekday(dt):
            # Increment the interval and make at time
            dt = dt + datetime.timedelta(days=1)  # Increment by days
            if self.at is not None:
                dt = self.make_at(dt)

            i += 1
            if i > 7:
                self.end_on = from_dt  # No weekdays for this interval are allowed
                return None

        return dt

    def stop(self, loop: asyncio.AbstractEventLoop = None):
        """Stop running all tasks associated with this schedule"""
        if loop is None:
            loop = get_loop()
        self.end_on = datetime.datetime.now()
        try:
            # Assume only one task runs this schedule or stop cancels all tasks with this schedule.
            for task in asyncio.all_tasks(loop):
                try:
                    if inspect.getcoroutinelocals(task.get_coro())['self'] == self:
                        task.cancel()
                except:
                    pass
        except:
            pass

    async def stop_async(self, ):
        self.stop()

    cancel = stop
    cancel_async = stop_async


class RepeatSchedule(Schedule):
    repeat: bool = True
