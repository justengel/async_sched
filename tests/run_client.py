import asyncio
import async_sched


if __name__ == '__main__':
    async def main():
        async with async_sched.Client('127.0.0.1', 8000) as client:
            s = async_sched.Schedule(seconds=5, repeat=True)
            await client.schedule_command('5 Seconds', s, 'print', s)
            await client.request_schedules()

    asyncio.run(main())
