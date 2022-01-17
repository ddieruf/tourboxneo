from evdev import UInput, ecodes as e
import logging

from .commands import *

logger = logging.getLogger(__name__)


class Driver:

    def __init__(self, reader, config):
        self.reader_resource = reader
        self.reader = None
        self.config = config
        self.controller = None

    def __enter__(self):
        self.reader = self.reader_resource.__enter__()
        events = {
            e.EV_KEY: e.keys.keys(),
            e.EV_REL: [e.REL_WHEEL, e.REL_HWHEEL]
        }
        self.controller = UInput(events,
                                 name='TourBoxNEO',
                                 vendor=0x0483,
                                 product=0x5740)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.reader_resource.__exit__(exc_type, exc_value, traceback)
        logger.info('Halting TourBoxNEO Driver')

    def tick(self):
        if data := self.reader.tick():
            btn, release, reverse = data
            if cmd := self.config.layouts['main'][btn.group][btn.key]:
                logger.info('Command found: %s', cmd)
                cmd.act(self.controller, release, reverse)
