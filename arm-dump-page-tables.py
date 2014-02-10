import gdb
import struct

L1_DESCRIPTOR_COARSE = 1
L1_DESCRIPTOR_SECTION = 2
L1_DESCRIPTOR_FINE = 3

L2_DESCRIPTOR_LARGE = 1
L2_DESCRIPTOR_SMALL = 2
L2_DESCRIPTOR_TINY = 3

class PageTables(gdb.Command):
    def __init__(self):
        super(PageTables, self).__init__('dump-page-tables', gdb.COMMAND_DATA)


    def _handle_large_page(self, out, ttb_index, l2, pgtbl_index):
        pass

    def _handle_small_page(self, out, ttb_index, l2, pgtbl_index):
        page = ttb_index & 0xfffff000
        vpage = (ttb_index << 20) | (pgtbl_index << 12)
        s = '0x{0:08X},0x{1:08X}'.format(vpage, page)
        b = bytearray(s)
        for x in b: out.append(x)

    def _handle_tiny_page(self, out, ttb_index, l2, pgtbl_index):
        pass

    def _handle_l1_coarse(self, out, anInt, inf, l1, ttb_index):
        pgtbl = inf.read_memory(l1 & 0xfffffc00, 256*4)
        for i in xrange(256):
            l2 = anInt.unpack_from(pgtbl, i*4)
            if not l2: continue

            if l2 & 0x3 == L2_DESCRIPTOR_LARGE:
                self._handle_large_page(out, ttb_index, l2, i*4)
            elif l2 & 0x3 == L2_DESCRIPTOR_SMALL:
                self._handle_small_page(out, ttb_index, l2, i*4)
            elif l2 & 0x3 == L2_DESCRIPTOR_TINY:
                self._handle_tiny_page(out, ttb_index, l2, i*4)
            else:
                raise gdb.GdbError('unknown L2 descriptor value: 0x{0:X}'.format(l2 & 0x3)

    def _dump_page_tables(self, fname, ttb):
        out = []
        anInt = struct.Struct('<I')
        inf = gdb.inferiors()[0]

        ttbl = inf.read_memory(ttb, 4096*4)
        for i in xrange(4096):
            l1 = anInt.unpack_from(ttbl, i*4)
            if not l1: continue

            if l1 & 0x3 == L1_DESCRIPTOR_COARSE:
                self._handle_l1_coarse(out, anInt, inf, l1, i*4)
            elif l1 & 0x3 == L1_DESCRIPTOR_SECTION:
                self._handle_l1_section(out, anInt, inf, l1, i*4)
            elif l1 & 0x3 == L1_DESCRIPTOR_FINE:
                self._handle_l1_fine(out, anInt, inf, l1, i*4)
            else:
                raise gdb.GdbError('unknown L1 descriptor value: 0x{0:X}'.format(l1 & 0x3)

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        if len(argv) != 1:
            raise gdb.GdbError('dump-page-tables <summary-output-filename>')

        ttb = gdb.execute('monitor arm mrc 15 0 2 0 0', True, True)
        ttb = int(ttb, 0)

        print 'ttb = 0x{0:X}'.format(ttb)

        self._dump_page_tables(argv[1], ttb)


PageTables()

