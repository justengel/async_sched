
import asyncio
from async_sched import Schedule


if __name__ == '__main__':
    async def print_schedule(schedule):
        print(schedule)

    second = Schedule(seconds=1, thursday=False)
    more = Schedule(seconds=0.5)

    loop = asyncio.get_event_loop()

    loop.create_task(second.run_async(print_schedule, second))
    loop.create_task(more.run_async(print_schedule, more))

    loop.run_forever()
