from evdev import ecodes as e, InputEvent

SIDE_BTN_DOWN = b'\x01'
SIDE_BTN_UP = b'\x81'
SIDE_BTN_DOUBLECLICK_DOWN = b'\x33'
SIDE_BTN_DOUBLECLICK_UP = b'\xa1'
TOP_BTN_DOWN = b'\x02'
TOP_BTN_UP = b'\x82'
C1_BTN_DOWN = b'\x22'
C1_BTN_UP = b'\xa2'
C2_BTN_DOWN = b'\x23'
C2_BTN_UP = b'\xa3'
TALL_BTN_DOWN = b'\x00'
TALL_BTN_UP = b'\x80'
SHORT_BTN_DOWN = b'\x03'
SHORT_BTN_UP = b'\x83'
UP_BTN_DOWN = b'\x10'
UP_BTN_UP = b'\x90'
RIGHT_BTN_DOWN = b'\x13'
RIGHT_BTN_UP = b'\x93'
DOWN_BTN_DOWN = b'\x11'
DOWN_BTN_UP = b'\x91'
LEFT_BTN_DOWN = b'\x12'
LEFT_BTN_UP = b'\x92'
SCROLL_UP = b'\x49'
SCROLL_UP_STOP = b'\xc9'
SCROLL_DOWN = b'\x09'
SCROLL_DOWN_STOP = b'\x89'
SCROLL_PRESS_DOWN = b'\x37'
SCROLL_PRESS_UP = b'\xb7'
DIAL_LEFT = b'\x4f'
DIAL_LEFT_STOP = b'\xcf'
DIAL_RIGHT = b'\x0f'
DIAL_RIGHT_STOP = b'\x8f'
DIAL_DOWN = b'\x38'
DIAL_UP = b'\xb8'
KNOB_LEFT = b'\x04'
KNOB_LEFT_STOP = b'\x84'
KNOB_RIGHT = b'\x44'
KNOB_RIGHT_STOP = b'\xc4'
KNOB_DOWN = b'\x37'
KNOB_UP = b'\xb7'
TOUR_BTN_DOWN = b'\x2a'
TOUR_BTN_UP = b'\xaa'

MAPPING = {
    SIDE_BTN_DOWN: [(e.EV_KEY, e.KEY_LEFTMETA, 1)], SIDE_BTN_UP: [(e.EV_KEY, e.KEY_LEFTMETA, 0)],
    TOP_BTN_DOWN: [(e.EV_KEY, e.KEY_LEFTSHIFT, 1)], TOP_BTN_UP: [(e.EV_KEY, e.KEY_LEFTSHIFT, 0)],
    C1_BTN_DOWN: [(e.EV_KEY, e.KEY_LEFTCTRL, 1), (e.EV_KEY, e.KEY_Y, 1)], C1_BTN_UP: [(e.EV_KEY, e.KEY_LEFTCTRL, 0), (e.EV_KEY, e.KEY_Y, 0)],
    C2_BTN_DOWN: [(e.EV_KEY, e.KEY_LEFTCTRL, 1), (e.EV_KEY, e.KEY_LEFTSHIFT, 1), (e.EV_KEY, e.KEY_Y, 1)],
    C2_BTN_UP: [(e.EV_KEY, e.KEY_LEFTCTRL, 0), (e.EV_KEY, e.KEY_LEFTSHIFT, 0), (e.EV_KEY, e.KEY_Y, 0)],
    TALL_BTN_DOWN: [(e.EV_KEY, e.KEY_LEFTALT, 1)], TALL_BTN_UP: [(e.EV_KEY, e.KEY_LEFTALT, 0)],
    SHORT_BTN_DOWN: [(e.EV_KEY, e.KEY_SPACE, 1), (e.EV_KEY, e.KEY_SPACE, 2)], SHORT_BTN_UP: [(e.EV_KEY, e.KEY_SPACE, 0)],
    UP_BTN_DOWN: [(e.EV_KEY, e.KEY_E, 1)], UP_BTN_UP: [(e.EV_KEY, e.KEY_E, 0)],
    RIGHT_BTN_DOWN: [(e.EV_KEY, e.KEY_B, 1)], RIGHT_BTN_UP: [(e.EV_KEY, e.KEY_B, 0)],
    DOWN_BTN_DOWN: [(e.EV_KEY, e.KEY_S, 1)], DOWN_BTN_UP: [(e.EV_KEY, e.KEY_S, 0)],
    LEFT_BTN_DOWN: [(e.EV_KEY, e.KEY_J, 1)], LEFT_BTN_UP: [(e.EV_KEY, e.KEY_J, 0)],
    KNOB_LEFT: [(e.EV_KEY, e.KEY_RIGHTALT, 1), (e.EV_KEY, e.KEY_8, 1)], KNOB_RIGHT: [(e.EV_KEY, e.KEY_RIGHTALT, 1), (e.EV_KEY, e.KEY_9, 1)],
    KNOB_LEFT_STOP: [(e.EV_KEY, e.KEY_RIGHTALT, 0), (e.EV_KEY, e.KEY_8, 0)], KNOB_RIGHT_STOP: [(e.EV_KEY, e.KEY_RIGHTALT, 0), (e.EV_KEY, e.KEY_9, 0)],
    SCROLL_UP: [(e.EV_REL, e.REL_WHEEL, 1)], SCROLL_DOWN: [(e.EV_REL, e.REL_WHEEL, -1)],
  #  SCROLL_UP_STOP: [(e.EV_KEY, e.BTN_4, 0)], SCROLL_DOWN_STOP: [(e.EV_KEY, e.BTN_5, 0)],
    DIAL_LEFT: [(e.EV_REL, e.REL_HWHEEL, -1)], DIAL_RIGHT: [(e.EV_REL, e.REL_HWHEEL, 1)],
  #  DIAL_LEFT_STOP: [(e.EV_REL, e.REL_HWHEEL, 0)], DIAL_RIGHT_STOP: [(e.EV_REL, e.REL_HWHEEL, 0)],
    DIAL_DOWN: [(e.EV_KEY, e.KEY_CONTEXT_MENU, 1)], DIAL_UP: [(e.EV_KEY, e.KEY_CONTEXT_MENU, 0)],
    SCROLL_PRESS_DOWN: [(e.EV_KEY, e.KEY_ZOOMRESET, 1)], SCROLL_PRESS_UP: [(e.EV_KEY, e.KEY_ZOOMRESET, 0)],
    TOUR_BTN_DOWN: [(e.EV_KEY, e.KEY_INSERT, 1)], TOUR_BTN_UP: [(e.EV_KEY, e.KEY_INSERT, 0)]
}

CAP = {
    e.EV_KEY: [
        e.KEY_LEFTMETA, e.KEY_LEFTCTRL, e.KEY_LEFTSHIFT, e.KEY_UNDO, e.KEY_REDO, e.KEY_LEFTALT, e.KEY_RIGHTALT, e.KEY_SPACE,
        e.KEY_Y, e.KEY_E, e.KEY_S, e.KEY_J, e.KEY_B, e.KEY_8, e.KEY_9, e.KEY_ZOOMRESET, e.KEY_CONTEXT_MENU, e.KEY_INSERT
    ],
    e.EV_REL: [
        e.REL_WHEEL, e.REL_HWHEEL
    ]
}