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

    def press(self, cmd):
        if type(cmd) is Button:
            cmd.action.press(self.controller, release)
        elif type(cmd) is Rotating:
            act = cmd.reverse if reverse else cmd.action
            act.press(self.controller)

    def release(self, cmd):
        if type(cmd) is Button:
            cmd.action.release(self.controller)
        elif type(cmd) is Rotating:
            act = cmd.reverse if reverse else cmd.action
            act.press(self.controller)

    def tick(self):
        data = self.reader.tick()
        if not data:
            return
        btn, release, reverse = data

        if release:
            held = []
            for h in self.held:
                group, key, cmd = h
                if btn.group == group and btn.key == key:
                    self.release(cmd)
                    logger.info('Command released: %s', cmd)
                else:
                    held.push(h)
            self.held = held
            return

        layout = self.config.layout[self.layout]
        cmd = layout.controls[btn.group][btn.key]
        if not cmd:
            return

        logger.info('Command found: %s', cmd)

        self.held.push((btn.group, btn.key, cmd))
        self.press(cmd)
