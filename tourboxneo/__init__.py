from evdev import UInput, ecodes as e
from time import sleep
import logging
import toml

from .reader import Reader
from .config import ButtonCfg, DialCfg

VERSION = '0.3'

logging.basicConfig()
logger = logging.getLogger(__name__)


class Service:
    def __init__(self, config, device):
        self.config = config
        self.device = device
        self.controller = None
        self.layout = 'main'
        self.held = {} # currently held buttons, no dials
        self.counters = {}  # counters for dials

    def __enter__(self):
        logger.info('Starting TourBoxNEO Service')
        self.connect_input()
        self.connect_output()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.reader is not None:
            self.reader.__exit__(exc_type, exc_value, traceback)
        logger.info('Halting TourBoxNEO Service')

    def connect_input(self):
        reader = Reader(self.device)
        self.reader = reader.__enter__()

    def disconnect_input(self, exc_type, exc_value, traceback):
        logger.warn('Input disconnected: %s', exc_value)
        if self.reader is not None:
            self.reader.__exit__(exc_type, exc_value, traceback)
        self.reader = None

    def check_input(self):
        if self.reader is None:
            try:
                self.connect_input()
            except:
                sleep(5)
        return self.reader is not None

    def connect_output(self):
        self.controller = UInput(
            {
                e.EV_KEY: e.keys.keys(),
                e.EV_REL: [e.REL_WHEEL, e.REL_HWHEEL]
            },
            name='TourBoxNEO',
            vendor=0x0483,
            product=0x5740)

    def tick(self):
        if not self.check_input():
            return

        try:
            data = self.reader.tick()
        except RuntimeError as err:
            self.disconnect_input(RuntimeError, err, None)
            return

        if not data:
            return
        btn, release, reverse = data

        if not release:
            layout = self.config.layouts[self.layout]
            cmd = layout.controls[btn.group][btn.key]
            if cmd is None:
                return
            logger.debug('Command pressed: %s', cmd)

            if isinstance(cmd, ButtonCfg):
                if (btn.group, btn.key) in self.held:
                    raise Error('Double hold')
                if cmd.kind == 'tap':
                    cmd.action.press(self.controller)
                    cmd.action.release(self.controller)
                elif cmd.kind == 'release':
                    self.held[(btn.group, btn.key)] = cmd
                elif cmd.kind == 'hold':
                    self.held[(btn.group, btn.key)] = cmd
                    cmd.action.press(self.controller)
            elif isinstance(cmd, DialCfg):
                action = cmd.action if not reverse else cmd.reverse
                action.press(self.controller)
                action.release(self.controller)
            else:
                raise Error('Invalid command')

        else:
            cmd = self.held.pop((btn.group, btn.key), None)
            if cmd is None:
                return
            if not isinstance(cmd, ButtonCfg):
                raise Error('Releasing non-button')
            if cmd.kind == 'tap':
                raise Error('Releasing tap')
            elif cmd.kind == 'release':
                cmd.action.press(self.controller)
                cmd.action.release(self.controller)
            elif cmd.kind == 'hold':
                cmd.action.release(self.controller)
            logger.debug('Command released: %s', cmd)

        self.controller.syn()

        logger.debug('Currently held: %s', self.held)
