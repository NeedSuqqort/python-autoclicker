import customtkinter as ctk
import time
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, Key
from data.keymap import SPECIAL_KEYS
import threading

class AutoClicker(ctk.CTkFrame):
    def __init__(self, master, get_config, set_config):
        super().__init__(master)
        self.mouse = Controller()
        self.running = False
        self.toggle_hotkey = get_config().toggle_hotkey  # Hotkey to toggle clicking
        self.repeat_key = get_config().autoclicker_repeat_key
        self.toggle_listener = Listener(on_press=self.toggle_by_hotkey)
        self.click_thread = None
        self.get_config = get_config
        self.set_config = set_config

        # Widgets
        self.delay_label = ctk.CTkLabel(
            self,
            text="Delay between clicks (seconds):",
        )
        self.delay_label.pack(pady=(15, 5))

        self.delay_entry = ctk.CTkEntry(
            self,
            width=400,
            height=40
        )
        self.delay_entry.pack(fill="x", padx=20, pady=5)
        self.delay_entry.insert(0, str(self.get_config().delay))
        self.delay_entry.bind("<FocusOut>", lambda e: self.update_delay())

        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Stopped",
            text_color="gray",
        )
        self.status_label.pack(fill="x", padx=20, pady=5)
        self.toggle_button = ctk.CTkButton(
            self,
            text="Start",
            command=self.toggle_clicking,
            width=300,
            height=40
        )
        self.toggle_button.pack(fill="x", padx=20, pady=10)
        self.toggle_listener.start()

        self.click_label = ctk.CTkLabel(
            self,
            text=f"Repeat key: {self.get_config().autoclicker_repeat_key.name.capitalize()} click"
        )

        self.click_label.pack(fill="x", padx=20, pady=5)

        self.click_buttons_frame = ctk.CTkFrame(self)
        self.click_buttons_frame.pack(pady=10)

        self.select_left_click_button = ctk.CTkButton(
            self.click_buttons_frame,
            text="Left click",
            command=lambda: self.set_repeat_key(Button.left),
            width=50,
            height=40
        )

        self.select_middle_click_button = ctk.CTkButton(
            self.click_buttons_frame,
            text="Middle click",
            command=lambda: self.set_repeat_key(Button.middle),
            width=50,
            height=40
        )

        self.select_right_click_button = ctk.CTkButton(
            self.click_buttons_frame,
            text="Right click",
            command=lambda: self.set_repeat_key(Button.right),
            width=50,
            height=40
        )

        self.select_left_click_button.pack(side="left", padx=(0,5))        
        self.select_middle_click_button.pack(side="left", padx=5)        
        self.select_right_click_button.pack(side="left", padx=(5,0))        

        
    def update_delay(self):
        try:
            delay = float(self.delay_entry.get())
            config = self.get_config()
            config.delay = delay
        except ValueError:
            self.delay_entry.delete(0, "end")
            self.delay_entry.insert(0, str(self.get_config().delay))

    def click_loop(self):
        try:
            config = self.get_config()
            delay = config.delay
        except ValueError:
            delay = self.get_config().delay

        while self.running:
            self.mouse.click(config.autoclicker_repeat_key)
            time.sleep(delay)

    def toggle_clicking(self):
        if self.running:
            # Stop
            self.running = False
            if self.click_thread is not None:
                self.click_thread.join(timeout=1.0)
            self.toggle_button.configure(text="Start")
            self.status_label.configure(text="Status: Stopped", text_color="gray")
        else:
            # Start
            self.running = True
            self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
            self.click_thread.start()
            self.toggle_button.configure(text="Stop")
            self.status_label.configure(text="Status: Running", text_color="green")

    def toggle_by_hotkey(self, event):
        # print(event, self.get_config().toggle_hotkey, type(event), type(self.get_config().toggle_hotkey))
        if isinstance(event, Key) and event.name in SPECIAL_KEYS:
            event = SPECIAL_KEYS[event.name]
        if event == self.get_config().toggle_hotkey:
            self.toggle_clicking()

    def set_repeat_key(self, mouse_key):
        config = self.get_config()
        config.autoclicker_repeat_key = mouse_key
        self.set_config(config)
        self.click_label.configure(text=f"Repeat key: {mouse_key.name.capitalize()} click")

    def on_enter(self):
        if self.toggle_listener is None:
            self.toggle_listener = Listener(on_press=self.toggle_by_hotkey)
            self.toggle_listener.start()

    def on_exit(self):
        if self.toggle_listener is not None:
            self.toggle_listener.stop()
        self.toggle_listener = None
    
    def on_destroy(self):
        self.running = False

        if self.click_thread is not None:
            self.click_thread.join(timeout=1.0)

        if self.toggle_listener is not None:
            self.toggle_listener.stop()