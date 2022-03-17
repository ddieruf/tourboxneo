from evdev import UInput, ecodes as e
import logging
import toml

from .config import Button, Rotating
from .reader import Reader

VERSION = '0.3'

logging.basicConfig()
logger = logging.getLogger(__name__)


class Service:

    def __init__(self, config, device):
        self.config = config
        self.reader = Reader(device)
        self.controller = None
        self.layout = 'main'
        self.held = []

    def __enter__(self):
        logger.info('Starting TourBoxNEO Service')
        self.reader.__enter__()
        self.controller = UInput(
            {
                e.EV_KEY: e.keys.keys(),
                e.EV_REL: [e.REL_WHEEL, e.REL_HWHEEL]
            },
            name='TourBoxNEO',
            vendor=0x0483,
            product=0x5740)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.reader.__exit__(exc_type, exc_value, traceback)
        logger.info('Halting TourBoxNEO Service')

    def tick(self):
        data = self.reader.tick()
        if not data:
            return
        btn, release, reverse = data

        if release:
            held = []
            for h in self.held:
                group, key, act = h
                if btn.group == group and btn.key == key:
                    act.release(self.controller)
                    logger.info('Action released: %s', act)
                else:
                    held.append(h)
            self.held = held
            return

        layout = self.config.layouts[self.layout]
        cmd = layout.controls[btn.group][btn.key]
        if not cmd:
            return

        logger.info('Command found: %s', cmd)
        act = cmd.action if not reverse else cmd.reverse
        self.held.append((btn.group, btn.key, act))
        act.press(self.controller)
