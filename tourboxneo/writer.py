import logging
import struct
import os
import fcntl
from time import time as now

logger = logging.getLogger(__name__)

EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03
EV_MSC = 0x04
EV_REP = 0x14

UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_SET_RELBIT = 0x40045566
UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502

REL_X = 0x00
REL_Y = 0x01
REL_Z = 0x02
REL_RX = 0x03
REL_RY = 0x04
REL_RZ = 0x05
REL_HWHEEL = 0x06
REL_DIAL = 0x07
REL_WHEEL = 0x08
REL_MISC = 0x09

BUS_USB = 0x03


class UInput:
    def __init__(self):
        if not os.path.exists('/dev/uinput'):
            raise IOError('No uinput module found.')

        uinput = open('/dev/uinput', 'wb')
        fcntl.ioctl(uinput, UI_SET_EVBIT, EV_KEY)
        fcntl.ioctl(uinput, UI_SET_EVBIT, EV_REL)
        fcntl.ioctl(uinput, UI_SET_EVBIT, EV_REP)
        # e.EV_KEY: e.keys.keys(),

        for i in range(256):
            fcntl.ioctl(uinput, UI_SET_KEYBIT, i)
        for i in range(10):
            fcntl.ioctl(uinput, UI_SET_RELBIT, i)

        fmt = '80sHHHHi64i64i64i64i'
        axis = [0] * 64 * 4
        name = b'TourBoxNEO'
        vend = 0x0483
        prod = 0x5740
        dev = struct.pack(fmt, name, BUS_USB, vend, prod, 1, 0, *axis)
        uinput.write(dev)
        uinput.flush() # Without this you may get Errno 22: Invalid argument.

        fcntl.ioctl(uinput, UI_DEV_CREATE)
        #fcntl.ioctl(uinput, UI_DEV_DESTROY)

        self.uinput = uinput

    def cur_time(self):
        integer, fraction = divmod(now(), 1)
        s = int(integer)
        ms = int(fraction * 1e6)
        return s, ms

    def write(self, event, code, value):
        fmt = 'llHHI'
        s, ms = self.cur_time()
        ev = struct.pack(fmt, s, ms, event, code, value)
        self.uinput.write(ev)
        self.uinput.flush()

    def syn(self):
        fmt = 'llHHI'
        s, ms = self.cur_time()
        ev = struct.pack(fmt, s, ms, EV_SYN, 0, 0)
        self.uinput.write(ev)
        self.uinput.flush()
