import customtkinter as ctk
from pynput.keyboard import Key, KeyCode
from data.keymap import SPECIAL_KEYS

class Settings(ctk.CTkFrame):
    def __init__(self, master, get_config, config_change):
        super().__init__(master)
        self.get_config = get_config
        self.config_change_callback = config_change
        self.current_settings = self.get_config()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        for hotkey_name, hotkey_attr in [
            ("Toggle Autoclicker", "toggle_hotkey"),
            ("Start Record Macro", "start_record_hotkey"),
            ("Stop Record Macro", "stop_record_hotkey"),
            ("Play Macro", "play_macro_hotkey"),
            ("Delete Macro", "delete_macro_hotkey"),
        ]:
            self.construct_setting_overlay(hotkey_name, hotkey_attr, getattr(self.get_config(), hotkey_attr))

        self.save_button = ctk.CTkButton(
            self, 
            text="Save Settings", 
            command=self.on_save
        )
        self.save_button.pack(fill="x", padx=20, pady=5)

    def on_save(self):
        self.config_change_callback(self.current_settings)

    def construct_setting_overlay(self, text, attr, current_hotkey=None):
            row = ctk.CTkFrame(self)
            row.pack(fill="x", padx=20, pady=5)
            row.grid_columnconfigure(1, weight=1)

            label = ctk.CTkLabel(
                row,
                text=text,
            )
            label.pack(side="left", padx=(0, 10))

            entry = ctk.CTkEntry(
                row,
                placeholder_text="Press one key",
                width=40,
                height=40,    
                border_color="#cccccc", 
                fg_color=("white", "#2b2b2b"),
                state="readonly",
            )
            entry.pack(side="right", fill="x", expand=True)
            self.selected_hotkey = current_hotkey if current_hotkey is not None else self.get_config().toggle_hotkey
            self._display_hotkey(entry, self.selected_hotkey)
            entry.bind("<KeyPress>", lambda e, attr=attr: self._capture_hotkey(attr, e))
            entry.bind("<FocusIn>", lambda e, attr=attr, entry=entry: self._on_focus(attr, entry))
            entry.bind("<FocusOut>", lambda e, attr=attr, entry=entry: self._on_blur(attr, entry))

            setattr(self, f"{attr}_label", label)  
            setattr(self, f"{attr}_entry", entry)  

    def get_hotkey_display(self, hotkey):
        if isinstance(hotkey, KeyCode):
            return hotkey.char
        else:
            return str(hotkey).replace("Key.", "").replace("_", " ").title()

    def _display_hotkey(self, component, hotkey):
        display = self.get_hotkey_display(hotkey)
        component.configure(state="normal")
        component.delete(0, "end")
        component.insert(0, display)
        component.configure(state="readonly")

    def _on_focus(self, attr, event):
        event.configure(
            border_color="#0ea4df",        
        )

    def _on_blur(self, attr, event):
        event.configure(
            border_color="#cccccc",
            fg_color=("white", "#2b2b2b")
        )

    def _capture_hotkey(self, attr, event):
        keysym = event.keysym.lower()
        if keysym in SPECIAL_KEYS:
            self.selected_hotkey = SPECIAL_KEYS[keysym]
        elif len(event.char) == 1:
            self.selected_hotkey = KeyCode.from_char(event.char)
        else:
            return "break"
        
        setattr(self.current_settings, attr, self.selected_hotkey)
        self._display_hotkey(getattr(self, f"{attr}_entry"), self.selected_hotkey)
        return "break"