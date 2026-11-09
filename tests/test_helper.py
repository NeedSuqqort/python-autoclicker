import json

from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button

from data.autoclicker_config import AutoClickerConfig
from helper import load_settings


def test_load_settings_returns_defaults_when_file_is_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert load_settings() == AutoClickerConfig()


def test_load_settings_parses_hotkeys_mouse_button_and_known_fields(
    tmp_path, monkeypatch
):
    saves = tmp_path / "saves"
    saves.mkdir()
    (saves / "settings.json").write_text(
        json.dumps(
            {
                "delay": 0.25,
                "toggle_hotkey": "Key.esc",
                "start_record_hotkey": "x",
                "autoclicker_repeat_key": "Button.right",
                "unknown_setting": "ignored",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    config = load_settings()

    assert config.delay == 0.25
    assert config.toggle_hotkey is Key.esc
    assert config.start_record_hotkey == KeyCode(char="x")
    assert config.autoclicker_repeat_key is Button.right
    assert not hasattr(config, "unknown_setting")


def test_load_settings_propagates_invalid_json(tmp_path, monkeypatch):
    saves = tmp_path / "saves"
    saves.mkdir()
    (saves / "settings.json").write_text("{", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    try:
        load_settings()
    except json.JSONDecodeError:
        pass
    else:
        raise AssertionError("Invalid JSON should not be silently ignored")

