import json
from types import SimpleNamespace

import pytest
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button

from app import App
from data.autoclicker_config import AutoClickerConfig


class FakePage:
    def __init__(self, events, name):
        self.events = events
        self.name = name

    def on_exit(self):
        self.events.append(f"{self.name}.exit")

    def on_enter(self):
        self.events.append(f"{self.name}.enter")

    def grid_forget(self):
        self.events.append(f"{self.name}.forget")

    def grid(self, **kwargs):
        self.events.append(f"{self.name}.grid")

    def tkraise(self):
        self.events.append(f"{self.name}.raise")


def test_show_page_exits_old_page_and_enters_new_page():
    events = []
    first = FakePage(events, "first")
    second = FakePage(events, "second")
    app = SimpleNamespace(
        pages={"first": first, "second": second},
        current_page="first",
    )

    App.show_page(app, "second")

    assert events == [
        "first.exit",
        "first.forget",
        "second.forget",
        "second.grid",
        "second.raise",
        "second.enter",
    ]
    assert app.current_page == "second"


def test_show_page_rejects_unknown_page():
    app = SimpleNamespace(pages={}, current_page=None)

    with pytest.raises(KeyError):
        App.show_page(app, "missing")


def test_config_change_updates_and_persists_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "saves").mkdir()
    app = object.__new__(App)
    app.config = AutoClickerConfig(
        toggle_hotkey=KeyCode(char="x"),
        start_record_hotkey=Key.esc,
        autoclicker_repeat_key=Button.right,
    )

    App.config_change(app, app.config)

    saved = json.loads((tmp_path / "saves" / "settings.json").read_text())
    assert saved["toggle_hotkey"] == "x"
    assert saved["start_record_hotkey"] == "Key.esc"
    assert saved["autoclicker_repeat_key"] == "Button.right"


def test_get_config_returns_current_config():
    config = AutoClickerConfig(delay=0.5)
    app = SimpleNamespace(config=config)

    assert App.get_config(app) is config
