import logging

from .actions import Action
from .reader import MAP

logger = logging.getLogger(__name__)


class Control:
    pass


class ButtonCtrl(Control):
    def __init__(self, name, action, kind):
        self.name = name
        self.action = action
        self.kind = kind

        if self.action is None:
            raise RuntimeError('bad action in ' + name)
        if not isinstance(self.action, Action):
            raise RuntimeError('bad action in ' + name)
        if self.kind not in ['hold', 'up', 'down']:
            raise RuntimeError('bad kind in ' + name)

    def __repr__(self):
        return f'ButtonCtrl(name={self.name}, action={self.action}, kind={self.kind})'


class DialCtrl(Control):
    def __init__(self, name, action, reverse, rate):
        self.name = name
        self.action = action
        self.reverse = reverse
        self.rate = rate

        if self.action is None:
            raise RuntimeError('bad action in ' + name)
        if self.reverse is None:
            raise RuntimeError('bad reverse in ' + name)
        if not isinstance(self.action, Action):
            raise RuntimeError('bad action type in ' + name)
        if not isinstance(self.reverse, Action):
            raise RuntimeError('bad reverse type in ' + name)
        if not (1 <= self.rate <= 5):
            raise RuntimeError('bad rate in ' + name)

    def __repr__(self):
        return f'DialCtrl(name={self.name}, action={self.action}, reverse={self.reverse}, rate={self.rate})'


controls = {
    'prime': {
        'side': ButtonCtrl,
        'top': ButtonCtrl,
        'tall': ButtonCtrl,
        'short': ButtonCtrl,
        'top_x2': ButtonCtrl,
        'side_x2': ButtonCtrl,
        'tall_x2': ButtonCtrl,
        'short_x2': ButtonCtrl,
        'side_top': ButtonCtrl,
        'side_tall': ButtonCtrl,
        'side_short': ButtonCtrl,
        'top_tall': ButtonCtrl,
        'top_short': ButtonCtrl,
        'tall_short': ButtonCtrl,
    },
    'kit': {
        'tour': ButtonCtrl,
        'up': ButtonCtrl,
        'down': ButtonCtrl,
        'left': ButtonCtrl,
        'right': ButtonCtrl,
        'c1': ButtonCtrl,
        'c2': ButtonCtrl,
        'top_up': ButtonCtrl,
        'top_down': ButtonCtrl,
        'top_left': ButtonCtrl,
        'top_right': ButtonCtrl,
        'side_up': ButtonCtrl,
        'side_down': ButtonCtrl,
        'side_left': ButtonCtrl,
        'side_right': ButtonCtrl,
        'tall_c1': ButtonCtrl,
        'tall_c2': ButtonCtrl,
        'short_c1': ButtonCtrl,
        'short_c2': ButtonCtrl,
    },
    'knob': {
        'press': ButtonCtrl,
        'turn': DialCtrl,
        'side_turn': DialCtrl,
        'top_turn': DialCtrl,
        'tall_turn': DialCtrl,
        'short_turn': DialCtrl,
    },
    'scroll': {
        'press': ButtonCtrl,
        'turn': DialCtrl,
        'side_turn': DialCtrl,
        'top_turn': DialCtrl,
        'tall_turn': DialCtrl,
        'short_turn': DialCtrl,
    },
    'dial': {
        'press': ButtonCtrl,
        'turn': DialCtrl,
    },
}

_p = MAP['prime']
clobbers = {
    'prime': {
        'side_top': [_p['side'], _p['top']],
        'side_tall': [_p['side'], _p['tall']],
        'side_short': [_p['side'], _p['short']],
        'top_tall': [_p['top'], _p['tall']],
        'top_short': [_p['top'], _p['short']],
        'tall_short': [_p['tall'], _p['short']],
    },
    'kit': {
        'top_up': [_p['top']],
        'top_down': [_p['top']],
        'top_left': [_p['top']],
        'top_right': [_p['top']],
        'side_up': [_p['side']],
        'side_down': [_p['side']],
        'side_left': [_p['side']],
        'side_right': [_p['side']],
        'tall_c1': [_p['tall']],
        'tall_c2': [_p['tall']],
        'short_c1': [_p['short']],
        'short_c2': [_p['short']],
    },
    'knob': {
        'side_turn': [_p['side']],
        'top_turn': [_p['top']],
        'tall_turn': [_p['tall']],
        'short_turn': [_p['short']],
    },
    'scroll': {
        'side_turn': [_p['side']],
        'top_turn': [_p['top']],
        'tall_turn': [_p['tall']],
        'short_turn': [_p['short']],
    },
    'dial': {},
}
