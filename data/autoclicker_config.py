from dataclasses import dataclass
from pynput.keyboard import Key, KeyCode

@dataclass
class AutoClickerConfig:
    delay: float = 1.0
    toggle_hotkey: Key | KeyCode = KeyCode(char='s')
    start_record_hotkey: Key | KeyCode = Key.f9
    stop_record_hotkey: Key | KeyCode = Key.f10
    play_macro_hotkey: Key | KeyCode = Key.f11
    delete_macro_hotkey: Key | KeyCode = Key.f12