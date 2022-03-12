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
        if data := self.reader.tick():
            btn, release, reverse = data
            layout = self.config.layout[self.layout]
            cmd = layout.controls[btn.group][btn.key]
            if not cmd:
                return
            logger.info('Command found: %s', cmd)
            if type(cmd) is Button:
                cmd.action.act(self.controller, release)
            if type(cmd) is Rotating:
                act = cmd.reverse if reverse else cmd.action
                act.act(self.controller, release)
