import customtkinter as ctk
import time
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode
import threading
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
class AutoClicker(ctk.CTkFrame):
    def __init__(self, master, get_config):
        super().__init__(master)
        self.mouse = Controller()
        self.running = False
        self.toggle_hotkey = KeyCode(char='s')  # Hotkey to toggle clicking
        self.toggle_listener = Listener(on_press=self.toggle_by_hotkey)
        self.click_thread = None
        self.get_config = get_config

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
            self.mouse.click(Button.left)
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
        if event == self.get_config().toggle_hotkey:
            self.toggle_clicking()

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