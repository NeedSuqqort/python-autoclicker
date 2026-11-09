from types import SimpleNamespace

from pynput.keyboard import Key, KeyCode

from models.settings import NORMAL, ON_FOCUS, RED, Settings


class FakeEntry:
    def __init__(self):
        self.value = ""
        self.configurations = []

    def configure(self, **kwargs):
        self.configurations.append(kwargs)

    def delete(self, _start, _end):
        self.value = ""

    def insert(self, _index, value):
        self.value = value

def make_settings(config):
    settings = SimpleNamespace(
        current_settings=config,
        get_config=lambda: config,
        selected_hotkey=config.toggle_hotkey,
        get_hotkey_display=lambda hotkey: Settings.get_hotkey_display(
            None, hotkey
        ),
        _set_border_color=lambda widget, color: Settings._set_border_color(
            None, widget, color
        ),
    )
    settings._display_hotkey = lambda component, hotkey: Settings._display_hotkey(
        settings, component, hotkey
    )
    settings.check_duplicates = lambda new_key: Settings.check_duplicates(
        settings, new_key
    )
    for attr in (
        "toggle_hotkey",
        "start_record_hotkey",
        "stop_record_hotkey",
        "play_macro_hotkey",
        "delete_macro_hotkey",
    ):
        setattr(settings, f"{attr}_entry", FakeEntry())
    return settings


def test_hotkey_display_formats_character_and_special_keys():
    assert Settings.get_hotkey_display(None, KeyCode(char="x")) == "x"
    assert Settings.get_hotkey_display(None, Key.f9) == "F9"
    assert Settings.get_hotkey_display(None, Key.page_up) == "Page Up"


def test_capture_hotkey_updates_settings_and_entry():
    config = SimpleNamespace(
        toggle_hotkey=KeyCode(char="s"),
        start_record_hotkey=Key.f9,
        stop_record_hotkey=Key.f10,
        play_macro_hotkey=Key.f11,
        delete_macro_hotkey=Key.f12,
    )
    settings = make_settings(config)
    event = SimpleNamespace(keysym="x", char="x")

    result = Settings._capture_hotkey(settings, "play_macro_hotkey", event)

    assert result == "break"
    assert config.play_macro_hotkey == KeyCode(char="x")
    assert settings.play_macro_hotkey_entry.value == "x"
    assert settings.play_macro_hotkey_entry.configurations[-1]["state"] == "readonly"


def test_capture_duplicate_hotkey_marks_both_entries_red():
    config = SimpleNamespace(
        toggle_hotkey=KeyCode(char="s"),
        start_record_hotkey=Key.f9,
        stop_record_hotkey=Key.f10,
        play_macro_hotkey=Key.f11,
        delete_macro_hotkey=Key.f12,
    )
    settings = make_settings(config)

    Settings._capture_hotkey(
        settings,
        "play_macro_hotkey",
        SimpleNamespace(keysym="s", char="s"),
    )

    assert settings.play_macro_hotkey_entry.configurations[0]["border_color"] == RED
    assert settings.toggle_hotkey_entry.configurations[0]["border_color"] == RED
    assert config.play_macro_hotkey == KeyCode(char="s")


def test_capture_rejects_non_character_key_without_changing_config():
    config = SimpleNamespace(
        toggle_hotkey=KeyCode(char="s"),
        start_record_hotkey=Key.f9,
        stop_record_hotkey=Key.f10,
        play_macro_hotkey=Key.f11,
        delete_macro_hotkey=Key.f12,
    )
    settings = make_settings(config)

    result = Settings._capture_hotkey(
        settings,
        "play_macro_hotkey",
        SimpleNamespace(keysym="unknown", char=""),
    )

    assert result == "break"
    assert config.play_macro_hotkey is Key.f11


def test_focus_and_blur_apply_expected_entry_styles():
    entry = FakeEntry()
    settings = SimpleNamespace(
        _set_border_color=lambda widget, color: Settings._set_border_color(
            None, widget, color
        )
    )

    Settings._on_focus(settings, "play_macro_hotkey", entry)
    assert entry.configurations[-1] == {"border_color": ON_FOCUS}

    Settings._on_blur(settings, "play_macro_hotkey", entry)
    assert entry.configurations[-2] == {"border_color": NORMAL}
    assert entry.configurations[-1] == {"fg_color": ("white", "#2b2b2b")}
