import serial
from time import sleep
from evdev import UInput, categorize, ecodes as e, AbsInfo
import logging
from .constants import MAPPING, CAP

logger = logging.getLogger(__name__)

RELEASE_MASK = 0x80


class Button:

    def __init__(self, group, key, down):
        self.group = group
        self.key = key
        self.down = down


BUTTONS = [
    Button('prime', 'tall', 0x00),
    Button('prime', 'side', 0x01),
    Button('prime', 'top', 0x02),
    Button('prime', 'short', 0x03),
    Button('prime', 'side_x2', 0x33),
    Button('knob', 'down', 0x04),
    Button('knob', 'press', 0x37),
    Button('knob', 'up', 0x44),
    Button('dial', 'down', 0x0f),
    Button('dial', 'press', 0x38),
    Button('dial', 'up', 0x4f),
    Button('scroll', 'down', 0x09),
    Button('scroll', 'press', 0x37),  # this must be wrong
    Button('scroll', 'up', 0x49),
    Button('kit', 'up', 0x10),
    Button('kit', 'down', 0x11),
    Button('kit', 'left', 0x12),
    Button('kit', 'right', 0x13),
    Button('kit', 'c1', 0x22),
    Button('kit', 'c2', 0x23),
    Button('kit', 'tour', 0x2a),
]

MAP = {b.down: b for b in BUTTONS}


class Reader:

    def __init__(self, dev_path='/dev/ttyACM0'):
        self.dev_path = dev_path
        self.serial = None

    def __enter__(self):
        self.serial = serial.Serial(self.dev_path, timeout=2)

    def __exit__(self):
        logger.debug('Closing TourBox Reader')

    def tick(self):
        try:
            bs = self.serial.read()
        except serial.SerialException:
            msg = f"Can't read: {self.dev_path}, maybe unplugged or no permission?"
            logging.warning(msg)
            sleep(1)

        btn = MAP[bs[1]]
        kind = 0 if bs[1] & RELEASE_MASK else 1
        return (btn.group, btn.key, kind)

        for m in MAPPING.get(x, []):
            self.controller.write(*m)
        self.controller.syn()
