
def check_values(obj, days=0, hours=0, minutes=0, seconds=0, milliseconds=0, microseconds=0,
                 sunday=True, monday=True, tuesday=True, wednesday=True, thursday=True, friday=True, saturday=True,
                 at=None, start_on=None, end_on=None, repeat=False, last_run=None, next_run=None):
    assert obj.days == days, f'{obj.days} != {days}'
    assert obj.hours == hours, f'{obj.hours} != {hours}'
    assert obj.minutes == minutes, f'{obj.minutes} != {minutes}'
    assert obj.seconds == seconds, f'{obj.seconds} != {seconds}'
    assert obj.milliseconds == milliseconds, f'{obj.milliseconds} != {milliseconds}'
    assert obj.microseconds == microseconds, f'{obj.microseconds} != {microseconds}'

    assert obj.sunday == sunday, f'{obj.sunday} != {sunday}'
    assert obj.monday == monday, f'{obj.monday} != {monday}'
    assert obj.tuesday == tuesday, f'{obj.tuesday} != {tuesday}'
    assert obj.wednesday == wednesday, f'{obj.wednesday} != {wednesday}'
    assert obj.thursday == thursday, f'{obj.thursday} != {thursday}'
    assert obj.friday == friday, f'{obj.friday} != {friday}'
    assert obj.saturday == saturday, f'{obj.saturday} != {saturday}'

    assert obj.at == at, f'{obj.at} != {at}'
    if start_on is not None:
        assert obj.start_on == start_on, f'{obj.start_on} != {start_on}'
    assert obj.end_on == end_on, f'{obj.end_on} != {end_on}'
    assert obj.repeat == repeat, f'{obj.repeat} != {repeat}'
    assert obj.last_run == last_run, f'{obj.last_run} != {last_run}'
    if next_run is not None:
        assert obj.next_run == next_run, f'{obj.next_run} != {next_run}'


def test_import():
    from async_sched.schedule import Schedule


def test_constructor():
    import datetime
    from async_sched.schedule import Schedule

    s = Schedule()
    for prop in ['weeks', 'days', 'hours', 'minutes', 'seconds', 'milliseconds', 'microseconds', 'interval',
                 'weekdays', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday',
                 'repeat', 'at', 'start_on', 'end_on', 'last_run', '_next_run']:
        assert hasattr(s, prop), 'No property {}'.format(prop)

    now = datetime.datetime.now()
    assert isinstance(s.start_on, datetime.datetime), type(s.start_on)
    s.start_on = s.start_on.replace(second=0, microsecond=0)
    now = now.replace(second=0, microsecond=0)
    check_values(s, start_on=now)  # Check default values

    s = Schedule(days=1)
    check_values(s, days=1)

    s = Schedule(seconds=0.5)
    check_values(s, seconds=0, milliseconds=500)


def test_interval_properties():
    import datetime
    from async_sched.schedule import Schedule

    s = Schedule(seconds=0.5)
    check_values(s, seconds=0, milliseconds=500)

    s.seconds = 0.2
    check_values(s, seconds=0, milliseconds=200)

    s.milliseconds = 100
    check_values(s, seconds=0, milliseconds=100)

    s.interval = datetime.timedelta()


def test_serializer():
    from async_sched.schedule import Schedule

    s = Schedule(seconds=0.5)
    d = s.dict()
    assert 'days' in d and d['days'] == s.days
    assert 'hours' in d and d['hours'] == s.hours
    assert 'minutes' in d and d['minutes'] == s.minutes
    assert 'milliseconds' in d and d['milliseconds'] == s.milliseconds
    assert 'microseconds' in d and d['microseconds'] == s.microseconds
    assert 'seconds' in d and d['seconds'] == s.seconds
    assert 'weeks' in d and d['weeks'] == s.weeks
    assert 'weekdays' in d and d['weekdays'] == s.weekdays, '{} != {}'.format(d['weekdays'], s.weekdays)
    assert 'repeat' in d and d['repeat'] == s.repeat
    assert 'at' in d and d['at'] == s.at
    assert 'start_on' in d and d['start_on'] == s.start_on
    assert 'end_on' in d and d['end_on'] == s.end_on
    assert 'last_run' in d and d['last_run'] == s.last_run
    assert '_next_run' in d and d['_next_run'] == s._next_run

    s = Schedule(hours=1, sunday=False, at='6:40 PM')
    print(s)
    d = s.dict()
    assert 'days' in d and d['days'] == s.days
    assert 'hours' in d and d['hours'] == s.hours
    assert 'minutes' in d and d['minutes'] == s.minutes
    assert 'milliseconds' in d and d['milliseconds'] == s.milliseconds
    assert 'microseconds' in d and d['microseconds'] == s.microseconds
    assert 'seconds' in d and d['seconds'] == s.seconds
    assert 'weeks' in d and d['weeks'] == s.weeks
    assert 'weekdays' in d and d['weekdays'] == s.weekdays, '{} != {}'.format(d['weekdays'], s.weekdays)
    assert 'repeat' in d and d['repeat'] == s.repeat
    assert 'at' in d and d['at'] == s.at
    assert 'start_on' in d and d['start_on'] == s.start_on
    assert 'end_on' in d and d['end_on'] == s.end_on
    assert 'last_run' in d and d['last_run'] == s.last_run
    assert '_next_run' in d and d['_next_run'] == s._next_run


if __name__ == '__main__':
    test_import()
    test_constructor()
    test_interval_properties()
    test_serializer()

    print('All tests finished successfully!')
