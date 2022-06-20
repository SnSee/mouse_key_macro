from pynput.keyboard import Key
from pynput.mouse import Button

# qt 按键码
_qt_transfer_map = {
    16777264: "Key.f1",
    16777265: "Key.f2",
    16777266: "Key.f3",
    16777267: "Key.f4",
    16777268: "Key.f5",
    16777269: "Key.f6",
    16777270: "Key.f7",
    16777271: "Key.f8",
    16777272: "Key.f9",
    16777273: "Key.f10",
    16777274: "Key.f11",
    16777275: "Key.f12",
    16777217: "Key.tab",
    16777252: "Key.caps_lock",
    16777248: "Key.shift",
    16777249: "Key.ctrl_l",
    16777251: "Key.alt_l",
    16777220: "Key.enter"
}

_pynput_key_map = {
    "Key.alt": Key.alt,
    "Key.alt_l": Key.alt_l,
    "Key.alt_r": Key.alt_r,
    "Key.alt_gr": Key.alt_gr,
    "Key.backspace": Key.backspace,
    "Key.caps_lock": Key.caps_lock,
    "Key.cmd": Key.cmd,
    "Key.cmd_l": Key.cmd_l,
    "Key.cmd_r": Key.cmd_r,
    "Key.ctrl": Key.ctrl,
    "Key.ctrl_l": Key.ctrl_l,
    "Key.ctrl_r": Key.ctrl_r,
    "Key.delete": Key.delete,
    "Key.down": Key.down,
    "Key.end": Key.end,
    "Key.enter": Key.enter,
    "Key.esc": Key.esc,
    "Key.f1": Key.f1,
    "Key.f2": Key.f2,
    "Key.f3": Key.f3,
    "Key.f4": Key.f4,
    "Key.f5": Key.f5,
    "Key.f6": Key.f6,
    "Key.f7": Key.f7,
    "Key.f8": Key.f8,
    "Key.f9": Key.f9,
    "Key.f10": Key.f10,
    "Key.f11": Key.f11,
    "Key.f12": Key.f12,
    "Key.f13": Key.f13,
    "Key.f14": Key.f14,
    "Key.f15": Key.f15,
    "Key.f16": Key.f16,
    "Key.f17": Key.f17,
    "Key.f18": Key.f18,
    "Key.f19": Key.f19,
    "Key.f20": Key.f20,
    "Key.home": Key.home,
    "Key.left": Key.left,
    "Key.page_down": Key.page_down,
    "Key.page_up": Key.page_up,
    "Key.right": Key.right,
    "Key.shift": Key.shift,
    "Key.shift_l": Key.shift_l,
    "Key.shift_r": Key.shift_r,
    "Key.space": Key.space,
    "Key.tab": Key.tab,
    "Key.up": Key.up,
    "Key.media_play_pause": Key.media_play_pause,
    "Key.media_volume_mute": Key.media_volume_mute,
    "Key.media_volume_down": Key.media_volume_down,
    "Key.media_volume_up": Key.media_volume_up,
    "Key.media_previous": Key.media_previous,
    "Key.media_next": Key.media_next
}

# 为方便与pynput联动，按键名称与其一致
_dd_key_map = {
    "Key.esc": 100, "Key.f1": 101, "Key.f2": 102, "Key.f3": 103, "Key.f4": 104, "Key.f5": 105, "Key.f6": 106, "Key.f7": 107, "Key.f8": 108, "Key.f9": 109, "Key.f10": 110, "Key.f11": 111, "Key.f12": 112, "Key.delete": 706,
    "`": 200, "1": 201, "2": 202, "3": 203, "4": 204, "5": 205, "6": 206, "7": 207, "8": 208, "9": 209, "0": 210, "-": 211, "=": 212, "\\": 213, "Key.backspace": 214,
    "Key.tab": 300, "q": 301, "w": 302, "e": 303, "r": 304, "t": 305, "y": 306, "u": 307, "i": 308, "o": 309, "p": 310, "[": 311, "]": 312,
    "Key.caps_lock": 400, "a": 401, "s": 402, "d": 403, "f": 404, "g": 405, "h": 406, "j": 407, "k": 408, "l": 409, ";": 410, "'": 411, "Key.enter": 313,
    "Key.shift": 500, "z": 501, "x": 502, "c": 503, "v": 504, "b": 505, "n": 506, "m": 507, ",": 508, ".": 509, "/": 510, "Key.shift_r": 511,
    "Key.ctrl_l": 600, "Key.cmd": 601, "Key.alt_l": 602, "Key.space": 603, "Key.alt_gr": 604, "Key.ctrl_r": 607,
    "Key.up": 709, "Key.left": 710, "Key.down": 711, "Key.right": 712
}

_pynput_buttons = {
    "Button.left": Button.left,
    "Button.middle": Button.middle,
    "Button.right": Button.right,
}

# ctrl组合键
_pynput_ctrl_key = {
    "<49>": "1", "<50>": "2", "<51>": "3", "<52>": "4", "<53>": "5", "<54>": "6", "<55>": "7", "<56>": "8", "<57>": "9", "<48>": "0", "<189>": "-", "<187>": "=",
    r"\x11": "q", r"\x17": "w", r"\x05": "e", r"\x12": "r", r"\x14": "t", r"\x19": "y", r"\x15": "u", r"\t": "i", r"\x0f": "o", r"\x10": "p",
    r"\x01": "a", r"\x13": "s", r"\x04": "d", r"\x06": "f", r"\x07": "g", r"\x08": "h", r"\n": "j", r"\x0b": "k", r"\x0c": "l",
    r"\x1a": "z", r"\x18": "x", r"\x03": "c", r"\x16": "v", r"\x02": "b", r"\x0e": "n", r"\r": "m",
}

# ctrl-shift组合键
_pynput_ctrl_shift_key = {
    r"\x00": "2", r"\x1e": "6", r"\x1f": "_"
}


def qt_trans_key(key: int):
    return _qt_transfer_map[key]


def pynput_trans_key(key: str):
    return _pynput_key_map[key]


def pynput_key_to_string(key: Key) -> str:
    key_text = str(key)
    if key_text.startswith("'"):
        key_text = key_text[1:-1]
    return _pynput_ctrl_key.get(key_text, _pynput_ctrl_shift_key.get(key_text, key_text))


def pynput_trans_button(button: str):
    return _pynput_buttons[button]


def pynput_standardize_key(key):
    key_text = key if isinstance(key, str) else pynput_key_to_string(key)
    if key_text.startswith("\\") or key_text.startswith("<"):
        return None
    if key_text.startswith("Button") or key_text.startswith("Key"):
        return key
    return key_text


def dd_key_number(key: str):
    return _dd_key_map[key]
