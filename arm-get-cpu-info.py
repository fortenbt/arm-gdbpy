import gdb

class CpuInfo(gdb.Command):
    def __init__(self):
        super(CpuInfo, self).__init__('get-cpu-info', gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        if len(argv) != 0:
            raise gdb.GdbError('get-cpu-info takes no arguments.')

        pid = gdb.execute('monitor arm mrc 15 0 13 0 0', True, True)
        ttb = gdb.execute('monitor arm mrc 15 0 2 0 0', True, True)

        print 'pid = {0}'.format(pid)
        print 'ttb = 0x{0:X}'.format(int(ttb, 0))

CpuInfo()

