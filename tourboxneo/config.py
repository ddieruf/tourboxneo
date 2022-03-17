import logging
import toml
from pathlib import Path

from .actions import library

logger = logging.getLogger(__name__)


class ButtonCfg:

    def __init__(self, name, data):
        self.name = name
        action_str = data if type(data) is str else data['action']
        self.action = library.lookup(action_str)
        self.kind = None if type(data) is str else data['kind']

        if self.action is None:
            raise RuntimeError('bad action in ' + name)
        if self.kind not in [None, 'release', 'hold']:
            raise RuntimeError('bad kind in ' + name)

    def __repr__(self):
        return f'ButtonCfg(name={self.name}, action={self.action}, kind={self.kind})'


class DialCfg:

    def __init__(self, name, data):
        self.name = name
        if type(data) is str:
            if '/' in data:
                data_f, data_r = data.split('/', 1)
                self.action = library.lookup(data_f)
                self.reverse = library.lookup(data_r)
            else:
                self.action = library.lookup(data)
                self.reverse = self.action.reverse()
            self.rate = 1
        else:
            self.action = library.lookup(data['action'])
            if data['reverse'] is None:
                self.reverse = self.action.reverse()
            else:
                self.reverse = library.lookup(data['reverse'])
            self.rate = data['rate']

        if self.action is None:
            raise RuntimeError('bad action in ' + name)
        if self.reverse is None:
            raise RuntimeError('bad reverse in ' + name)
        if not (1 <= self.rate <= 5):
            raise RuntimeError('bad rate in ' + name)

    def __repr__(self):
        return f'DialCfg(name={self.name}, action={self.action}, reverse={self.reverse}, rate={self.rate})'


class Layout:
    controls = {
        'prime': {
            'side': ButtonCfg,
            'top': ButtonCfg,
            'tall': ButtonCfg,
            'short': ButtonCfg,
            'top_x2': ButtonCfg,
            'side_x2': ButtonCfg,
            'tall_x2': ButtonCfg,
            'short_x2': ButtonCfg,
            'side_top': ButtonCfg,
            'side_tall': ButtonCfg,
            'side_short': ButtonCfg,
            'top_tall': ButtonCfg,
            'top_short': ButtonCfg,
            'tall_short': ButtonCfg,
        },
        'kit': {
            'tour': ButtonCfg,
            'up': ButtonCfg,
            'down': ButtonCfg,
            'left': ButtonCfg,
            'right': ButtonCfg,
            'c1': ButtonCfg,
            'c2': ButtonCfg,
            'top_up': ButtonCfg,
            'top_down': ButtonCfg,
            'top_left': ButtonCfg,
            'top_right': ButtonCfg,
            'side_up': ButtonCfg,
            'side_down': ButtonCfg,
            'side_left': ButtonCfg,
            'side_right': ButtonCfg,
            'tall_c1': ButtonCfg,
            'tall_c2': ButtonCfg,
            'short_c1': ButtonCfg,
            'short_c2': ButtonCfg,
        },
        'knob': {
            'press': ButtonCfg,
            'turn': DialCfg,
            'side_turn': DialCfg,
            'top_turn': DialCfg,
            'tall_turn': DialCfg,
            'short_turn': DialCfg,
        },
        'scroll': {
            'press': ButtonCfg,
            'turn': DialCfg,
            'side_turn': DialCfg,
            'top_turn': DialCfg,
            'tall_turn': DialCfg,
            'short_turn': DialCfg,
        },
        'dial': {
            'press': ButtonCfg,
            'turn': DialCfg,
        },
    }

    def __init__(self, name, data):
        self.name = name
        self.controls = {
            'prime': {},
            'kit': {},
            'knob': {},
            'scroll': {},
            'dial': {},
        }

        extra_keys = set(
            data.keys()) - {'prime', 'kit', 'knob', 'scroll', 'dial'}
        if len(extra_keys) > 0:
            raise RuntimeError('unexpected keys in layout:' + str(extra_keys))

        for s_name, s_data in data.items():
            for c_name, c_data in s_data.items():
                c = Layout.controls[s_name][c_name]
                self.controls[s_name][c_name] = c(c_name, c_data)


class Shortcut:

    def __init__(self, name, data):
        self.name = name
        self.key = None
        self.shift = False
        self.ctrl = False
        self.alt = False
        self.super = False


class Macro:

    def __init__(self, name, data):
        self.name = name
        self.actions = []


class Menu:

    def __init__(self, name, data):
        self.name = name
        self.entries = None


class Config:

    def __init__(self, data):
        self.name = data['name']
        self.layouts = {}
        self.shortcuts = {}
        self.macros = {}
        self.menus = {}

        if data['name'] is None:
            raise RuntimeError('no name')
        if data['layouts'] is None:
            raise RuntimeError('no layouts')
        if data['layouts']['main'] is None:
            raise RuntimeError('no main layout')
        expected_keys = {'name', 'layouts', 'shortcuts', 'macros', 'menus'}
        extra_keys = set(data.keys()) - expected_keys
        if len(extra_keys) > 0:
            raise RuntimeError('unexpected keys in config:' + str(extra_keys))

        for l_name, l_data in data['layouts'].items():
            layout = Layout(l_name, l_data)
            self.layouts[layout.name] = layout
            # for s_name, section in layout.items():
            #     for key, cmd_str in section.items():
            #         section[key] = library.lookup(cmd_str)

        for s_name, s_data in data['shortcuts'].items():
            shortcut = Shortcut(s_name, s_data)
            self.shortcuts[shortcut.name] = shortcut

        for m_name, m_data in data['macros'].items():
            macro = Macro(m_name, m_data)
            self.macros[macro.name] = macro

        for m_name, m_data in data['menus'].items():
            menu = Menu(m_name, m_data)
            self.menus[menu.name] = menu

    @staticmethod
    def from_file(config_path):
        if config_path is None:
            config_path = Path.home() / '.tourboxneo'
        if not config_path.exists():
            logger.info('falling back on default configuration')
            config_path = Path(__file__).with_name('default.toml')
        if not config_path.exists():
            raise RuntimeError('No default configuration available')

        logger.info('reading %s', config_path.name)

        with config_path.open('r') as config_text:
            data = toml.loads(config_text.read())
            config = Config(data)

        logger.info('loaded %s', config_path.name)

        return config

