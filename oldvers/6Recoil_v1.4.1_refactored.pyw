import tkinter as tk
from tkinter import ttk
import threading
import ctypes
from pynput import keyboard as kb, mouse
import keyboard
import os
import random
import sv_ttk
import sys
import configparser
import pydirectinput
import time

# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================

class ConfigManager:
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.defaults = {
            "Settings": {
                "always_on_top": "0",
                "swd": "0",
                "cd": "0",
                "rf": "0",
                "variation": "1",
                "variation_range": "1",
                "dark_mode": "0",
                "rf_duration": "0.15",
                "rf_interval": "0.01",
            },
            "Messages": {
                "f1": "glhf",
                "f2": "ggwp",
                "f3": "nt",
                "f4": "nice",
                "f5": "good job",
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

# ============================================================================
# CONFIGURATION LOADING
# ============================================================================

config_manager = ConfigManager()

custom_messages = {
    "f1": config_manager.get("Messages", "f1", "glhf"),
    "f2": config_manager.get("Messages", "f2", "ggwp"),
    "f3": config_manager.get("Messages", "f3", "nt"),
    "f4": config_manager.get("Messages", "f4", "nice team"),
    "f5": config_manager.get("Messages", "f5", "good job"),
}

dark_mode_enabled = config_manager.get("Settings", "dark_mode",      "0") == "1"
always_on_top     = config_manager.get("Settings", "always_on_top",  "0") == "1"
swd_enabled       = config_manager.get("Settings", "swd",            "0") == "1"
cd_enabled        = config_manager.get("Settings", "cd",             "0") == "1"
rf_enabled        = config_manager.get("Settings", "rf",             "0") == "1"
rf_duration       = config_manager.get("Settings", "rf_duration",    "0.15")
rf_interval       = config_manager.get("Settings", "rf_interval",    "0.01")
variation         = config_manager.get("Settings", "variation",      "1")
variation_range   = config_manager.get("Settings", "variation_range","1")

# ============================================================================
# GLOBAL STATE
# ============================================================================

rpm            = 800
mouse_vspeed   = 1
mouse_hspeed   = 1
active         = False
both_buttons_held  = False
listener_active    = False
listener_thread    = None
keyboard_listener  = None
mouse_listener     = None
pressed_buttons    = set()
moving             = False
use_custom_speed   = False
custom_vspeed      = 0
custom_hspeed      = 0
v_remainder        = 0.0
h_remainder        = 0.0
move_mouse_lock    = threading.Lock()

# ============================================================================
# WEAPON SETTINGS
# ============================================================================

def set_rpm(duration):
    global rpm
    rpm = float(duration)
    print(f"Set RPM to: {rpm} RPM")

def set_vspeed(vspeed):
    global mouse_vspeed
    mouse_vspeed = int(vspeed)
    print(f"Vertical: {mouse_vspeed}")

def set_hspeed(hspeed):
    global mouse_hspeed
    mouse_hspeed = int(hspeed)
    print(f"Horizontal: {mouse_hspeed}")

# ============================================================================
# UTILITIES
# ============================================================================

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def is_caps_lock_on():
    return True if ctypes.windll.user32.GetKeyState(0x14) & 1 else False

def toggle_caps_lock(state):
    if state:
        pydirectinput.press('capslock')
    else:
        pydirectinput.press('capslock')

def type_message(message, delay=None, duration=None):
    global rf_interval, rf_duration
    was_caps_lock_on = is_caps_lock_on()
    if was_caps_lock_on:
        toggle_caps_lock(False)
    print(f"Typing message: {message}")
    if delay is None:
        delay = float(rf_interval)
    if duration is None:
        duration = float(rf_duration)
    pydirectinput.press('t', duration=duration, _pause=False)
    time.sleep(delay)
    pydirectinput.typewrite(message, interval=delay, duration=duration, _pause=False)
    time.sleep(delay)
    pydirectinput.press('enter', duration=duration, _pause=False)
    if was_caps_lock_on:
        toggle_caps_lock(True)

# ============================================================================
# EVENT HANDLERS
# ============================================================================

def on_press(key):
    global active, listener_active
    try:
        if key == kb.Key.caps_lock:
            active = not active
            print("Toggle Key ON" if active else "Toggle Key OFF")
        elif keyboard.is_pressed('t') and toggle_caps_lock_var.get():
            if is_caps_lock_on():
                toggle_caps_lock(False)
                print("T pressed, Toggle Key turned off")
        elif keyboard.is_pressed('y') and toggle_caps_lock_var.get():
            if is_caps_lock_on():
                toggle_caps_lock(False)
                print("Y pressed, Toggle Key turned off")
        elif keyboard.is_pressed('enter') and toggle_caps_lock_var.get():
            if not is_caps_lock_on():
                toggle_caps_lock(True)
                print("Enter pressed, Toggle Key turned on")
        elif keyboard.is_pressed('esc') and toggle_caps_lock_var.get():
            if not is_caps_lock_on():
                toggle_caps_lock(True)
                print("Esc pressed, Toggle Key turned on")
        elif macros_enabled_var.get():
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

        if listen_keys_var.get():
            if keyboard.is_pressed('1'):
                if not is_caps_lock_on():
                    toggle_caps_lock(True)
                    print("1 pressed, Caps Lock turned on")
            elif keyboard.is_pressed('2'):
                if is_caps_lock_on():
                    toggle_caps_lock(False)
                    print("2 pressed, Caps Lock turned off")

    except AttributeError:
        if key == kb.Key.caps_lock:
            active = not active
            print("CapsLock ON" if active else "CapsLock OFF")

def on_click(x, y, button, pressed):
    global both_buttons_held, moving
    if pressed:
        pressed_buttons.add(button)
    else:
        pressed_buttons.discard(button)

    if mouse.Button.left in pressed_buttons and mouse.Button.right in pressed_buttons:
        if not both_buttons_held:
            both_buttons_held = True
            print("Both buttons held")
            start_moving()
    else:
        if both_buttons_held:
            both_buttons_held = False
            moving = False
            print("Both buttons released")

# ============================================================================
# RECOIL LOOP
# ============================================================================

def start_moving():
    global moving

    def move_mouse():
        global moving, rpm, v_remainder, h_remainder
        if not moving:
            print("Started moving mouse")
            print(f"RPM: {rpm}")
            moving = True
            while both_buttons_held and active and listener_active and is_caps_lock_on():
                dx = mouse_hspeed
                dy = mouse_vspeed
                if variation_var.get():
                    dx_variation = random.uniform(-float(variation_range), float(variation_range))
                    dy_variation = random.uniform(-float(variation_range), float(variation_range))
                else:
                    dx_variation = 0
                    dy_variation = 0
                total_dx = dx + dx_variation + h_remainder
                total_dy = dy + dy_variation + v_remainder
                move_dx = int(round(total_dx))
                move_dy = int(round(total_dy))
                h_remainder = total_dx - move_dx
                v_remainder = total_dy - move_dy
                if move_dx != 0 or move_dy != 0:
                    pydirectinput.moveRel(move_dx, move_dy, relative=True,
                                         disable_mouse_acceleration=True,
                                         _pause=False, duration=rpm)
                else:
                    while both_buttons_held and active and listener_active and is_caps_lock_on():
                        pydirectinput.moveRel(mouse_hspeed, mouse_vspeed, relative=True,
                                              disable_mouse_acceleration=True,
                                              _pause=False, duration=rpm)
            if moving:
                print("Stopped moving mouse")
                moving = False

    with move_mouse_lock:
        if not moving:
            threading.Thread(target=move_mouse, daemon=True).start()

# ============================================================================
# FILE READING
# ============================================================================

def read_speed_options(file_name):
    speed_options = {}
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if '=' in line:
                    gun, values = line.strip().split('=')
                    gun = gun.strip()
                    vspeed, hspeed, r = map(int, values.strip().split(','))
                    speed_options[gun] = {'vspeed': vspeed, 'hspeed': hspeed, 'rpm': r}
    except FileNotFoundError:
        print(f"Error: {file_name} not found.")
    except ValueError:
        print(f"Error: Invalid format in {file_name}.")
    return speed_options

def read_operators(file_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        print(f"Error: {file_name} not found.")
        return []

# ============================================================================
# GUI CALLBACKS
# ============================================================================

def select_random_attack_operator():
    operators = read_operators('attack_operators.txt')
    operator_label.config(text=f"Operator: {random.choice(operators)}" if operators else "No attack operators found")

def select_random_defense_operator():
    operators = read_operators('defense_operators.txt')
    operator_label.config(text=f"Operator: {random.choice(operators)}" if operators else "No defense operators found")

def toggle_always_on_top():
    if always_on_top_var.get():
        root.attributes("-topmost", True)
        print("Always on Top ON")
    else:
        root.attributes("-topmost", False)
        print("Always on Top OFF")

def on_speed_change(event):
    selected_speed = speed_var.get()
    if not use_custom_speed:
        gun_settings = speed_options[selected_speed]
        set_vspeed(gun_settings['vspeed'])
        set_hspeed(gun_settings['hspeed'])
        set_rpm(60 / gun_settings['rpm'])

def toggle_custom_speed():
    global use_custom_speed
    use_custom_speed = custom_speed_var.get()
    if use_custom_speed:
        set_vspeed(custom_vspeed)
        set_hspeed(custom_hspeed)
    else:
        on_speed_change(None)

def update_custom_vspeed(*args):
    global custom_vspeed
    try:
        custom_vspeed = int(custom_vspeed_entry.get())
        if use_custom_speed:
            set_vspeed(custom_vspeed)
    except ValueError:
        pass

def update_custom_hspeed(*args):
    global custom_hspeed
    try:
        custom_hspeed = int(custom_hspeed_entry.get())
        if use_custom_speed:
            set_hspeed(custom_hspeed)
    except ValueError:
        pass

def update_rpm(*args):
    try:
        if use_custom_speed:
            set_rpm(60 / int(custom_rpm_entry.get()))
    except ValueError:
        pass

def start_mouse_movement():
    global listener_active, active
    active = is_caps_lock_on()
    listener_active = True
    toggle_button.config(text="Stop")
    print("Script ON")

def stop_mouse_movement():
    global listener_active, active
    listener_active = False
    active = False
    toggle_button.config(text="Start")
    print("Script OFF")

def toggle_program():
    global listener_thread, keyboard_listener, mouse_listener
    if listener_active:
        stop_mouse_movement()
    else:
        start_mouse_movement()
        listener_thread = threading.Thread(target=run_listener)
        listener_thread.start()

def run_listener():
    global keyboard_listener, mouse_listener
    keyboard_listener = kb.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener.start()
    mouse_listener.start()

def open_config_window():
    def save_and_close():
        global custom_messages, dark_mode_enabled, rf_duration, rf_interval, variation, variation_range
        dark_mode_enabled = bool(dark_mode_var.get())
        custom_messages["f1"] = f1_message_entry.get()
        custom_messages["f2"] = f2_message_entry.get()
        custom_messages["f3"] = f3_message_entry.get()
        custom_messages["f4"] = f4_message_entry.get()
        custom_messages["f5"] = f5_message_entry.get()
        config_manager.set("Messages", "f1", custom_messages["f1"])
        config_manager.set("Messages", "f2", custom_messages["f2"])
        config_manager.set("Messages", "f3", custom_messages["f3"])
        config_manager.set("Messages", "f4", custom_messages["f4"])
        config_manager.set("Messages", "f5", custom_messages["f5"])
        config_manager.set("Settings", "always_on_top", str(always_on_top_var.get()))
        config_manager.set("Settings", "swd",           str(listen_keys_var.get()))
        config_manager.set("Settings", "cd",            str(toggle_caps_lock_var.get()))
        config_manager.set("Settings", "rf",            str(macros_enabled_var.get()))
        config_manager.set("Settings", "dark_mode",     str(int(dark_mode_enabled)))
        variation_range = variation_range_entry.get()
        config_manager.set("Settings", "variation",       str(variation_var.get()))
        config_manager.set("Settings", "variation_range", str(variation_range))
        rf_duration = rf_duration_entry.get()
        rf_interval = rf_interval_entry.get()
        config_manager.set("Settings", "rf_duration", rf_duration)
        config_manager.set("Settings", "rf_interval", rf_interval)
        config_manager.save_config()
        sv_ttk.set_theme("dark" if dark_mode_enabled else "light")
        config_window.destroy()

    config_window = tk.Toplevel(root)
    config_window.title("Config")
    config_window.resizable(False, False)
    config_window.attributes('-topmost', True)
    config_window.iconbitmap(resource_path("icon.ico"))
    sv_ttk.set_theme("dark" if dark_mode_enabled else "light")

    ttk.Label(config_window, text="Custom Messages:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    f1_message_entry = ttk.Entry(config_window); f1_message_entry.insert(0, custom_messages["f1"])
    f1_message_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
    f2_message_entry = ttk.Entry(config_window); f2_message_entry.insert(0, custom_messages["f2"])
    f2_message_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
    f3_message_entry = ttk.Entry(config_window); f3_message_entry.insert(0, custom_messages["f3"])
    f3_message_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
    f4_message_entry = ttk.Entry(config_window); f4_message_entry.insert(0, custom_messages["f4"])
    f4_message_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
    f5_message_entry = ttk.Entry(config_window); f5_message_entry.insert(0, custom_messages["f5"])
    f5_message_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

    ttk.Checkbutton(config_window, text="Always on Top",    variable=always_on_top_var, command=toggle_always_on_top).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Checkbutton(config_window, text="Enable SWD",       variable=listen_keys_var).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Checkbutton(config_window, text="Enable CD",        variable=toggle_caps_lock_var).grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Checkbutton(config_window, text="Enable RF",        variable=macros_enabled_var).grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Checkbutton(config_window, text="Enable Variation", variable=variation_var).grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Checkbutton(config_window, text="Enable Dark Mode", variable=dark_mode_var).grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)

    variation_range_entry = ttk.Entry(config_window); variation_range_entry.insert(0, variation_range)
    variation_range_entry.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)

    ttk.Button(config_window, text="Save and Close", command=save_and_close).grid(row=7, column=1, columnspan=2, pady=5, ipadx=33)

    ttk.Label(config_window, text="Keypress Duration:").grid(row=8, column=0, padx=5, pady=5)
    rf_duration_entry = ttk.Entry(config_window); rf_duration_entry.insert(0, rf_duration)
    rf_duration_entry.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)

    ttk.Label(config_window, text="Interval Between Keypresses:").grid(row=8, column=1, padx=5, pady=5)
    rf_interval_entry = ttk.Entry(config_window); rf_interval_entry.insert(0, rf_interval)
    rf_interval_entry.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)

def cleanup():
    global listener_active, keyboard_listener, mouse_listener, listener_thread
    listener_active = False
    if keyboard_listener is not None:
        keyboard_listener.stop()
        keyboard_listener = None
    if mouse_listener is not None:
        mouse_listener.stop()
        mouse_listener = None
    if listener_thread is not None:
        listener_thread.join(timeout=1)
        listener_thread = None
    print("Listeners and threads stopped. Exiting application.")

def on_close():
    cleanup()
    root.destroy()

# ============================================================================
# GUI INIT
# ============================================================================

root = tk.Tk()
root.title("6Recoil")
root.resizable(False, False)
root.iconbitmap(resource_path("icon.ico"))
sv_ttk.set_theme("dark" if dark_mode_enabled else "light")

dark_mode_var        = tk.IntVar(value=int(dark_mode_enabled))
always_on_top_var    = tk.IntVar(value=int(always_on_top))
listen_keys_var      = tk.IntVar(value=int(swd_enabled))
toggle_caps_lock_var = tk.IntVar(value=int(cd_enabled))
macros_enabled_var   = tk.IntVar(value=int(rf_enabled))
variation_var        = tk.IntVar(value=int(variation))

frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

speed_options = read_speed_options('speed_options_new.txt')
speed_var = tk.StringVar(root)
speed_var.set(next(iter(speed_options)))

# Row 0
custom_speed_check = ttk.Checkbutton(frame, text="Use Custom Speeds", variable=custom_speed_var if False else tk.IntVar(), command=toggle_custom_speed)
# (custom_speed_var defined below, placeholder above is wrong — define vars first)

custom_speed_var = tk.IntVar()
custom_vspeed_var = tk.IntVar()
custom_hspeed_var = tk.IntVar()
custom_rpm_var    = tk.IntVar()

custom_speed_check = ttk.Checkbutton(frame, text="Use Custom Speeds", variable=custom_speed_var, command=toggle_custom_speed)
custom_speed_check.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

speed_menu = ttk.Combobox(frame, textvariable=speed_var, values=list(speed_options.keys()), height=5)
speed_menu.bind("<<ComboboxSelected>>", on_speed_change)
speed_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

# Row 1
custom_vspeed_label = ttk.Label(frame, text="Vertical Speed:")
custom_vspeed_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
custom_vspeed_entry = ttk.Entry(frame); custom_vspeed_entry.insert(0, "1")
custom_vspeed_entry.grid(row=1, column=1, padx=5, pady=5, ipadx=15, sticky=tk.W)
custom_vspeed_entry.bind("<KeyRelease>", update_custom_vspeed)

# Row 2
custom_hspeed_label = ttk.Label(frame, text="Horizontal Speed:")
custom_hspeed_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
custom_hspeed_entry = ttk.Entry(frame); custom_hspeed_entry.insert(0, "1")
custom_hspeed_entry.grid(row=2, column=1, padx=5, pady=5, ipadx=15, sticky=tk.W)
custom_hspeed_entry.bind("<KeyRelease>", update_custom_hspeed)

# Row 3
custom_rpm_label = ttk.Label(frame, text="Gun RPM:")
custom_rpm_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
custom_rpm_entry = ttk.Entry(frame); custom_rpm_entry.insert(0, "800")
custom_rpm_entry.grid(row=3, column=1, padx=5, pady=5, ipadx=15, sticky=tk.W)
custom_rpm_entry.bind("<KeyRelease>", update_rpm)

# Row 4
operator_label = ttk.Label(frame, text="Operator: None")
operator_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
random_defense_operator_button = ttk.Button(frame, text="Select Random Defender", command=select_random_defense_operator)
random_defense_operator_button.grid(row=4, column=1, padx=5, pady=5, ipadx=18, sticky=tk.W)

# Row 5
credits_label = ttk.Label(frame, text="Made by TX24 (v1.4.1)")
credits_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
random_attack_operator_button = ttk.Button(frame, text="Select Random Attacker", command=select_random_attack_operator)
random_attack_operator_button.grid(row=5, column=1, padx=5, pady=5, ipadx=21, sticky=tk.W)

# Row 6
config_menu = ttk.Button(frame, text="Config", command=open_config_window)
config_menu.grid(row=6, column=0, padx=5, pady=5, ipadx=43, sticky=tk.W)
toggle_button = ttk.Button(frame, text="Start", command=toggle_program)
toggle_button.grid(row=6, column=1, columnspan=4, padx=5, pady=5, ipadx=78, sticky=tk.W)

toggle_always_on_top()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
