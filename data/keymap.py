from pynput.keyboard import Key, KeyCode

PYNPUT_TO_TKINTER = {
    # Whitespace / editing
    "space": "space",
    "enter": "Return",
    "tab": "Tab",
    "backspace": "BackSpace",
    "delete": "Delete",
    "insert": "Insert",

    # Navigation
    "up": "Up",
    "down": "Down",
    "left": "Left",
    "right": "Right",
    "home": "Home",
    "end": "End",
    "page_up": "Prior",
    "page_down": "Next",

    # Modifiers
    "shift": "Shift_L",
    "shift_l": "Shift_L",
    "shift_r": "Shift_R",
    "ctrl": "Control_L",
    "ctrl_l": "Control_L",
    "ctrl_r": "Control_R",
    "alt": "Alt_L",
    "alt_l": "Alt_L",
    "alt_r": "Alt_R",
    "cmd": "Meta_L",
    "cmd_l": "Meta_L",
    "cmd_r": "Meta_R",

    # Locks
    "caps_lock": "Caps_Lock",
    "num_lock": "Num_Lock",
}

SPECIAL_KEYS = {
    "escape": Key.esc,
    "shift_l": Key.shift,
    "shift_r": Key.shift,
    "control_l": Key.ctrl,
    "control_r": Key.ctrl,
    "return": Key.enter,
    "alt_l": Key.alt,
    "alt_r": Key.alt,
    "space": Key.space,
    "tab": Key.tab,
    "return": Key.enter,
    "backspace": Key.backspace,
    "delete": Key.delete,
    "left": Key.left,
    "right": Key.right,
    "up": Key.up,
    "down": Key.down,
}

def pynput_to_tkinter(key: Key | KeyCode) -> str:
    if isinstance(key, Key):
        name = PYNPUT_TO_TKINTER.get(key.name, key.name)
        if name.startswith("f") and name[1:].isdigit():
            name = name.upper()

        return name

    if isinstance(key, KeyCode) and key.char:
        return key.char

    return str(key)