import json
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button
from data.autoclicker_config import AutoClickerConfig

def load_settings():
    try:
        with open("saves/settings.json", "r") as f:
            settings = json.load(f)
            settings_obj = AutoClickerConfig()

            for key, value in settings.items():
                if key in settings_obj.__dataclass_fields__:
                    if key.endswith("key"):
                        value = value.strip()
                        if value.startswith("Key."):
                            key_name = value[4:]
                            setattr(settings_obj, key, getattr(Key, key_name))
                        elif value.startswith("Button."):
                            setattr(settings_obj, key, Button[value.split(".")[-1]])
                        else:
                            setattr(settings_obj, key, KeyCode(char=value))

                    else:
                        setattr(settings_obj, key, value)
            return settings_obj
    except FileNotFoundError:
        print("Unable to load settings. Using default settings...")
        return AutoClickerConfig()