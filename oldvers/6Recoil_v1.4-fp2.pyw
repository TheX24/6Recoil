import tkinter as tk
from tkinter import ttk
import threading
import ctypes
from pynput import keyboard as kb
import keyboard
import os
import sv_ttk
import configparser  # For configuration
import pydirectinput
import time
import sys

listener_active = False
listener_thread = None
keyboard_listener = None
typing = False

# Configuration Manager
class ConfigManager:
    def __init__(self, config_file="configtxt.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.defaults = {
            "Settings": {
                "rf_enabled": "1",
                "rf_duration": "0.1",
                "rf_interval": "0.1",
            },
            "Messages": {
                "f1": "good luck have fun",
                "f2": "good game well played",
                "f3": "nice try",
                "f4": "nice kill",
                "f5": "nice play",
                "f6": "nice team",
                "f7": "nice thinking",
                "f8": "good one",
                "f9": "good job",
                "f10": "good kill",
                "f11": "good round",
                "f12": "good aim",
            },
        }
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            self.config.read_dict(self.defaults)
            self.save_config()
        else:
            self.config.read(self.config_file)

    def save_config(self):
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)

    def get(self, section, option, fallback=None):
        return self.config.get(section, option, fallback=fallback)

    def set(self, section, option, value):
        if section not in self.config:
            self.config.add_section(section)
        self.config.set(section, option, value)
        self.save_config()

# Initialize configuration
config_manager = ConfigManager()

# Load configuration values
rf_enabled = config_manager.get("Settings", "rf", "0") == "1"
rf_duration = float(config_manager.get("Settings", "rf_duration", "0.1"))
rf_interval = float(config_manager.get("Settings", "rf_interval", "0.1"))
custom_messages = {
    "f1": config_manager.get("Messages", "f1", "good luck have fun"),
    "f2": config_manager.get("Messages", "f2", "good game well played"),
    "f3": config_manager.get("Messages", "f3", "nice try"),
    "f4": config_manager.get("Messages", "f4", "nice kill"),
    "f5": config_manager.get("Messages", "f5", "nice play"),
    "f6": config_manager.get("Messages", "f6", "nice team"),
    "f7": config_manager.get("Messages", "f7", "nice thinking"),
    "f8": config_manager.get("Messages", "f8", "good one"),
    "f9": config_manager.get("Messages", "f9", "good job"),
    "f10": config_manager.get("Messages", "f10", "good kill"),
    "f11": config_manager.get("Messages", "f11", "good round"),
    "f12": config_manager.get("Messages", "f12", "good aim"),
}

def toggle_caps_lock(state):
    if state:
        pydirectinput.press('capslock')
    else:
        pydirectinput.press('capslock')

def is_caps_lock_on():
    return True if ctypes.windll.user32.GetKeyState(0x14) & 1 else False

def is_rf_on():
    return True if rf_enabled == 1 else False

def type_message(message):
    global rf_duration, rf_interval, typing
    was_caps_lock_on = is_caps_lock_on()
    typing = True
    if was_caps_lock_on:
        toggle_caps_lock(False)
    if typing:
        print(f"Typing message: {message}")
        pydirectinput.press('t', duration=rf_duration, _pause=False)
        time.sleep(rf_interval)
        pydirectinput.typewrite(message, interval=rf_interval, duration=rf_duration, _pause=False)
        time.sleep(rf_interval)
        pydirectinput.press('enter', duration=rf_duration, _pause=False)
        print('Typing:', typing)
    typing = False
    if was_caps_lock_on:
        toggle_caps_lock(True)

def on_press(key):
    global listener_active
    try:
        if is_rf_on():
            if keyboard.is_pressed('f1'):
                type_message(custom_messages["f1"])
            elif keyboard.is_pressed('f2'):
                type_message(custom_messages["f2"])
            elif keyboard.is_pressed('f3'):
                type_message(custom_messages["f3"])
            elif keyboard.is_pressed('f4'):
                type_message(custom_messages["f4"])
            elif keyboard.is_pressed('f5'):
                type_message(custom_messages["f5"])
            elif keyboard.is_pressed('f6'):
                type_message(custom_messages["f6"])
            elif keyboard.is_pressed('f7'):
                type_message(custom_messages["f7"])
            elif keyboard.is_pressed('f8'):
                type_message(custom_messages["f8"])
            elif keyboard.is_pressed('f9'):
                type_message(custom_messages["f9"])
            elif keyboard.is_pressed('f10'):
                type_message(custom_messages["f10"])
            elif keyboard.is_pressed('f11'):
                type_message(custom_messages["f11"])
            elif keyboard.is_pressed('f12'):
                type_message(custom_messages["f12"])
    except AttributeError:
        print('special key {0} pressed'.format(key))

# Function to get the correct path to the icon file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Create the GUI
root = tk.Tk()
root.title("6RepFarm")
root.geometry("382x366")  # Set the window size
root.resizable(False, False)  # Disable resizing
root.iconbitmap(resource_path("icon.ico"))  # Set the custom icon
sv_ttk.set_theme("dark")
macros_enabled_var = tk.IntVar(value=int(rf_enabled))
# Create a frame for padding
frame = ttk.Frame(root, padding="10")

def run_listener():
    global keyboard_listener
    keyboard_listener = kb.Listener(on_press=on_press)
    keyboard_listener.start()

def start_mouse_movement():
    global listener_active, macros_enabled_var, rf_enabled
    listener_active = True
    rf_enabled = 1
    toggle_button.config(text="Stop")
    print("Script ON")

def stop_mouse_movement():
    global listener_active, macros_enabled_var, rf_enabled
    listener_active = False
    rf_enabled = 0
    toggle_button.config(text="Start")
    print("Script OFF")
    cleanup()

def toggle_program():
    global listener_thread, keyboard_listener
    if listener_active:
        stop_mouse_movement()
    else:
        start_mouse_movement()
        listener_thread = threading.Thread(target=run_listener)
        listener_thread.start()
def save_and_close():
    global custom_messages, rf_duration, rf_interval
    rf_duration = float(rf_duration_entry.get())
    rf_interval = float(rf_interval_entry.get())
    custom_messages["f1"] = f1_message_entry.get()
    custom_messages["f2"] = f2_message_entry.get()
    custom_messages["f3"] = f3_message_entry.get()
    custom_messages["f4"] = f4_message_entry.get()
    custom_messages["f5"] = f5_message_entry.get()
    custom_messages["f6"] = f6_message_entry.get()
    custom_messages["f7"] = f7_message_entry.get()
    custom_messages["f8"] = f8_message_entry.get()
    custom_messages["f9"] = f9_message_entry.get()
    custom_messages["f10"] = f10_message_entry.get()
    custom_messages["f11"] = f11_message_entry.get()
    custom_messages["f12"] = f12_message_entry.get()
    config_manager.set("Messages", "f1", custom_messages["f1"])
    config_manager.set("Messages", "f2", custom_messages["f2"])
    config_manager.set("Messages", "f3", custom_messages["f3"])
    config_manager.set("Messages", "f4", custom_messages["f4"])
    config_manager.set("Messages", "f5", custom_messages["f5"])
    config_manager.set("Messages", "f6", custom_messages["f6"])
    config_manager.set("Messages", "f7", custom_messages["f7"])
    config_manager.set("Messages", "f8", custom_messages["f8"])
    config_manager.set("Messages", "f9", custom_messages["f9"])
    config_manager.set("Messages", "f10", custom_messages["f10"])
    config_manager.set("Messages", "f11", custom_messages["f11"])
    config_manager.set("Messages", "f12", custom_messages["f12"])
    config_manager.set("Settings", "rf_enabled", str(macros_enabled_var))
    config_manager.set("Settings", "rf_duration", str(rf_duration))
    config_manager.set("Settings", "rf_interval", str(rf_interval))
    config_manager.save_config()
    print("Configuration saved.")

f1_message_entry = ttk.Entry(root)
f1_message_entry.insert(0, custom_messages["f1"])
f1_message_entry.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

f2_message_entry = ttk.Entry(root)
f2_message_entry.insert(0, custom_messages["f2"])
f2_message_entry.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

f3_message_entry = ttk.Entry(root)
f3_message_entry.insert(0, custom_messages["f3"])
f3_message_entry.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

f4_message_entry = ttk.Entry(root)
f4_message_entry.insert(0, custom_messages["f4"])
f4_message_entry.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    
f5_message_entry = ttk.Entry(root)
f5_message_entry.insert(0, custom_messages["f5"])
f5_message_entry.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)

f6_message_entry = ttk.Entry(root)
f6_message_entry.insert(0, custom_messages["f6"])
f6_message_entry.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

f7_message_entry = ttk.Entry(root)
f7_message_entry.insert(0, custom_messages["f7"])
f7_message_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

f8_message_entry = ttk.Entry(root)
f8_message_entry.insert(0, custom_messages["f8"])
f8_message_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

f9_message_entry = ttk.Entry(root)
f9_message_entry.insert(0, custom_messages["f9"])
f9_message_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

f10_message_entry = ttk.Entry(root)
f10_message_entry.insert(0, custom_messages["f10"])
f10_message_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

f11_message_entry = ttk.Entry(root)
f11_message_entry.insert(0, custom_messages["f11"])
f11_message_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

f12_message_entry = ttk.Entry(root)
f12_message_entry.insert(0, custom_messages["f12"])
f12_message_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

rf_duration_label = ttk.Label(root, text="Keypress Duration:")
rf_duration_label.grid(row=6, column=0, padx=5, pady=5)
rf_duration_entry = ttk.Entry(root)
rf_duration_entry.insert(0, str(rf_duration))
rf_duration_entry.grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)

rf_interval_label = ttk.Label(root, text="Delay Between Keypresses:")
rf_interval_label.grid(row=6, column=1, padx=5, pady=5)
rf_interval_entry = ttk.Entry(root)
rf_interval_entry.insert(0, str(rf_interval))
rf_interval_entry.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)

reload_button = ttk.Button(root, text="Save", command=save_and_close)
reload_button.grid(row=8, column=0, padx=5, pady=5, ipadx=65)
toggle_button = ttk.Button(root, text="Start", command=toggle_program)
toggle_button.grid(row=8, column=1 , columnspan=2, pady=5, ipadx=63)

def cleanup():
    global listener_active, keyboard_listener, listener_thread

    # Stop the listeners
    listener_active = False
    if keyboard_listener is not None:
        keyboard_listener.stop()
        keyboard_listener = None

    # Stop the listener thread
    if listener_thread is not None:
        listener_thread.join(timeout=1)  # Wait for the thread to finish
        listener_thread = None

# Run the GUI loop
root.mainloop()