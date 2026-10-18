import json
from pynput.keyboard import Key, KeyCode
from data.autoclicker_config import AutoClickerConfig

def load_settings():
    try:
        with open("saves/settings.json", "r") as f:
            settings = json.load(f)
            settings_obj = AutoClickerConfig()

            for key, value in settings.items():
                if key in settings_obj.__dataclass_fields__:
                    if key.endswith("_hotkey"):
                        value = value.strip()
                        if value.startswith("Key."):
                            key_name = value[4:]
                            setattr(settings_obj, key, getattr(Key, key_name))
                        else:
                            setattr(settings_obj, key, KeyCode(char=value))
                    else:
                        setattr(settings_obj, key, value)
            return settings_obj
    except FileNotFoundError:
        return {
            "delay": 1.0,
            "toggle_hotkey": "s",
            "start_record_hotkey": "Key.f9",
            "stop_record_hotkey": "Key.f10",
            "play_macro_hotkey": "Key.f11",
            "delete_macro_hotkey": "Key.f12"
        }
    