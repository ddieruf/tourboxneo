from dataclasses import dataclass
from time import sleep
from evdev import UInput, ecodes as e
from pathlib import Path
import serial
import logging

logger = logging.getLogger(__name__)

RELEASE_MASK = 0x80
REVERSE_MASK = 0x40
BUTTON_MASK = ~(RELEASE_MASK | REVERSE_MASK)
UEVENT_PRODUCT = 'PRODUCT=2e3c/5740/200'


@dataclass
class Button:
    group: str
    key: str
    byte: int

    def __repr__(self):
        byte = hex(self.byte)
        return f"Button(group={self.group}, key={self.key}, byte={byte})"


BUTTONS = [
    Button('prime', 'side', 0x01),
    Button('prime', 'top', 0x02),
    Button('prime', 'tall', 0x00),
    Button('prime', 'short', 0x03),
    Button('prime', 'tall_x2', 0x18),
    Button('prime', 'side_x2', 0x21),
    Button('prime', 'top_x2', 0x1f),
    Button('prime', 'short_x2', 0x1c),
    Button('prime', 'side_top', 0x20),
    Button('prime', 'side_tall', 0x1b),
    Button('prime', 'side_short', 0x1e),
    Button('prime', 'top_tall', 0x19),
    Button('prime', 'top_short', 0x1d),
    Button('prime', 'tall_short', 0x1a),
    Button('kit', 'up', 0x10),
    Button('kit', 'down', 0x11),
    Button('kit', 'left', 0x12),
    Button('kit', 'right', 0x13),
    Button('kit', 'c1', 0x22),
    Button('kit', 'c2', 0x23),
    Button('kit', 'tour', 0x2a),
    Button('kit', 'side_up', 0x14),
    Button('kit', 'side_down', 0x15),
    Button('kit', 'side_left', 0x16),
    Button('kit', 'side_right', 0x17),
    Button('kit', 'top_up', 0x2b),
    Button('kit', 'top_down', 0x2c),
    Button('kit', 'top_left', 0x2d),
    Button('kit', 'top_right', 0x2e),
    Button('kit', 'tall_c1', 0x24),
    Button('kit', 'tall_c2', 0x25),
    Button('kit', 'short_c1', 0x39),
    Button('kit', 'short_c2', 0x3a),
    Button('knob', 'press', 0x37),
    Button('knob', 'turn', 0x04),
    Button('knob', 'side_turn', 0x08),
    Button('knob', 'top_turn', 0x07),
    Button('knob', 'tall_turn', 0x05),
    Button('knob', 'short_turn', 0x06),
    Button('scroll', 'press', 0x0a),
    Button('scroll', 'turn', 0x09),
    Button('scroll', 'side_turn', 0x0e),
    Button('scroll', 'top_turn', 0x0d),
    Button('scroll', 'tall_turn', 0x0b),
    Button('scroll', 'short_turn', 0x0c),
    Button('dial', 'press', 0x38),
    Button('dial', 'turn', 0x0f),
]

MAP = {b.byte: b for b in BUTTONS}


class Reader:

    def __init__(self, dev_path):
        if dev_path is not None and not dev_path.exists():
            logger.warn('Specified device does not exist')
            dev_path = None
        if dev_path is None:
            logger.info('Searching for device')
            for d in Path('/sys/class/tty/').glob('*ACM*'):
                uevent = d.joinpath('device/uevent').read_text()
                if UEVENT_PRODUCT in uevent:
                    dev_path = Path('/dev').joinpath(d.name)
                    logger.info('Identified device %s', dev_path)
                    break
        if dev_path is None or not dev_path.exists():
            raise RuntimeError('Could not find a device')

        self.dev_path = dev_path
        self.serial = None

    def __enter__(self):
        self.serial = serial.Serial(str(self.dev_path), timeout=2)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.info('Halting TourBox Reader')

    def tick(self):
        try:
            bs = self.serial.read()
        except serial.SerialException:
            msg = f"Can't read: {self.dev_path}, maybe unplugged or no permission?"
            logging.warn(msg)
            sleep(1)

        if len(bs) > 0:
            b = bs[0]
            btn = MAP.get(b & BUTTON_MASK, None)
            if btn is None:
                logger.warn(f'Unknown byte {hex(b)}')
            release = bool(b & RELEASE_MASK)
            reverse = bool(b & REVERSE_MASK)
            logger.info(f'Read: %s, rel=%s, rev=%s', btn, release, reverse)
            return (btn, release, reverse)
