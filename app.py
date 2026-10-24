import threading
import time
import customtkinter as ctk
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, Key, KeyCode
from helper import load_settings
from dataclasses import dataclass
from models.macro import MacroApp 
from models.autoclicker import AutoClicker
from models.settings import Settings
from data.autoclicker_config import AutoClickerConfig
import json

ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Auto Clicker")
        self.root.geometry("600x480")
        self.root.resizable(False, False)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.nav_bar = ctk.CTkFrame(self.root,width=120,corner_radius=0)
        self.nav_bar.grid(row=0, column=0, sticky="ns")
        self.config = load_settings()
        self.current_page = None

        ctk.CTkLabel(
            self.nav_bar,
            text="Menu",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=10)

        # Navigation buttons
        self.btn_autoclicker = ctk.CTkButton(
            self.nav_bar,
            text="Autoclicker",
            command=lambda: self.show_page("autoclicker"),
        )
        self.btn_autoclicker.pack(fill="x", padx=10, pady=5)

        self.btn_macros = ctk.CTkButton(
            self.nav_bar,
            text="Macros",
            command=lambda: self.show_page("macro"),
        )
        self.btn_macros.pack(fill="x", padx=10, pady=5)

        self.btn_settings = ctk.CTkButton(
            self.nav_bar,
            text="Settings",
            command=lambda: self.show_page("settings"),
        )
        self.btn_settings.pack(fill="x", padx=10, pady=5)

        self.content_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        self.autoclicker = AutoClicker(self.content_frame, self.get_config, self.config_change)
        self.settings = Settings(self.content_frame, self.get_config, self.config_change)
        self.macro = MacroApp(self.content_frame, self.config)

        self.pages = {
            "autoclicker": self.autoclicker,
            "settings": self.settings,
            "macro": self.macro
        }
    
        # display the autoclicker page by default
        self.show_page("autoclicker")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    def show_page(self, page):
        try:
            target = self.pages[page]

            if self.current_page is not None and hasattr(self.pages[self.current_page], "on_exit"):
                self.pages[self.current_page].on_exit()

            for p in self.pages.values():
                p.grid_forget()

            target.grid(row=0, column=0, sticky="nsew")
            if hasattr(target, "on_enter"):
                target.on_enter()

            self.current_page = page
           
        except KeyError:
            print("Page not found or initialized")
            raise


    def config_change(self, updated: AutoClickerConfig):
        self.config = updated
        print(f"Config updated: {self.config}")


    def get_config(self):
        return self.config

    def save_config(self):
        with open("saves/settings.json", "w") as f:
            for key, value in self.config.__dict__.items():
                if isinstance(value, Key):
                    self.config.__dict__[key] = f"Key.{value.name}"
                if isinstance(value, KeyCode):
                    self.config.__dict__[key] = value.char
                if isinstance(value, Button):
                    self.config.__dict__[key] = f"Button.{value.name}"
            json.dump(self.config.__dict__, f, indent=4)
        
    def on_close(self):
        for page in self.pages.values():
            if hasattr(page, "on_destroy"):
                page.on_destroy()
        self.save_config()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()
