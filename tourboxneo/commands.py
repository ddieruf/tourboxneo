from evdev import ecodes as e
import logging

logger = logging.getLogger(__name__)


class Cmd:
    pass


class CmdKey:

    def __init__(self, name, key):
        self.name = name
        self.key = key

    def act(self, controller, release, reverse):
        controller.write(e.EV_KEY, self.key, int(not release))
        controller.syn()


class Cmd2Way(Cmd):

    def __init__(self, name, front, back):
        self.name = name
        self.front = front
        self.back = back

    def act(self, controller, release, reverse):
        pass


class CmdRel(Cmd2Way):

    def __init__(self, name, rel, step):
        self.name = name
        self.rel = rel
        self.step = step

    def act(self, controller, release, reverse):
        step = 0 if release else (-self.step if reverse else self.step)
        controller.write(e.EV_REL, self.rel, step)
        controller.syn()


class CmdMacro(Cmd):

    def __init__(self, name):
        self.name = name

    def act(self, controller, release, reverse):
        pass


class Library:

    def __init__(self):
        self.cmds = []

    def lookup(self, cmd_str):
        for cmd in self.cmds:
            if cmd.name == cmd_str:
                return cmd

    def push(self, cmd):
        self.cmds.append(cmd)


library = Library()

library.push(CmdKey('space', e.KEY_SPACE))

library.push(CmdRel('wheel', e.REL_WHEEL, 1))
library.push(CmdRel('wheel_rev', e.REL_WHEEL, -1))
library.push(CmdRel('hwheel', e.REL_HWHEEL, 1))
library.push(CmdRel('hwheel_rev', e.REL_HWHEEL, -1))
