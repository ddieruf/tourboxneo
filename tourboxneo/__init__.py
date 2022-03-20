from evdev import UInput, ecodes as e
from evdev.device import KbdInfo
from time import sleep
import logging
import toml

from .actions import ActionNone
from .reader import Reader
from .controls import ButtonCtrl, DialCtrl, clobbers

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
                e.EV_REL: [e.REL_WHEEL, e.REL_HWHEEL],
            },
            name='TourBoxNEO',
            vendor=0x0483,
            product=0x5740)

    def clobber(self, btn):
        cbs = clobbers[btn.group].get(btn.key, None)
        if cbs is None:
            return
        for c in cbs:
            self.release(c)

    def press(self, btn, reverse):
        layout = self.config.layouts[self.layout]
        cmd = layout.controls[btn.group][btn.key]
        if cmd is None or isinstance(cmd, ActionNone):
            return
        logger.debug('Command found: %s', cmd)

        self.clobber(btn)

        if isinstance(cmd, ButtonCtrl):
            if (btn.group, btn.key) in self.held:
                raise Error('Double hold')
            if cmd.kind == 'hold':
                self.held[(btn.group, btn.key)] = cmd
                cmd.action.press(self.controller)
                logger.debug('Hold starts: %s', cmd.action)
            elif cmd.kind == 'up':
                self.held[(btn.group, btn.key)] = cmd
            elif cmd.kind == 'down':
                cmd.action.press(self.controller)
                cmd.action.release(self.controller)
                logger.debug('Down triggers: %s', cmd.action)
        elif isinstance(cmd, DialCtrl):
            action = cmd.action if not reverse else cmd.reverse
            action.press(self.controller)
            action.release(self.controller)
            logger.debug('Dial moves: %s', action)
        else:
            raise Error('Invalid command')

    def release(self, btn):
        cmd = self.held.pop((btn.group, btn.key), None)
        if cmd is None:
            return
        if not isinstance(cmd, ButtonCtrl):
            raise Error('Releasing non-button')
        if cmd.kind == 'hold':
            cmd.action.release(self.controller)
            logger.debug('Hold ends: %s', cmd.action)
        elif cmd.kind == 'up':
            cmd.action.press(self.controller)
            cmd.action.release(self.controller)
            logger.debug('Up triggers: %s', cmd.action)
        elif cmd.kind == 'down':
            raise Error('Releasing down button')


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
            self.press(btn, reverse)
        else:
            self.release(btn)

        self.controller.syn()
