from evdev import ecodes as e
import re
import copy
import logging

logger = logging.getLogger(__name__)


class Action:

    def __init__(self, name, shift=False, ctrl=False, alt=False, cmd=False):
        self.name = name
        self.shift = shift
        self.ctrl = ctrl
        self.alt = alt
        self.cmd = cmd

    def with_mods(self, shift=False, ctrl=False, alt=False, cmd=False):
        a = copy.copy(self)
        a.shift = self.shift or shift
        a.ctrl = self.ctrl or ctrl
        a.alt = self.alt or alt
        a.cmd = self.cmd or cmd
        return a

    def press(self, controller):
        if self.shift:
            controller.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
        if self.ctrl:
            controller.write(e.EV_KEY, e.KEY_LEFTCTRL, 1)
        if self.alt:
            controller.write(e.EV_KEY, e.KEY_LEFTALT, 1)
        if self.cmd:
            controller.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)

    def release(self, controller):
        if self.shift:
            controller.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
        if self.ctrl:
            controller.write(e.EV_KEY, e.KEY_LEFTCTRL, 0)
        if self.alt:
            controller.write(e.EV_KEY, e.KEY_LEFTALT, 0)
        if self.cmd:
            controller.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)

    def reverse(self):
        return self

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
        return f'Action(name={self.name}, mods={mods})'


class ActionKey(Action):

    def __init__(self, name, key, **mods):
        super().__init__(name, **mods)
        self.key = key

    def press(self, controller):
        super().press(controller)
        controller.write(e.EV_KEY, self.key, 1)
        controller.syn()

    def release(self, controller):
        super().release(controller)
        controller.write(e.EV_KEY, self.key, 0)
        controller.syn()

    def __repr__(self):
        mods = self.__repr_mods__()
        return f'ActionKey(name={self.name}, mods={mods}, key={self.key})'


class ActionRel(Action):

    def __init__(self, name, rel, step, **mods):
        super().__init__(name, **mods)
        self.rel = rel
        self.step = step

    def press(self, controller):
        super().press(controller)
        controller.write(e.EV_REL, self.rel, self.step)
        controller.syn()

    def release(self, controller):
        super().release(controller)
        controller.write(e.EV_REL, self.rel, 0)
        controller.syn()

    def reverse(self):
        a = copy.copy(self)
        a.step = -self.step
        return a

    def __repr__(self):
        mods = self.__repr_mods__()
        return f'ActionKey(name={self.name}, mods={mods}, rel={self.rel}, step={self.step})'


class ActionMacro(Action):

    def __init__(self, name):
        super().__init__(name)

    def press(self, controller):
        super().press(controller)

    def release(self, controller):
        super().release(controller)

    def __repr__(self):
        return f'ActionMacro(name={self.name})'


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
        elif match == 'M-' or m.match == 'A-':
            mods['alt'] = True
        elif match == 'D-':
            mods['cmd'] = True
    return mods, cmd_str


def split_rev(cmd_str):
    rev = cmd_str.endswith('-')
    cmd_str = cmd_str.rstrip('-+')
    return rev, cmd_str


class Library:

    def __init__(self):
        self.cmds = {}

    def lookup(self, cmd_str):
        mods, cmd_str = split_mods(cmd_str)
        rev, cmd_str = split_rev(cmd_str)
        cmd = self.cmds[cmd_str]
        if rev:
            cmd = cmd.reverse()
        if mods:
            cmd = cmd.with_mods(**mods)
        return cmd

    def push(self, cmd):
        self.cmds[cmd.name] = cmd


library = Library()

library.push(Action('none'))

library.push(ActionKey('esc', e.KEY_ESC))
library.push(ActionKey('backspace', e.KEY_ESC))

library.push(ActionKey('up', e.KEY_UP))
library.push(ActionKey('down', e.KEY_DOWN))
library.push(ActionKey('left', e.KEY_LEFT))
library.push(ActionKey('right', e.KEY_RIGHT))
library.push(ActionKey('home', e.KEY_HOME))
library.push(ActionKey('end', e.KEY_END))
library.push(ActionKey('pageup', e.KEY_PAGEUP))
library.push(ActionKey('pagedown', e.KEY_PAGEDOWN))

library.push(ActionKey('shift', e.KEY_LEFTSHIFT))
library.push(ActionKey('ctrl', e.KEY_LEFTCTRL))
library.push(ActionKey('alt', e.KEY_LEFTALT))
library.push(ActionKey('cmd', e.KEY_LEFTMETA))

library.push(ActionKey('space', e.KEY_SPACE))
library.push(ActionKey('tab', e.KEY_TAB))
library.push(ActionKey('enter', e.KEY_ENTER))

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
library.push(ActionKey('-', e.KEY_MINUS))
library.push(ActionKey('equal', e.KEY_EQUAL))
library.push(ActionKey('=', e.KEY_EQUAL))
library.push(ActionKey('leftbrace', e.KEY_LEFTBRACE))
library.push(ActionKey('[', e.KEY_LEFTBRACE))
library.push(ActionKey('rightbrace', e.KEY_RIGHTBRACE))
library.push(ActionKey(']', e.KEY_RIGHTBRACE))
library.push(ActionKey('semicolon', e.KEY_SEMICOLON))
library.push(ActionKey(';', e.KEY_SEMICOLON))
library.push(ActionKey('apostrophe', e.KEY_APOSTROPHE))
library.push(ActionKey('\'', e.KEY_APOSTROPHE))
library.push(ActionKey('grave', e.KEY_GRAVE))
library.push(ActionKey('`', e.KEY_GRAVE))
library.push(ActionKey('backslash', e.KEY_BACKSLASH))
library.push(ActionKey('\\', e.KEY_BACKSLASH))
library.push(ActionKey('comma', e.KEY_COMMA))
library.push(ActionKey(',', e.KEY_COMMA))
library.push(ActionKey('dot', e.KEY_DOT))
library.push(ActionKey('.', e.KEY_DOT))
library.push(ActionKey('slash', e.KEY_SLASH))
library.push(ActionKey('/', e.KEY_SLASH))

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

library.push(ActionRel('wheel', e.REL_WHEEL, 1))
library.push(ActionRel('hwheel', e.REL_HWHEEL, 1))
