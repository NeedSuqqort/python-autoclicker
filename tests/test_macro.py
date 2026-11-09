import json
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button

import models.macro as macro_module
from models.macro import MacroApp


class FakeWidget:
    def __init__(self):
        self.configurations = []
        self.value = ""

    def configure(self, **kwargs):
        self.configurations.append(kwargs)

    def set(self, value):
        self.value = value

    def get(self):
        return self.value

    def insert(self, _index, value):
        self.value = value

    def delete(self, _start, _end):
        self.value = ""


def make_macro(**kwargs):
    macro = object.__new__(MacroApp)
    macro.macros = []
    macro.current = []
    macro.save_path = Path(kwargs.get("save_path", "macros.json"))
    macro.prev = 0.0
    macro.recording = False
    macro.recording_name = ""
    macro.event_lock = threading.Lock()
    macro.playing_lock = threading.Lock()
    macro.is_repeat = False
    macro.repeat_times = 1
    macro.macro_options = {}
    macro.macro_menu = FakeWidget()
    macro.play_button = FakeWidget()
    macro.delete_button = FakeWidget()
    macro.record_button = FakeWidget()
    macro.name_entry = FakeWidget()
    macro.stop_button = FakeWidget()
    macro.status_label = FakeWidget()
    return macro


def test_key_records_round_trip_characters_and_special_keys():
    char_record = MacroApp.get_key_from_keycode(KeyCode(char="a"))
    special_record = MacroApp.get_key_from_keycode(Key.esc)

    assert char_record == {"kind": "char", "value": "a"}
    assert special_record == {"kind": "special", "value": "esc"}
    assert MacroApp.get_keycode_from_key(char_record) == KeyCode(char="a")
    assert MacroApp.get_keycode_from_key(special_record) is Key.esc


def test_key_record_rejects_unknown_kind():
    with pytest.raises(ValueError, match="Unknown key record kind"):
        MacroApp.get_keycode_from_key({"kind": "unknown", "value": "x"})


def test_append_event_records_event_data_and_elapsed_delay(monkeypatch):
    times = iter((1.5, 2.0, 3.25))
    monkeypatch.setattr(macro_module.time, "time", lambda: next(times))
    macro = make_macro()
    macro.prev = 1.0

    macro.append_event(type="move", x=12, y=34)
    macro.append_event(
        type="click",
        x=12,
        y=34,
        button=Button.left,
        pressed=True,
    )
    macro.append_event(type="key_down", key=KeyCode(char="z"))

    assert macro.current == [
        {"type": "move", "x": 12, "y": 34, "delay": 0.5},
        {
            "type": "click",
            "x": 12,
            "y": 34,
            "button": "left",
            "pressed": True,
            "delay": 0.5,
        },
        {
            "type": "key_down",
            "key": {"kind": "char", "value": "z"},
            "delay": 1.25,
        },
    ]


def test_append_event_rejects_unsupported_event_type():
    macro = make_macro()

    with pytest.raises(ValueError, match="Unsupported event type"):
        macro.append_event(type="unsupported")


def test_create_macro_uses_fallback_name_and_current_events():
    macro = make_macro()
    macro.current = [{"type": "move", "x": 1, "y": 2}]

    created = macro.create_macro()

    assert created == {
        "name": "Macro 1",
        "description": "macro",
        "events": [{"type": "move", "x": 1, "y": 2}],
    }
    assert macro.macros == [created]


def test_load_macro_handles_missing_file_single_object_and_list(tmp_path):
    macro = make_macro(save_path=tmp_path / "macros.json")
    assert macro.load_macro() == []

    macro.save_path.write_text(
        json.dumps({"name": "single", "events": []}),
        encoding="utf-8",
    )
    assert macro.load_macro() == [{"name": "single", "events": []}]

    expected = [{"name": "first"}, {"name": "second"}]
    macro.save_path.write_text(json.dumps(expected), encoding="utf-8")
    assert macro.load_macro() == expected


def test_load_macro_rejects_non_object_or_list_json(tmp_path):
    macro = make_macro(save_path=tmp_path / "macros.json")
    macro.save_path.write_text("42", encoding="utf-8")

    with pytest.raises(ValueError, match="macro object or list"):
        macro.load_macro()


def test_save_macro_persists_macros_as_json(tmp_path):
    macro = make_macro(save_path=tmp_path / "macros.json")
    macro.macros = [{"name": "test", "events": []}]

    macro.save_macro()

    assert json.loads(macro.save_path.read_text(encoding="utf-8")) == macro.macros


def test_refresh_macro_list_disables_actions_when_empty():
    macro = make_macro()

    macro.refresh_macro_list()

    assert macro.macro_menu.value == "No macros yet"
    assert macro.play_button.configurations[-1] == {"state": "disabled"}
    assert macro.delete_button.configurations[-1] == {"state": "disabled"}


def test_refresh_macro_list_clamps_selection_and_enables_actions():
    macro = make_macro()
    macro.macros = [{"name": "first"}, {"name": "second"}]

    macro.refresh_macro_list(selected_index=99)

    assert macro.macro_options == {"1. first": 0, "2. second": 1}
    assert macro.macro_menu.value == "2. second"
    assert macro.play_button.configurations[-1] == {"state": "normal"}
    assert macro.delete_button.configurations[-1] == {"state": "normal"}


def test_repeat_times_accepts_positive_integers_and_restores_invalid_input():
    macro = make_macro()
    macro.repeat_times_entry = FakeWidget()
    macro.repeat_times_entry.value = "3"

    macro.set_repeat_times()
    assert macro.repeat_times == 3

    macro.repeat_times_entry.value = "invalid"
    macro.set_repeat_times()
    assert macro.repeat_times_entry.value == "3"

    macro.repeat_times_entry.value = "0"
    macro.set_repeat_times()
    assert macro.repeat_times == 3


def test_replay_macro_dispatches_mouse_and_keyboard_events(monkeypatch):
    actions = []
    mouse_controller = SimpleNamespace(
        position=None,
        press=lambda button: actions.append(("press", button)),
        release=lambda button: actions.append(("release", button)),
    )
    keyboard_controller = SimpleNamespace(
        press=lambda key: actions.append(("key_down", key)),
        release=lambda key: actions.append(("key_up", key)),
    )
    macro = make_macro()
    macro.mouse_controller = mouse_controller
    macro.keyboard_controller = keyboard_controller
    monkeypatch.setattr(macro_module.time, "sleep", lambda _delay: None)
    events = [
        {"type": "move", "x": 10, "y": 20},
        {"type": "click", "x": 30, "y": 40, "button": "left", "pressed": True},
        {"type": "click", "x": 30, "y": 40, "button": "right", "pressed": False},
        {"type": "key_down", "key": {"kind": "char", "value": "x"}},
        {"type": "key_up", "key": {"kind": "special", "value": "esc"}},
    ]

    macro.replay_macro(events)

    assert mouse_controller.position == (30, 40)
    assert actions == [
        ("press", Button.left),
        ("release", Button.right),
        ("key_down", KeyCode(char="x")),
        ("key_up", Key.esc),
    ]


def test_replay_macro_rejects_unsupported_events():
    macro = make_macro()
    macro.mouse_controller = SimpleNamespace(position=None)
    macro.keyboard_controller = SimpleNamespace()

    with pytest.raises(ValueError, match="Unsupported event type"):
        macro.replay_macro([{"type": "unknown"}])


def test_selected_macro_resolves_menu_value():
    macro = make_macro()
    macro.macro_options = {"1. sample": 0}
    macro.macro_menu.value = "1. sample"

    assert macro.selected_macro("1. sample") == 0
    assert macro.selected_macro_index() == 0
    assert macro.selected_macro("missing") is None
