from types import SimpleNamespace

from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button

import models.autoclicker as autoclicker_module
from models.autoclicker import AutoClicker


class FakeWidget:
    def __init__(self, value=""):
        self.value = value
        self.configurations = []

    def get(self):
        return self.value

    def delete(self, _start, _end):
        self.value = ""

    def insert(self, _index, value):
        self.value = value

    def configure(self, **kwargs):
        self.configurations.append(kwargs)


def test_update_delay_accepts_numeric_value_and_restores_invalid_input():
    config = SimpleNamespace(delay=1.0)
    clicker = SimpleNamespace(
        delay_entry=FakeWidget("0.125"),
        get_config=lambda: config,
    )

    AutoClicker.update_delay(clicker)
    assert config.delay == 0.125

    clicker.delay_entry.value = "not-a-number"
    AutoClicker.update_delay(clicker)
    assert config.delay == 0.125
    assert clicker.delay_entry.value == "0.125"


def test_click_loop_clicks_with_configured_button_and_delay(monkeypatch):
    clicks = []
    clicker = SimpleNamespace(
        running=True,
        get_config=lambda: SimpleNamespace(
            delay=0.25,
            autoclicker_repeat_key=Button.right,
        ),
        mouse=SimpleNamespace(click=lambda button: clicks.append(button)),
    )

    def stop_after_first_click(_delay):
        clicker.running = False

    monkeypatch.setattr(autoclicker_module.time, "sleep", stop_after_first_click)

    AutoClicker.click_loop(clicker)

    assert clicks == [Button.right]


def test_toggle_clicking_starts_and_stops_worker(monkeypatch):
    started = []

    class FakeThread:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def start(self):
            started.append(self.kwargs)

        def join(self, timeout):
            assert timeout == 1.0

    monkeypatch.setattr(autoclicker_module.threading, "Thread", FakeThread)
    clicker = SimpleNamespace(
        running=False,
        click_thread=None,
        click_loop=lambda: None,
        toggle_button=FakeWidget(),
        status_label=FakeWidget(),
    )

    AutoClicker.toggle_clicking(clicker)
    assert clicker.running is True
    assert clicker.toggle_button.configurations[-1] == {"text": "Stop"}
    assert clicker.status_label.configurations[-1]["text"] == "Status: Running"
    assert len(started) == 1

    AutoClicker.toggle_clicking(clicker)
    assert clicker.running is False
    assert clicker.toggle_button.configurations[-1] == {"text": "Start"}
    assert clicker.status_label.configurations[-1]["text"] == "Status: Stopped"


def test_hotkey_toggles_clicking_for_character_and_mapped_special_key():
    received = []
    clicker = SimpleNamespace(
        get_config=lambda: SimpleNamespace(toggle_hotkey=KeyCode(char="s")),
        toggle_clicking=lambda: received.append("toggle"),
    )

    AutoClicker.toggle_by_hotkey(clicker, KeyCode(char="s"))
    AutoClicker.toggle_by_hotkey(clicker, KeyCode(char="x"))
    assert received == ["toggle"]

    clicker.get_config = lambda: SimpleNamespace(toggle_hotkey=Key.space)
    AutoClicker.toggle_by_hotkey(clicker, Key.space)
    assert received == ["toggle", "toggle"]


def test_set_repeat_key_updates_config_and_label():
    config = SimpleNamespace(autoclicker_repeat_key=Button.left)
    labels = []
    clicker = SimpleNamespace(
        get_config=lambda: config,
        set_config=lambda updated: labels.append(updated),
        click_label=FakeWidget(),
    )

    AutoClicker.set_repeat_key(clicker, Button.middle)

    assert config.autoclicker_repeat_key is Button.middle
    assert labels == [config]
    assert clicker.click_label.configurations[-1]["text"] == "Repeat key: Middle click"
