import sys
import async_sched

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("asyncio").setLevel(logging.DEBUG)


if __name__ == '__main__':
    # server = async_sched.Scheduler(logger=logger)
    server = async_sched.Scheduler()
    # server.set_debug(True)
    async_sched.set_server(server)  # Set the global server for load.

    server.start('127.0.0.1', 8000)

    @server.register_callback('print')
    async def print_sched(sched):
        print(sched)

    async def raise_err(*args, **kwargs):
        raise ValueError('Invalid value given!')

    server.add('Error', async_sched.RepeatSchedule(seconds=5), raise_err)

    # sched = async_sched.Schedule(seconds=1)
    # server.add('Second', sched, print_sched, sched)
    #
    # sched = async_sched.Schedule(seconds=2)
    # server.add('2 Second', sched, print_sched, sched)
    #
    sched = async_sched.Schedule(seconds=3, repeat=True)
    server.add('3 Second', sched, print_sched, sched)

    # server.loop.call_later(2, server.stop)
    server.run_forever()
