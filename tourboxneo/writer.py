from time import sleep
from evdev import UInput, categorize, ecodes as e, AbsInfo
import logging
from .constants import MAPPING, CAP
from evdev import ecodes as e, InputEvent

logger = logging.getLogger(__name__)


class Writer:

    def __init__(self, config):
        self.config = config
        self.controller = None

    def __enter__(self):
        self.controller = UInput(name='TourBox', vendor=0x0483, product=0x5740)

    def __exit__(self):
        logger.debug('Closing TourBox Writer')

    def process(self, input):
        print(input)
        # for m in MAPPING.get(x, []):
        #     self.controller.write(*m)
        # self.controller.syn()
