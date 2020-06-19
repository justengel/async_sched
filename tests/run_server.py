
import async_sched


if __name__ == '__main__':
    server = async_sched.Scheduler()
    async_sched.set_server(server)  # Set the global server for load.

    server.start('127.0.0.1', 8000)

    @server.register_callback('print')
    async def print_sched(sched):
        print(sched)

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
