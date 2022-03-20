import logging
import toml
from pathlib import Path

from .actions import Library
from .controls import ButtonCtrl, DialCtrl, controls

logger = logging.getLogger(__name__)


def parse_button(name, data, library):
    action_str = data if isinstance(data, str) else data['action']
    action = library.lookup(action_str)
    kind = 'hold' if isinstance(data, str) else data['kind']

    if action is None:
        raise RuntimeError('bad action in ' + name)
    if kind not in ['hold', 'up', 'down']:
        raise RuntimeError('bad kind in ' + name)

    return ButtonCtrl(name, action, kind)


def parse_dial(name, data, library):
    if isinstance(data, str):
        if data != '/' and '/' in data:
            data_f, data_r = data.split('/', 1)
            action = library.lookup(data_f)
            reverse = library.lookup(data_r)
        else:
            action = library.lookup(data)
            reverse = action.reverse()
        rate = 1
    else:
        action = library.lookup(data['action'])
        if data['reverse'] is None:
            reverse = action.reverse()
        else:
            reverse = library.lookup(data['reverse'])
        rate = data['rate']

    if action is None:
        raise RuntimeError('bad action in ' + name)
    if reverse is None:
        raise RuntimeError('bad reverse in ' + name)
    if not (1 <= rate <= 5):
        raise RuntimeError('bad rate in ' + name)

    return DialCtrl(name, action, reverse, rate)


class Layout:
    def __init__(self, name, data, library):
        self.name = name
        self.controls = {
            'prime': {},
            'kit': {},
            'knob': {},
            'scroll': {},
            'dial': {},
        }

        extra_keys = set(data.keys()) - set(controls.keys())
        if len(extra_keys) > 0:
            raise RuntimeError('Unexpected keys in layout:' + str(extra_keys))

        for s_name, s_data in data.items():
            for c_name, c_data in s_data.items():
                kind = controls[s_name][c_name]
                if kind == ButtonCtrl:
                    control = parse_button(c_name, c_data, library)
                elif kind == DialCtrl:
                    control = parse_dial(c_name, c_data, library)
                else:
                    raise Error('Bad control kind')
                self.controls[s_name][c_name] = control

    def __repr__(self):
        return f'Layout(name={self.name})'


class Config:
    def __init__(self, data):
        self.name = data['name']
        self.library = Library()
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
        if len(set(data.keys()) - expected_keys) > 0:
            raise RuntimeError('unexpected keys:' + str(data.keys()))

        for s_name, s_data in data['shortcuts'].items():
            self.register_shortcut(s_name, s_data)

        for m_name, m_data in data['macros'].items():
            macro = Macro(m_name, m_data, self.library)
            self.macros[macro.name] = macro

        for m_name, m_data in data['menus'].items():
            menu = Menu(m_name, m_data, self.library)
            self.menus[menu.name] = menu

        for l_name, l_data in data['layouts'].items():
            layout = Layout(l_name, l_data, self.library)
            self.layouts[layout.name] = layout

    def register_shortcut(self, name, data):
        if isinstance(data, str):
            action = self.library.lookup(data)
        else:
            action = self.library.lookup(data['action'])
            expected_keys = {'action', 'shift', 'ctrl', 'alt', 'super'}
            if len(set(data.keys()) - expected_keys) > 0:
                raise RuntimeError('unexpected keys:' + str(data.keys()))
            mods = {'shift', 'ctrl', 'alt', 'super'}
            mod_data = {k: data[k] for k in mods if k in data}
            action = action.with_mods(**mod_data)

        self.shortcuts[name] = action
        self.library.push(action.with_name(name))

    def register_macro(self, name, data):
        pass

    def register_menu(self, name, data):
        if data['entries'] is None:
            raise RuntimeError('no entries')

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
