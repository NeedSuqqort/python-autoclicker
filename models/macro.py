import json
import threading
import time
from pathlib import Path

import customtkinter as ctk
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button, Controller as MouseController
from data.keymap import pynput_to_tkinter

class MacroApp(ctk.CTkFrame):
    def __init__(self, master, config):
        super().__init__(master, corner_radius=12)
        self.macros = []
        self.current = []
        self.save_path = Path(__file__).parent.parent / "saves" / "macros.json"
        self.prev = time.time()
        self.recording = False
        self.is_playing = False
        self.recording_name = ""
        self.mouse_listener = None
        self.keyboard_listener = None
        self.event_lock = threading.Lock()
        self.mouse_controller = MouseController()
        self.keyboard_controller = KeyboardController()
        self.config = config
        self.macro_options = {}
        self.hotkey_bindings = []

        self.ui_init()
        try:
            self.macros = self.load_macro()
        except (json.JSONDecodeError, OSError, ValueError) as error:
            self.set_status(f"Could not load macros: {error}", "red")
        self.refresh_macro_list()

    def ui_init(self):
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self,
            text="Macro Recorder",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=24, pady=(24, 6), sticky="w")

        ctk.CTkLabel(
            self,
            text="Record mouse and keyboard actions, then replay them anytime.",
            text_color=("gray40", "gray70"),
        ).grid(row=1, column=0, padx=24, pady=(0, 18), sticky="w")

        self.name_entry = ctk.CTkEntry(
            self,
            placeholder_text="Macro name",
            height=38,
        )
        self.name_entry.grid(row=2, column=0, padx=24, pady=(0, 12), sticky="ew")

        record_controls = ctk.CTkFrame(self, fg_color="transparent")
        record_controls.grid(row=3, column=0, padx=24, pady=4, sticky="ew")
        record_controls.grid_columnconfigure((0, 1), weight=1)

        self.record_button = ctk.CTkButton(
            record_controls,
            text="Start recording",
            command=self.start_recording,
            height=40,
        )
        self.record_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.stop_button = ctk.CTkButton(
            record_controls,
            text="Stop and save",
            command=self.stop_recording,
            state="disabled",
            height=40,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"),
        )
        self.stop_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
            text_color=("gray40", "gray70"),
        )
        self.status_label.grid(row=4, column=0, padx=24, pady=(12, 18), sticky="ew")

        ctk.CTkLabel(
            self,
            text="Saved macros",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=5, column=0, padx=24, pady=(0, 8), sticky="w")

        self.macro_menu = ctk.CTkOptionMenu(
            self,
            values=["No macros yet"],
            command=self.selected_macro,
            height=38,
        )
        self.macro_menu.grid(row=6, column=0, padx=24, pady=(0, 12), sticky="ew")

        saved_controls = ctk.CTkFrame(self, fg_color="transparent")
        saved_controls.grid(row=7, column=0, padx=24, pady=(0, 24), sticky="ew")
        saved_controls.grid_columnconfigure((0, 1), weight=1)

        self.play_button = ctk.CTkButton(
            saved_controls,
            text="Play selected",
            command=self.play_selected,
            state="disabled",
            height=40,
        )
        self.play_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.delete_button = ctk.CTkButton(
            saved_controls,
            text="Delete selected",
            command=self.delete_selected,
            state="disabled",
            height=40,
            fg_color=("#c0392b", "#922b21"),
            hover_color=("#a93226", "#7b241c"),
        )
        self.delete_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")

    def set_status(self, message, color=("gray40", "gray70")):
        self.status_label.configure(text=message, text_color=color)

    def refresh_macro_list(self, selected_index=0):
        self.macro_options = {
            f"{index + 1}. {macro.get('name') or 'Untitled'}": index
            for index, macro in enumerate(self.macros)
        }
        options = list(self.macro_options)
        if not options:
            self.macro_menu.configure(values=["No macros yet"])
            self.macro_menu.set("No macros yet")
            self.play_button.configure(state="disabled")
            self.delete_button.configure(state="disabled")
            return

        self.macro_menu.configure(values=options)
        selected_index = min(max(selected_index, 0), len(options) - 1)
        self.macro_menu.set(options[selected_index])
        self.play_button.configure(state="normal")
        self.delete_button.configure(state="normal")

    def selected_macro(self, choice):
        return self.macro_options.get(choice)

    def selected_macro_index(self):
        return self.macro_options.get(self.macro_menu.get())

    def start_recording(self):
        if self.recording:
            self.stop_recording()
            return 

        self.recording_name = self.name_entry.get().strip()
        if not self.recording_name:
            self.recording_name = f"Macro {len(self.macros) + 1}"

        with self.event_lock:
            self.current = []
            self.prev = time.time()

        try:
            self.mouse_listener = mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click,
            )
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release,
            )
            self.mouse_listener.start()
            self.keyboard_listener.start()
        except (OSError, RuntimeError) as error:
            if self.mouse_listener is not None:
                self.mouse_listener.stop()
            if self.keyboard_listener is not None:
                self.keyboard_listener.stop()
            self.set_status(f"Could not start recording: {error}", "red")
            return

        self.recording = True
        self.record_button.configure(state="disabled")
        self.name_entry.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.set_status("Recording mouse and keyboard actions…", "#d35400")

    def stop_recording(self):
        if not self.recording:
            self.status_label.configure(text="Not currently recording.", text_color="gray")
            return

        self.recording = False
        if self.mouse_listener is not None:
            self.mouse_listener.stop()
            self.mouse_listener.join(timeout=0.5)
        if self.keyboard_listener is not None:
            self.keyboard_listener.stop()
            self.keyboard_listener.join(timeout=0.5)

        with self.event_lock:
            events = list(self.current)
        self.record_button.configure(state="normal")
        self.name_entry.configure(state="normal")
        self.stop_button.configure(state="disabled")

        if not events:
            self.set_status("No actions recorded.", "gray")
            return

        self.create_macro(self.recording_name, events)
        try:
            self.save_macro()
        except OSError as error:
            self.set_status(f"Macro created but could not be saved: {error}", "red")
            self.refresh_macro_list(len(self.macros) - 1)
            return

        self.refresh_macro_list(len(self.macros) - 1)
        self.set_status(
            f"Saved “{self.recording_name}” ({len(events)} actions).",
            "green",
        )

    @staticmethod
    def get_key_from_keycode(key):
        if isinstance(key, KeyCode) and key.char:
            return {"kind": "char", "value": key.char}
        if isinstance(key, Key):
            return {"kind": "special", "value": key.name}
        if isinstance(key, KeyCode) and key.vk is not None:
            return {"kind": "special", "value": f"vk_{key.vk}"}
        return {"kind": "special", "value": str(key)}

    @staticmethod
    def get_keycode_from_key(record):
        kind = record["kind"]
        value = record["value"]
        if kind == "char":
            return KeyCode.from_char(value)
        if kind == "special":
            if value.startswith("vk_"):
                return KeyCode.from_vk(int(value[3:]))
            return getattr(Key, value)
        raise ValueError(f"Unknown key record kind: {kind}")

    def append_event(self, **event_data):
        now = time.time()
        with self.event_lock:
            delay = max(0, now - self.prev)
            self.prev = now

            event_type = event_data["type"]
            if event_type == "move":
                event = {
                    "type": "move",
                    "x": event_data["x"],
                    "y": event_data["y"],
                }
            elif event_type == "click":
                event = {
                    "type": "click",
                    "x": event_data["x"],
                    "y": event_data["y"],
                    "button": event_data["button"].name,
                    "pressed": event_data["pressed"],
                }
            elif event_type in {"key_down", "key_up"}:
                event = {
                    "type": event_type,
                    "key": self.get_key_from_keycode(event_data["key"]),
                }
            else:
                raise ValueError(f"Unsupported event type: {event_type}")

            event["delay"] = delay
            self.current.append(event)

    def create_macro(self, name="", events=None):
        if events is None:
            with self.event_lock:
                events = list(self.current)
        macro = {
            "name": name or f"Macro {len(self.macros) + 1}",
            "description": "macro",
            "events": events,
        }
        self.macros.append(macro)
        return macro

    def save_macro(self):
        with self.save_path.open("w", encoding="utf-8") as file:
            json.dump(self.macros, file, ensure_ascii=False, indent=2)

    def load_macro(self):
        if not self.save_path.exists():
            print("Macro file not found, starting with empty macro list.")
            return []
        with self.save_path.open("r", encoding="utf-8") as file:
            saved_macros = json.load(file)
        if isinstance(saved_macros, dict):
            return [saved_macros]
        if not isinstance(saved_macros, list):
            raise ValueError("The macro file must contain a macro object or list.")
        return saved_macros

    def play_selected(self):
        index = self.selected_macro_index()
        if index is None or self.recording:
            return

        events = self.macros[index].get("events", [])
        self.play_button.configure(state="disabled")
        self.record_button.configure(state="disabled")
        self.set_status("Playing macro…", "#2980b9")
        threading.Thread(
            target=self.run_macro,
            args=(events,),
            daemon=True,
        ).start()
        self.play_button.configure(state="normal")
        self.record_button.configure(state="normal")

    def run_macro(self, events):
        try:
            self.replay_macro(events)
        except (KeyError, TypeError, ValueError, OSError) as error:
            print(f"Error during macro playback: {error}")
            message = f"Playback failed: {error}"
            color = "red"
        else:
            message = "Playback complete."
            color = "green"
        self.after(0, self.play_button.configure, {"state": "normal"})
        self.after(0, self.set_status, message, color)

    def replay_macro(self, events):
        for event in events:
            time.sleep(max(0, event.get("delay", 0)))
            event_type = event["type"]
            if event_type == "move":
                self.mouse_controller.position = (event["x"], event["y"])
            elif event_type == "click":
                self.mouse_controller.position = (event["x"], event["y"])
                button = Button[event["button"]]
                if event.get("pressed", True):
                    self.mouse_controller.press(button)
                else:
                    self.mouse_controller.release(button)
            elif event_type == "key_down" and event.get("key") is not None:
                self.keyboard_controller.press(
                    self.get_keycode_from_key(event["key"])
                )
            elif event_type == "key_up" and event.get("key") is not None:
                self.keyboard_controller.release(
                    self.get_keycode_from_key(event["key"])
                )
            else:
                raise ValueError(f"Unsupported event type: {event_type}")

    def delete_selected(self):
        index = self.selected_macro_index()
        if index is None:
            return
        del self.macros[index]
        try:
            self.save_macro()
        except OSError as error:
            self.set_status(f"Macro deleted but could not update file: {error}", "red")
        else:
            self.set_status("Macro deleted.", "green")
        self.refresh_macro_list(index)

    def on_move(self, x, y):
        self.append_event(type="move", x=x, y=y)

    def on_click(self, x, y, button, pressed):
        self.append_event(
            type="click",
            x=x,
            y=y,
            button=button,
            pressed=pressed,
        )

    def on_press(self, key):
        self.append_event(type="key_down", key=key)

    def on_release(self, key):
        self.append_event(type="key_up", key=key)


    def on_enter(self):
        if self.recording:
            self.stop_recording()

        window = self.winfo_toplevel()
        hotkeys = (
            (self.config.start_record_hotkey, self.start_recording),
            (self.config.stop_record_hotkey, self.stop_recording),
            (self.config.play_macro_hotkey, self.play_selected),
            (self.config.delete_macro_hotkey, self.delete_selected),
        )

        for hotkey, callback in hotkeys:
            sequence = f"<KeyPress-{pynput_to_tkinter(hotkey)}>"

            def handle_hotkey(_event, command=callback):
                command()
                return "break"

            binding_id = window.bind(sequence, handle_hotkey, add="+")
            self.hotkey_bindings.append((sequence, binding_id))

    def on_exit(self):
        if self.recording:
            self.stop_recording()
        self.recording = False

        window = self.winfo_toplevel()
        for sequence, binding_id in self.hotkey_bindings:
            window.unbind(sequence, binding_id)
        self.hotkey_bindings.clear()


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Macro Recorder")
    app.geometry("460x500")
    app.resizable(False, False)
    MacroApp(app).pack(fill="both", expand=True, padx=16, pady=16)
    app.mainloop()
