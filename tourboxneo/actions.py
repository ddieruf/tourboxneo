from evdev import ecodes as e
from copy import copy
import logging
import re

from .menu import Menu, gui_thread

logger = logging.getLogger(__name__)


class Action:
    def __init__(self, name):
        self.name = name

    def with_name(self, name):
        new = copy(self)
        new.name = name
        return new

    def press(self, writer):
        pass

    def release(self, writer):
        pass

    def __repr__(self):
        return f'Action(name={self.name})'


class ActionNone(Action):
    pass


class ActionMod(Action):
    def __init__(self, name, shift=False, ctrl=False, alt=False, cmd=False):
        super().__init__(name)
        self.shift = shift
        self.ctrl = ctrl
        self.alt = alt
        self.cmd = cmd

    def with_mods(self, shift=False, ctrl=False, alt=False, cmd=False):
        new = copy(self)
        new.shift = self.shift or shift
        new.ctrl = self.ctrl or ctrl
        new.alt = self.alt or alt
        new.cmd = self.cmd or cmd
        return new

    def press(self, writer):
        if self.shift:
            writer.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
        if self.ctrl:
            writer.write(e.EV_KEY, e.KEY_LEFTCTRL, 1)
        if self.alt:
            writer.write(e.EV_KEY, e.KEY_LEFTALT, 1)
        if self.cmd:
            writer.write(e.EV_KEY, e.KEY_LEFTMETA, 1)

    def release(self, writer):
        if self.shift:
            writer.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
        if self.ctrl:
            writer.write(e.EV_KEY, e.KEY_LEFTCTRL, 0)
        if self.alt:
            writer.write(e.EV_KEY, e.KEY_LEFTALT, 0)
        if self.cmd:
            writer.write(e.EV_KEY, e.KEY_LEFTMETA, 0)

    def __repr_mods__(self):
        mods = ''
        if self.shift:
            mods += 'S'
        if self.ctrl:
            mods += 'C'
        if self.alt:
            mods += 'A'
        if self.cmd:
            mods += 'D'
        return mods

    def __repr__(self):
        mods = self.__repr_mods__()
        return f'ActionMod(name={self.name}, mods={mods})'


class ActionKey(ActionMod):
    def __init__(self, name, key, **mods):
        super().__init__(name, **mods)
        self.key = key

    def press(self, writer):
        super().press(writer)
        writer.write(e.EV_KEY, self.key, 1)

    def release(self, writer):
        super().release(writer)
        writer.write(e.EV_KEY, self.key, 0)

    def __repr__(self):
        mods = self.__repr_mods__()
        return f'ActionKey(name={self.name}, mods={mods}, key={self.key})'


class ActionRel(ActionMod):
    def __init__(self, name, rel, step, **mods):
        super().__init__(name, **mods)
        self.rel = rel
        self.step = step

    def press(self, writer):
        super().press(writer)
        writer.write(e.EV_REL, self.rel, self.step)

    def release(self, writer):
        super().release(writer)
        writer.write(e.EV_REL, self.rel, 0)

    def reverse(self):
        a = copy(self)
        a.step = -self.step
        return a

    def __repr__(self):
        mods = self.__repr_mods__()
        return f'ActionKey(name={self.name}, mods={mods}, rel={self.rel}, step={self.step})'


class ActionMacro(Action):
    def __init__(self, name, actions):
        super().__init__(name)
        self.actions = actions

    def press(self, writer):
        super().press(writer)
        for action in self.actions:
            action.press(writer)
            action.release(writer)

    def release(self, writer):
        super().release(writer)

    def __repr__(self):
        return f'ActionMacro(name={self.name})'


class ActionMenu(Action):
    def __init__(self, name, entries):
        super().__init__(name)
        self.entries = entries

    def press(self, writer):
        super().press(writer)
        start_tk(Menu())

    def release(self, writer):
        super().release(writer)

    def __repr__(self):
        return f'ActionMenu(name={self.name})'


split_mod_re = re.compile('^([SCMAD])-')


def split_mods(cmd_str):
    mods = None
    while m := split_mod_re.match(cmd_str):
        mods = mods or {}
        cmd_str = cmd_str[2:]
        match = m.group(0)
        if match == 'S-':
            mods['shift'] = True
        elif match == 'C-':
            mods['ctrl'] = True
        elif match == 'M-' or match == 'A-':
            mods['alt'] = True
        elif match == 'D-':
            mods['cmd'] = True
    return mods, cmd_str


def split_reverse(cmd_str):
    rev = cmd_str.endswith('-')
    cmd_str = cmd_str.rstrip('-+')
    return rev, cmd_str


class Library:
    def __init__(self):
        self.cmds = {}
        library_defaults(self)

    def lookup(self, cmd_str):
        mods, cmd_str = split_mods(cmd_str)
        rev, cmd_str = split_reverse(cmd_str)
        cmd = self.cmds[cmd_str]
        if isinstance(cmd, ActionMod) and mods:
            cmd = cmd.with_mods(**mods)
        if isinstance(cmd, ActionRel) and rev:
            cmd = cmd.reverse()
        return cmd

    def push(self, cmd):
        if cmd.name in self.cmds:
            raise RuntimeError(f'duplicate key: {cmd.name}')
        self.cmds[cmd.name] = cmd

    def alias(self, alias, name):
        self.cmds[alias] = self.cmds[name]


def library_defaults(library):
    library.push(ActionNone('none'))

    library.push(ActionKey('esc', e.KEY_ESC))
    library.push(ActionKey('backspace', e.KEY_ESC))
    library.push(ActionKey('delete', e.KEY_DELETE))
    library.push(ActionKey('insert', e.KEY_INSERT))

    library.push(ActionKey('up', e.KEY_UP))
    library.push(ActionKey('down', e.KEY_DOWN))
    library.push(ActionKey('left', e.KEY_LEFT))
    library.push(ActionKey('right', e.KEY_RIGHT))
    library.push(ActionKey('home', e.KEY_HOME))
    library.push(ActionKey('end', e.KEY_END))
    library.push(ActionKey('pageup', e.KEY_PAGEUP))
    library.push(ActionKey('pagedown', e.KEY_PAGEDOWN))

    library.push(ActionKey('lshift', e.KEY_LEFTSHIFT))
    library.alias('shift', 'lshift')
    library.push(ActionKey('lctrl', e.KEY_LEFTCTRL))
    library.alias('ctrl', 'lctrl')
    library.push(ActionKey('lalt', e.KEY_LEFTALT))
    library.alias('alt', 'lalt')
    library.push(ActionKey('lcmd', e.KEY_LEFTMETA))
    library.alias('cmd', 'lcmd')
    library.push(ActionKey('rshift', e.KEY_RIGHTSHIFT))
    library.push(ActionKey('rctrl', e.KEY_RIGHTCTRL))
    library.push(ActionKey('ralt', e.KEY_RIGHTALT))
    library.push(ActionKey('rcmd', e.KEY_RIGHTMETA))

    library.push(ActionKey('space', e.KEY_SPACE))
    library.push(ActionKey('tab', e.KEY_TAB))
    library.push(ActionKey('enter', e.KEY_ENTER))

    library.push(ActionKey('1', e.KEY_1))
    library.push(ActionKey('2', e.KEY_2))
    library.push(ActionKey('3', e.KEY_3))
    library.push(ActionKey('4', e.KEY_4))
    library.push(ActionKey('5', e.KEY_5))
    library.push(ActionKey('6', e.KEY_6))
    library.push(ActionKey('7', e.KEY_7))
    library.push(ActionKey('8', e.KEY_8))
    library.push(ActionKey('9', e.KEY_9))
    library.push(ActionKey('0', e.KEY_0))

    library.push(ActionKey('exclaim', e.KEY_1, shift=True))
    library.alias('!', 'exclaim')
    library.push(ActionKey('at', e.KEY_2, shift=True))
    library.alias('@', 'at')
    library.push(ActionKey('hash', e.KEY_3, shift=True))
    library.alias('#', 'hash')
    library.push(ActionKey('dollar', e.KEY_4, shift=True))
    library.alias('$', 'dollar')
    library.push(ActionKey('percent', e.KEY_5, shift=True))
    library.alias('%', 'percent')
    library.push(ActionKey('carat', e.KEY_6, shift=True))
    library.alias('^', 'carat')
    library.push(ActionKey('ampersand', e.KEY_7, shift=True))
    library.alias('&', 'ampersand')
    library.push(ActionKey('asterisk', e.KEY_8, shift=True))
    library.alias('*', 'asterisk')
    library.push(ActionKey('leftparen', e.KEY_9, shift=True))
    library.alias('(', 'leftparen')
    library.push(ActionKey('rightparen', e.KEY_0, shift=True))
    library.alias(')', 'rightparen')

    library.push(ActionKey('a', e.KEY_A))
    library.push(ActionKey('b', e.KEY_B))
    library.push(ActionKey('c', e.KEY_C))
    library.push(ActionKey('d', e.KEY_D))
    library.push(ActionKey('e', e.KEY_E))
    library.push(ActionKey('f', e.KEY_F))
    library.push(ActionKey('g', e.KEY_G))
    library.push(ActionKey('h', e.KEY_H))
    library.push(ActionKey('i', e.KEY_I))
    library.push(ActionKey('j', e.KEY_J))
    library.push(ActionKey('k', e.KEY_K))
    library.push(ActionKey('l', e.KEY_L))
    library.push(ActionKey('m', e.KEY_M))
    library.push(ActionKey('n', e.KEY_N))
    library.push(ActionKey('o', e.KEY_O))
    library.push(ActionKey('p', e.KEY_P))
    library.push(ActionKey('q', e.KEY_Q))
    library.push(ActionKey('r', e.KEY_R))
    library.push(ActionKey('s', e.KEY_S))
    library.push(ActionKey('t', e.KEY_T))
    library.push(ActionKey('u', e.KEY_U))
    library.push(ActionKey('v', e.KEY_V))
    library.push(ActionKey('w', e.KEY_W))
    library.push(ActionKey('x', e.KEY_X))
    library.push(ActionKey('y', e.KEY_Y))
    library.push(ActionKey('z', e.KEY_Z))

    library.push(ActionKey('minus', e.KEY_MINUS))
    library.alias('-', 'minus')
    library.push(ActionKey('equal', e.KEY_EQUAL))
    library.alias('=', 'equal')
    library.push(ActionKey('leftbrace', e.KEY_LEFTBRACE))
    library.alias('[', 'leftbrace')
    library.push(ActionKey('rightbrace', e.KEY_RIGHTBRACE))
    library.alias(']', 'rightbrace')
    library.push(ActionKey('semicolon', e.KEY_SEMICOLON))
    library.alias(';', 'semicolon')
    library.push(ActionKey('apostrophe', e.KEY_APOSTROPHE))
    library.alias('\'', 'apostrophe')
    library.push(ActionKey('grave', e.KEY_GRAVE))
    library.alias('`', 'grave')
    library.push(ActionKey('backslash', e.KEY_BACKSLASH))
    library.alias('\\', 'backslash')
    library.push(ActionKey('comma', e.KEY_COMMA))
    library.alias(',', 'comma')
    library.push(ActionKey('dot', e.KEY_DOT))
    library.alias('.', 'dot')
    library.push(ActionKey('slash', e.KEY_SLASH))
    library.alias('/', 'slash')

    library.push(ActionKey('underscore', e.KEY_MINUS, shift=True))
    library.alias('_', 'underscore')
    library.push(ActionKey('plus', e.KEY_EQUAL, shift=True))
    library.alias('+', 'plus')
    library.push(ActionKey('leftcurly', e.KEY_LEFTBRACE, shift=True))
    library.alias('{', 'leftcurly')
    library.push(ActionKey('rightcurly', e.KEY_RIGHTBRACE, shift=True))
    library.alias('}', 'rightcurly')
    library.push(ActionKey('colon', e.KEY_SEMICOLON, shift=True))
    library.alias(':', 'colon')
    library.push(ActionKey('quote', e.KEY_APOSTROPHE, shift=True))
    library.alias('"', 'quote')
    library.push(ActionKey('tilde', e.KEY_GRAVE, shift=True))
    library.alias('~', 'tilde')
    library.push(ActionKey('pipe', e.KEY_BACKSLASH, shift=True))
    library.alias('|', 'pipe')
    library.push(ActionKey('leftangle', e.KEY_COMMA, shift=True))
    library.alias('lt', 'leftangle')
    library.alias('<', 'leftangle')
    library.push(ActionKey('rightangle', e.KEY_DOT, shift=True))
    library.alias('gt', 'rightangle')
    library.alias('>', 'rightangle')
    library.push(ActionKey('question', e.KEY_SLASH, shift=True))
    library.alias('?', 'question')

    library.push(ActionKey('kp1', e.KEY_KP1))
    library.push(ActionKey('kp2', e.KEY_KP2))
    library.push(ActionKey('kp3', e.KEY_KP3))
    library.push(ActionKey('kp4', e.KEY_KP4))
    library.push(ActionKey('kp5', e.KEY_KP5))
    library.push(ActionKey('kp6', e.KEY_KP6))
    library.push(ActionKey('kp7', e.KEY_KP7))
    library.push(ActionKey('kp8', e.KEY_KP8))
    library.push(ActionKey('kp9', e.KEY_KP9))
    library.push(ActionKey('kp0', e.KEY_KP0))
    library.push(ActionKey('kpslash', e.KEY_KPSLASH))
    library.push(ActionKey('kpasterisk', e.KEY_KPASTERISK))
    library.push(ActionKey('kpminus', e.KEY_KPMINUS))
    library.push(ActionKey('kpplus', e.KEY_KPPLUS))
    library.push(ActionKey('kpdot', e.KEY_KPDOT))
    library.push(ActionKey('kpenter', e.KEY_KPENTER))

    library.push(ActionKey('kpplusminus', e.KEY_KPPLUSMINUS))
    library.push(ActionKey('kpcomma', e.KEY_KPCOMMA))
    library.push(ActionKey('kpleftparen', e.KEY_KPLEFTPAREN))
    library.push(ActionKey('kprightparen', e.KEY_KPRIGHTPAREN))

    library.push(ActionKey('capslock', e.KEY_CAPSLOCK))
    library.push(ActionKey('numlock', e.KEY_NUMLOCK))
    library.push(ActionKey('scrolllock', e.KEY_SCROLLLOCK))

    library.push(ActionKey('f1', e.KEY_F1))
    library.push(ActionKey('f2', e.KEY_F2))
    library.push(ActionKey('f3', e.KEY_F3))
    library.push(ActionKey('f4', e.KEY_F4))
    library.push(ActionKey('f5', e.KEY_F5))
    library.push(ActionKey('f6', e.KEY_F6))
    library.push(ActionKey('f7', e.KEY_F7))
    library.push(ActionKey('f8', e.KEY_F8))
    library.push(ActionKey('f9', e.KEY_F9))
    library.push(ActionKey('f10', e.KEY_F10))
    library.push(ActionKey('f11', e.KEY_F11))
    library.push(ActionKey('f12', e.KEY_F12))

    library.push(ActionKey('f13', e.KEY_F13))
    library.push(ActionKey('f14', e.KEY_F14))
    library.push(ActionKey('f15', e.KEY_F15))
    library.push(ActionKey('f16', e.KEY_F16))
    library.push(ActionKey('f17', e.KEY_F17))
    library.push(ActionKey('f18', e.KEY_F18))
    library.push(ActionKey('f19', e.KEY_F19))
    library.push(ActionKey('f20', e.KEY_F20))
    library.push(ActionKey('f21', e.KEY_F21))
    library.push(ActionKey('f22', e.KEY_F22))
    library.push(ActionKey('f23', e.KEY_F23))
    library.push(ActionKey('f24', e.KEY_F24))

    library.push(ActionRel('wheel', e.REL_WHEEL, 1))
    library.push(ActionRel('hwheel', e.REL_HWHEEL, 1))
