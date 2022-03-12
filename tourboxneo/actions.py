from evdev import ecodes as e
import logging

logger = logging.getLogger(__name__)


class Action:

    def __init__(self, name):
        self.name = name

    def act(self, controller, release):
        pass

    def reverse(self):
        return self


class ActionKey(Action):

    def __init__(self, name, key):
        super().__init__(name)
        self.key = key

    def act(self, controller, release):
        controller.write(e.EV_KEY, self.key, int(not release))
        controller.syn()


class ActionRel(Action):

    def __init__(self, name, rel, step):
        super().__init__(name)
        self.rel = rel
        self.step = step

    def act(self, controller, release):
        step = 0 if release else self.step
        controller.write(e.EV_REL, self.rel, step)
        controller.syn()

    def reverse(self):
        return ActionRel(self.name, self.rel, -self.step)


class ActionMacro(Action):

    def __init__(self, name):
        super().__init__(name)

    def act(self, controller, release):
        pass


class Library:

    def __init__(self):
        self.cmds = {}

    def lookup(self, cmd_str):
        rev = False
        if cmd_str[-1] == '-':
            rev = True
        if cmd_str[-1] == '+' or cmd_str[-1] == '-':
            cmd_str = cmd_str[0:-1]
        cmd = self.cmds[cmd_str]
        if rev:
            cmd = cmd.reverse()
        return cmd

    def push(self, cmd):
        self.cmds[cmd.name] = cmd


library = Library()

library.push(Action('none'))

library.push(ActionKey('space', e.KEY_SPACE))

library.push(ActionRel('wheel', e.REL_WHEEL, 1))
library.push(ActionRel('hwheel', e.REL_HWHEEL, 1))
