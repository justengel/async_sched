import asyncio
import async_sched


async def main():
    async with async_sched.Client('127.0.0.1', 8000) as client:
        s = async_sched.Schedule(seconds=5, repeat=True)
        await client.schedule_command('5 Seconds', s, 'print', s)
        await client.request_schedules()


async def main_func():
    addr = ('127.0.0.1', 8000)

    s = async_sched.Schedule(seconds=5, repeat=True)
    await async_sched.schedule_command_async(addr, '5 Seconds', s, 'print', s)
    await async_sched.request_schedules_async(addr)


if __name__ == '__main__':
    asyncio.run(main())
    # asyncio.run(main_func())
