from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button

from data.autoclicker_config import AutoClickerConfig
from data.keymap import pynput_to_tkinter


def test_config_has_expected_defaults():
    config = AutoClickerConfig()

    assert config.delay == 1.0
    assert config.toggle_hotkey == KeyCode(char="s")
    assert config.start_record_hotkey == Key.f9
    assert config.stop_record_hotkey == Key.f10
    assert config.play_macro_hotkey == Key.f11
    assert config.delete_macro_hotkey == Key.f12
    assert config.autoclicker_repeat_key is Button.left


def test_keymap_converts_special_keys_and_function_keys():
    assert pynput_to_tkinter(Key.space) == "space"
    assert pynput_to_tkinter(Key.enter) == "Return"
    assert pynput_to_tkinter(Key.f9) == "F9"


def test_keymap_converts_character_keys():
    assert pynput_to_tkinter(KeyCode.from_char("x")) == "x"


def test_keymap_stringifies_unknown_or_empty_keys():
    assert pynput_to_tkinter(KeyCode.from_vk(999)) == str(KeyCode.from_vk(999))

