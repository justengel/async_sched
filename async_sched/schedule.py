import time
import inspect
import asyncio
import datetime
from typing import Union, Callable, Awaitable, Tuple, Optional, ClassVar

from dataclass_property import dataclass, field_property, field, MISSING, \
    Weekdays, weekdays_property, \
    datetime_property, time_property, timedelta_helper_property, seconds_property,\
    make_time, make_date, make_datetime, str_time, str_date, str_datetime


__all__ = ['Schedule']


@dataclass
class Schedule:
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
        at (datetime.datetime/str)[None]: Time of day when the schedule should run.
        start_on (datetime.datetime/str)[datetime.datetime.now()]: Date and time on which to start on.
        end_on (datetime.datetime/str)[None]: Date and time on which to end on.
        last_run (datetime.datetime/str)[None]: Date and time to make the next_run from.
        next_run (datetime.datetime/str)[None]: Manually set the next run time.
    """
    days: int = 0
    hours: int = 0
    minutes: int = 0
    milliseconds: int = 0
    microseconds: int = 0
    seconds: Union[int, float] = seconds_property('seconds')
    weeks: int = 0
    interval: datetime.timedelta = timedelta_helper_property()

    weekdays: Weekdays = field(default_factory=Weekdays)
    sunday: bool = weekdays_property('sunday')
    monday: bool = weekdays_property('monday')
    tuesday: bool = weekdays_property('tuesday')
    wednesday: bool = weekdays_property('wednesday')
    thursday: bool = weekdays_property('thursday')
    friday: bool = weekdays_property('friday')
    saturday: bool = weekdays_property('saturday')

    repeat: bool = True
    at: Optional[datetime.time] = time_property('at', allow_none=True)
    start_on: Optional[datetime.datetime] = datetime_property('start_on', default_factory=datetime.datetime.now)
    end_on: Optional[datetime.datetime] = datetime_property('end_on', allow_none=True)
    last_run: Optional[datetime.datetime] = datetime_property('last_run', allow_none=True)
    _next_run: Union[datetime.datetime, None] = field(default=None, init=False, repr=False)

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

    EXCLUDE_FIELDS = ('interval', *Weekdays.DAYS, 'next_run')
    INCLUDE_FIELDS = ('_next_run', )

    def __post_init__(self):
        # Change my fields for asdict
        include = {k: self.__class__.__dataclass_fields__[k] for k in self.INCLUDE_FIELDS}
        self.__dataclass_fields__ = {k: v for k, v in self.__class__.__dataclass_fields__.items()
                                     if k not in self.EXCLUDE_FIELDS}
        self.__dataclass_fields__.update(include)

    # ========== Methods ==========
    make_date = staticmethod(make_date)
    make_datetime = staticmethod(make_datetime)
    make_time = staticmethod(make_time)
    str_date = staticmethod(str_date)
    str_datetime = staticmethod(str_datetime)
    str_time = staticmethod(str_time)

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
        return self.end_on and now > self.end_on

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

        if callable(callback):
            return callback(*args, **kwargs)

    async def call_async(self, callback: Callable[..., Awaitable[None]] = None, *args, **kwargs) -> object:
        """Run the set callback and setup repeat if set."""
        await self.wait_async()
        await self.reschedule_async()
        if inspect.iscoroutinefunction(callback):
            return await callback(*args, **kwargs)
        elif callable(callback):
            return callback(*args, **kwargs)

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

    WEEKDAY_ATTRS = tuple(Weekdays.DAYS)
    INTERVAL_ATTRS = ('weeks', 'days', 'hours', 'minutes', 'seconds', 'milliseconds')
    STRING_NAME_ATTRS = INTERVAL_ATTRS + ('repeat', 'at')

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

    def __str__(self) -> str:
        attrs = tuple('{}={}'.format(attr, getattr(self, attr))
                      for attr in self.STRING_NAME_ATTRS if getattr(self, attr))

        allowed_weekdays = self.allowed_weekdays()
        if allowed_weekdays != self.WEEKDAY_ATTRS:
            attrs = attrs + ('on=[' + ', '.join(allowed_weekdays) + ']',)
        return '{cls}({attrs})'.format(cls=self.__class__.__name__, attrs=', '.join(attrs))

    def __repr__(self) -> str:
        return '<{str} at {id}>'.format(str=self.__str__(), id=id(self))

    # ========== Data Serialization ==========
    # def __getstate__(self) -> dict:
    #     return self.dict()
    #
    # def __setstate__(self, state: dict):
    #     for k, v in state.items():
    #         setattr(self, k, v)
