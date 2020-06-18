from typing import List

from serial_json import DataClass, field

from ..schedule import Schedule


__all__ = ['DataClass', 'Message', 'Error', 'Quit', 'Update', 'RunCommand', 'ScheduleCommand',
           'RunningSchedule', 'ListSchedules', 'StopSchedule']


class Message(DataClass):
    message: str


class Error(DataClass):
    message: str


class Quit(DataClass):
    pass


class Update(DataClass):
    pass


class RunCommand(DataClass):
    callback_name: str
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)


class ScheduleCommand(DataClass):
    name: str
    schedule: Schedule
    callback_name: str
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)


class RunningSchedule(DataClass):
    name: str
    schedule: Schedule


class ListSchedules(DataClass):
    schedules: List[RunningSchedule] = field(default_factory=list)


class StopSchedule(DataClass):
    name: str
