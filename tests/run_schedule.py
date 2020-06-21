
import asyncio
from async_sched import Schedule, RepeatSchedule

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("asyncio").setLevel(logging.DEBUG)


if __name__ == '__main__':
    async def print_schedule(schedule):
        print(schedule)

    second = Schedule(seconds=1, thursday=False, repeat=True)
    more = Schedule(seconds=0.5, repeat=True)
    repeat = RepeatSchedule(seconds=0.1)  # Automatically sets repeat to True

    loop = asyncio.get_event_loop()

    loop.create_task(second.run_async(print_schedule, second))
    loop.create_task(more.run_async(print_schedule, more))
    loop.create_task(more.run_async(print_schedule, repeat))

    loop.run_forever()
