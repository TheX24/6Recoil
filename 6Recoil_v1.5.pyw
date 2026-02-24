import tkinter as tk
from tkinter import ttk
import threading
import ctypes
from pynput import keyboard as kb, mouse
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
cd_enabled        = config_manager.get("Settings", "cd",             "0") == "1"
rf_enabled        = config_manager.get("Settings", "rf",             "0") == "1"
rf_duration       = config_manager.get("Settings", "rf_duration",    "0.15")
rf_interval       = config_manager.get("Settings", "rf_interval",    "0.01")
variation         = config_manager.get("Settings", "variation",      "1")
variation_range   = config_manager.get("Settings", "variation_range","1")

# ============================================================================
# GLOBAL STATE
# ============================================================================

rpm_main      = 800
rpm_secondary = 800

mouse_main_vspeed      = 1
mouse_main_hspeed      = 1
mouse_secondary_vspeed = 1
mouse_secondary_hspeed = 1

active_main       = False
active_secondary  = False
both_buttons_held = False
listener_active   = False
keyboard_listener = None
mouse_listener    = None
pressed_buttons   = set()
moving            = False
use_custom_speed  = False

custom_main_vspeed      = 0
custom_main_hspeed      = 0
custom_secondary_vspeed = 0
custom_secondary_hspeed = 0

v_main_remainder      = 0.0
h_main_remainder      = 0.0
v_secondary_remainder = 0.0
h_secondary_remainder = 0.0

move_mouse_lock = threading.Lock()

# ============================================================================
# WEAPON SETTINGS
# ============================================================================

def set_rpm(duration, is_secondary=False):
    global rpm_main, rpm_secondary
    if is_secondary:
        rpm_secondary = float(duration)
        print(f"Set Secondary RPM to: {rpm_secondary} RPM")
    else:
        rpm_main = float(duration)
        print(f"Set Primary RPM to: {rpm_main} RPM")

def set_vspeed(vspeed, is_secondary=False):
    global mouse_main_vspeed, mouse_secondary_vspeed
    if is_secondary:
        mouse_secondary_vspeed = int(vspeed)
        print(f"Secondary Vertical: {mouse_secondary_vspeed}")
    else:
        mouse_main_vspeed = int(vspeed)
        print(f"Primary Vertical: {mouse_main_vspeed}")

def set_hspeed(hspeed, is_secondary=False):
    global mouse_main_hspeed, mouse_secondary_hspeed
    if is_secondary:
        mouse_secondary_hspeed = int(hspeed)
        print(f"Secondary Horizontal: {mouse_secondary_hspeed}")
    else:
        mouse_main_hspeed = int(hspeed)
        print(f"Primary Horizontal: {mouse_main_hspeed}")

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
    current_state = is_caps_lock_on()
    if (state and not current_state) or (not state and current_state):
        pydirectinput.press("capslock")

def type_message(message, delay=None, duration=None):
    global rf_interval, rf_duration
    was_caps_lock_on = is_caps_lock_on()
    if was_caps_lock_on:
        toggle_caps_lock(False)
    print(f"Typing message: {message}")
    if delay is None:    delay    = float(rf_interval)
    if duration is None: duration = float(rf_duration)
    pydirectinput.press("t", duration=duration, _pause=False)
    time.sleep(delay)
    pydirectinput.typewrite(message, interval=delay, duration=duration, _pause=False)
    time.sleep(delay)
    pydirectinput.press("enter", duration=duration, _pause=False)
    if was_caps_lock_on:
        toggle_caps_lock(True)

# ============================================================================
# FILE READING
# ============================================================================

def read_speed_options(file_name):
    speed_options = {}
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    gun, values = line.split("=", 1)
                    gun = gun.strip()
                    try:
                        vspeed, hspeed, r = map(float, [x.strip() for x in values.split(",")])
                        speed_options[gun] = {"vspeed": int(vspeed), "hspeed": int(hspeed), "rpm": float(r)}
                    except (ValueError, IndexError) as e:
                        print(f"Warning: Skipping invalid line: {line}. Error: {e}")
    except FileNotFoundError:
        print(f"Error: {file_name} not found. Using default values.")
        speed_options = {"Default": {"vspeed": 1, "hspeed": 1, "rpm": 800}}
    return speed_options

def read_operators(file_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        print(f"Error: {file_name} not found.")
        return []

# ============================================================================
# RECOIL LOOP
# ============================================================================

def start_moving():
    global moving

    def move_mouse():
        global moving, v_main_remainder, h_main_remainder, v_secondary_remainder, h_secondary_remainder
        if not moving:
            print("Started moving mouse")
            moving = True
            time.sleep(random.uniform(0.01, 0.06))
            while both_buttons_held and listener_active and is_caps_lock_on():
                if active_main:
                    if variation_var.get():
                        dx_variation = random.gauss(0, float(variation_range) / 2)
                        dy_variation = random.gauss(0, float(variation_range) / 2)
                    else:
                        dx_variation = 0
                        dy_variation = 0
                    total_dx = mouse_main_hspeed + dx_variation + h_main_remainder
                    total_dy = mouse_main_vspeed + dy_variation + v_main_remainder
                    move_dx  = int(round(total_dx))
                    move_dy  = int(round(total_dy))
                    h_main_remainder = total_dx - move_dx
                    v_main_remainder = total_dy - move_dy
                    if move_dx != 0 or move_dy != 0:
                        pydirectinput.moveRel(move_dx, move_dy, relative=True,
                                              disable_mouse_acceleration=True,
                                              _pause=False, duration=rpm_main + random.gauss(0, rpm_main * 0.05))
                elif active_secondary:
                    if variation_var.get():
                        dx_variation = random.uniform(-float(variation_range), float(variation_range))
                        dy_variation = random.uniform(-float(variation_range), float(variation_range))
                    else:
                        dx_variation = 0
                        dy_variation = 0
                    total_dx = mouse_secondary_hspeed + dx_variation + h_secondary_remainder
                    total_dy = mouse_secondary_vspeed + dy_variation + v_secondary_remainder
                    move_dx  = int(round(total_dx))
                    move_dy  = int(round(total_dy))
                    h_secondary_remainder = total_dx - move_dx
                    v_secondary_remainder = total_dy - move_dy
                    if move_dx != 0 or move_dy != 0:
                        pydirectinput.moveRel(move_dx, move_dy, relative=True,
                                              disable_mouse_acceleration=True,
                                              _pause=False, duration=rpm_secondary + random.gauss(0, rpm_secondary * 0.05))
                else:
                    break
            if moving:
                print("Stopped moving mouse")
                moving = False

    with move_mouse_lock:
        if not moving and (active_main or active_secondary):
            threading.Thread(target=move_mouse, daemon=True).start()

# ============================================================================
# EVENT HANDLERS
# ============================================================================

last_key_press_time = {}
KEY_DEBOUNCE_TIME   = 0.3

def on_press(key):
    global active_main, active_secondary
    current_time = time.time()
    try:
        if hasattr(key, "char") and key.char:
            if key.char in ["1", "2"]:
                if key.char in last_key_press_time:
                    if current_time - last_key_press_time[key.char] < KEY_DEBOUNCE_TIME:
                        return
                last_key_press_time[key.char] = current_time           
                if key.char == "1":
                    if active_main or active_secondary:
                        if not active_main:
                            toggle_caps_lock(False)
                            print("1 pressed, no primary recoil - CapsLock OFF")
                        else:
                            if not active_secondary:
                                active_secondary = False
                                root.after(0, lambda: toggle_secondary_button.config(text="Start"))
                            toggle_caps_lock(True)
                            root.after(0, lambda: toggle_main_button.config(text="Stop"))
                            print("Switched to Primary Weapon")

                elif key.char == "2":
                    if active_main or active_secondary:
                        if not active_secondary:
                            toggle_caps_lock(False)
                            print("2 pressed, no secondary recoil - CapsLock OFF")
                        else:
                            if not active_main:
                                active_main = False
                                root.after(0, lambda: toggle_main_button.config(text="Start"))
                            toggle_caps_lock(True)
                            root.after(0, lambda: toggle_secondary_button.config(text="Stop"))
                            print("Switched to Secondary Weapon")

            if toggle_caps_lock_var.get() and key.char.lower() in ["t", "y"]:
                if is_caps_lock_on():
                    toggle_caps_lock(False)
                    print(f"{key.char.upper()} pressed, chat opened - Toggle Key turned off")

        if key == kb.Key.enter and toggle_caps_lock_var.get():
            if not is_caps_lock_on():
                toggle_caps_lock(True)
                print("Enter pressed, chat closed - Toggle Key turned on")
        elif key == kb.Key.esc and toggle_caps_lock_var.get():
            if not is_caps_lock_on():
                toggle_caps_lock(True)
                print("Esc pressed, chat closed - Toggle Key turned on")

        if macros_enabled_var.get():
            key_str = str(key)
            if "f1" in key_str.lower(): type_message(custom_messages["f1"])
            elif "f2" in key_str.lower(): type_message(custom_messages["f2"])
            elif "f3" in key_str.lower(): type_message(custom_messages["f3"])
            elif "f4" in key_str.lower(): type_message(custom_messages["f4"])
            elif "f5" in key_str.lower(): type_message(custom_messages["f5"])

    except Exception as e:
        print(f"Error in on_press: {e}")

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
# GUI CALLBACKS
# ============================================================================

def select_random_attack_operator():
    operators = read_operators("attack_operators.txt")
    operator_label.config(text=f"Operator: {random.choice(operators)}" if operators else "No attack operators found")

def select_random_defense_operator():
    operators = read_operators("defense_operators.txt")
    operator_label.config(text=f"Operator: {random.choice(operators)}" if operators else "No defense operators found")

def toggle_always_on_top():
    if always_on_top_var.get():
        root.attributes("-topmost", True)
        print("Always on Top ON")
    else:
        root.attributes("-topmost", False)
        print("Always on Top OFF")

def on_speed_change(event):
    selected_speed = speed_main_var.get()
    if selected_speed in speed_main_options:
        gun_settings = speed_main_options[selected_speed]
        if not use_custom_speed or (event and hasattr(event, "widget") and event.widget == speed_main_menu):
            set_vspeed(gun_settings["vspeed"], is_secondary=False)
            set_hspeed(gun_settings["hspeed"], is_secondary=False)
            set_rpm(60 / gun_settings["rpm"], is_secondary=False)
    selected_secondary_speed = speed_secondary_var.get()
    if selected_secondary_speed in speed_secondary_options:
        gun_settings = speed_secondary_options[selected_secondary_speed]
        if not use_custom_speed or (event and hasattr(event, "widget") and event.widget == speed_secondary_menu):
            set_vspeed(gun_settings["vspeed"], is_secondary=True)
            set_hspeed(gun_settings["hspeed"], is_secondary=True)
            set_rpm(60 / gun_settings["rpm"], is_secondary=True)

def toggle_custom_speed():
    global use_custom_speed
    use_custom_speed = custom_speed_var.get()
    if use_custom_speed:
        try:
            set_vspeed(int(custom_main_vspeed_entry.get()), is_secondary=False)
            set_hspeed(int(custom_main_hspeed_entry.get()), is_secondary=False)
            set_rpm(60 / int(custom_main_rpm_entry.get()), is_secondary=False)
        except (ValueError, ZeroDivisionError):
            pass
        try:
            set_vspeed(int(custom_secondary_vspeed_entry.get()), is_secondary=True)
            set_hspeed(int(custom_secondary_hspeed_entry.get()), is_secondary=True)
            set_rpm(60 / int(custom_secondary_rpm_entry.get()), is_secondary=True)
        except (ValueError, ZeroDivisionError):
            pass
    else:
        on_speed_change(None)

def update_custom_vspeed(*args):
    global custom_main_vspeed, custom_secondary_vspeed
    try:
        if args and hasattr(args[0], "widget"):
            if args[0].widget == custom_main_vspeed_entry:
                custom_main_vspeed = int(custom_main_vspeed_entry.get())
                if use_custom_speed: set_vspeed(custom_main_vspeed, is_secondary=False)
            elif args[0].widget == custom_secondary_vspeed_entry:
                custom_secondary_vspeed = int(custom_secondary_vspeed_entry.get())
                if use_custom_speed: set_vspeed(custom_secondary_vspeed, is_secondary=True)
    except ValueError:
        pass

def update_custom_hspeed(*args):
    global custom_main_hspeed, custom_secondary_hspeed
    try:
        if args and hasattr(args[0], "widget"):
            if args[0].widget == custom_main_hspeed_entry:
                custom_main_hspeed = int(custom_main_hspeed_entry.get())
                if use_custom_speed: set_hspeed(custom_main_hspeed, is_secondary=False)
            elif args[0].widget == custom_secondary_hspeed_entry:
                custom_secondary_hspeed = int(custom_secondary_hspeed_entry.get())
                if use_custom_speed: set_hspeed(custom_secondary_hspeed, is_secondary=True)
    except ValueError:
        pass

def update_rpm(*args):
    try:
        if use_custom_speed:
            if args and hasattr(args[0], "widget"):
                if args[0].widget == custom_main_rpm_entry:
                    set_rpm(60 / int(custom_main_rpm_entry.get()), is_secondary=False)
                elif args[0].widget == custom_secondary_rpm_entry:
                    set_rpm(60 / int(custom_secondary_rpm_entry.get()), is_secondary=True)
    except (ValueError, ZeroDivisionError):
        pass

def toggle_main_program():
    global active_main, listener_active, keyboard_listener, mouse_listener
    if not listener_active:
        listener_active = True
        try:
            if keyboard_listener: keyboard_listener.stop()
            if mouse_listener:    mouse_listener.stop()
        except:
            pass
        keyboard_listener = kb.Listener(on_press=on_press)
        mouse_listener    = mouse.Listener(on_click=on_click)
        keyboard_listener.start()
        mouse_listener.start()
        print("Listeners started")
    active_main = not active_main
    if active_main:
        toggle_main_button.config(text="Stop")
        print("Primary weapon started")
    else:
        toggle_main_button.config(text="Start")
        print("Primary weapon stopped")

def toggle_secondary_program():
    global active_secondary, listener_active, keyboard_listener, mouse_listener
    if not listener_active:
        listener_active = True
        try:
            if keyboard_listener: keyboard_listener.stop()
            if mouse_listener:    mouse_listener.stop()
        except:
            pass
        keyboard_listener = kb.Listener(on_press=on_press)
        mouse_listener    = mouse.Listener(on_click=on_click)
        keyboard_listener.start()
        mouse_listener.start()
        print("Listeners started")
    active_secondary = not active_secondary
    if active_secondary:
        toggle_secondary_button.config(text="Stop")
        print("Secondary weapon started")
    else:
        toggle_secondary_button.config(text="Start")
        print("Secondary weapon stopped")

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
    config_window.attributes("-topmost", True)
    config_window.iconbitmap(resource_path("icon.ico"))
    sv_ttk.set_theme("dark" if dark_mode_enabled else "light")

    frame = ttk.Frame(config_window, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="Custom Messages:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    f1_message_entry = ttk.Entry(frame); f1_message_entry.insert(0, custom_messages["f1"])
    f1_message_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
    f2_message_entry = ttk.Entry(frame); f2_message_entry.insert(0, custom_messages["f2"])
    f2_message_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
    f3_message_entry = ttk.Entry(frame); f3_message_entry.insert(0, custom_messages["f3"])
    f3_message_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
    f4_message_entry = ttk.Entry(frame); f4_message_entry.insert(0, custom_messages["f4"])
    f4_message_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
    f5_message_entry = ttk.Entry(frame); f5_message_entry.insert(0, custom_messages["f5"])
    f5_message_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

    ttk.Checkbutton(frame, text="Always on Top",    variable=always_on_top_var, command=toggle_always_on_top).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Checkbutton(frame, text="Enable CD",        variable=toggle_caps_lock_var).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Checkbutton(frame, text="Enable RF",        variable=macros_enabled_var).grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Checkbutton(frame, text="Enable Variation", variable=variation_var).grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)

    variation_range_entry = ttk.Entry(frame); variation_range_entry.insert(0, variation_range)
    variation_range_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

    ttk.Checkbutton(frame, text="Enable Dark Mode", variable=dark_mode_var).grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Button(frame, text="Save and Close", command=save_and_close).grid(row=6, column=1, columnspan=2, pady=5, ipadx=33)

    ttk.Label(frame, text="Keypress Duration:").grid(row=7, column=0, padx=5, pady=5)
    rf_duration_entry = ttk.Entry(frame); rf_duration_entry.insert(0, rf_duration)
    rf_duration_entry.grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)

    ttk.Label(frame, text="Interval Between Keypresses:").grid(row=7, column=1, padx=5, pady=5)
    rf_interval_entry = ttk.Entry(frame); rf_interval_entry.insert(0, rf_interval)
    rf_interval_entry.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)

def cleanup():
    global listener_active, keyboard_listener, mouse_listener
    listener_active = False
    try:
        if keyboard_listener is not None:
            keyboard_listener.stop()
            keyboard_listener = None
    except Exception as e:
        print(f"Error stopping keyboard listener: {e}")
    try:
        if mouse_listener is not None:
            mouse_listener.stop()
            mouse_listener = None
    except Exception as e:
        print(f"Error stopping mouse listener: {e}")
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
root.geometry("625x300")
root.iconbitmap(resource_path("icon.ico"))
sv_ttk.set_theme("dark" if dark_mode_enabled else "light")

dark_mode_var        = tk.IntVar(value=int(dark_mode_enabled))
always_on_top_var    = tk.IntVar(value=int(always_on_top))
toggle_caps_lock_var = tk.IntVar(value=int(cd_enabled))
macros_enabled_var   = tk.IntVar(value=int(rf_enabled))
variation_var        = tk.IntVar(value=int(variation))

frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

speed_main_options      = read_speed_options("speed_main_options.txt")
speed_secondary_options = read_speed_options("speed_secondary_options.txt")

speed_main_var      = tk.StringVar(root)
speed_secondary_var = tk.StringVar(root)
speed_main_var.set(next(iter(speed_main_options)))
speed_secondary_var.set(next(iter(speed_secondary_options)))

# Row 0
credits_label = ttk.Label(frame, text="Made by TX24 (v1.5)")
credits_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
speed_main_menu_label = ttk.Label(frame, text="Primary Weapon Speed:")
speed_main_menu_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
speed_secondary_menu_label = ttk.Label(frame, text="Secondary Weapon Speed:")
speed_secondary_menu_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

# Row 1
custom_speed_var = tk.IntVar()
custom_speed_check = ttk.Checkbutton(frame, text="Use Custom Speeds", variable=custom_speed_var, command=toggle_custom_speed)
custom_speed_check.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
speed_main_menu = ttk.Combobox(frame, textvariable=speed_main_var, values=list(speed_main_options.keys()), height=5)
speed_main_menu.bind("<<ComboboxSelected>>", on_speed_change)
speed_main_menu.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
speed_secondary_menu = ttk.Combobox(frame, textvariable=speed_secondary_var, values=list(speed_secondary_options.keys()), height=5)
speed_secondary_menu.bind("<<ComboboxSelected>>", on_speed_change)
speed_secondary_menu.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

# Row 2
custom_main_vspeed_label = ttk.Label(frame, text="Vertical Speed:")
custom_main_vspeed_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
custom_main_vspeed_entry = ttk.Entry(frame); custom_main_vspeed_entry.insert(0, "1")
custom_main_vspeed_entry.grid(row=2, column=1, padx=5, pady=5, ipadx=15, sticky=tk.W)
custom_main_vspeed_entry.bind("<KeyRelease>", update_custom_vspeed)
custom_secondary_vspeed_entry = ttk.Entry(frame); custom_secondary_vspeed_entry.insert(0, "1")
custom_secondary_vspeed_entry.grid(row=2, column=2, padx=5, pady=5, ipadx=15, sticky=tk.W)
custom_secondary_vspeed_entry.bind("<KeyRelease>", update_custom_vspeed)

# Row 3
custom_main_hspeed_label = ttk.Label(frame, text="Horizontal Speed:")
custom_main_hspeed_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
custom_main_hspeed_entry = ttk.Entry(frame); custom_main_hspeed_entry.insert(0, "1")
custom_main_hspeed_entry.grid(row=3, column=1, padx=5, pady=5, ipadx=15, sticky=tk.W)
custom_main_hspeed_entry.bind("<KeyRelease>", update_custom_hspeed)
custom_secondary_hspeed_entry = ttk.Entry(frame); custom_secondary_hspeed_entry.insert(0, "1")
custom_secondary_hspeed_entry.grid(row=3, column=2, padx=5, pady=5, ipadx=15, sticky=tk.W)
custom_secondary_hspeed_entry.bind("<KeyRelease>", update_custom_hspeed)

# Row 4
custom_main_rpm_label = ttk.Label(frame, text="Gun RPM:")
custom_main_rpm_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
custom_main_rpm_entry = ttk.Entry(frame); custom_main_rpm_entry.insert(0, "800")
custom_main_rpm_entry.grid(row=4, column=1, padx=5, pady=5, ipadx=15, sticky=tk.W)
custom_main_rpm_entry.bind("<KeyRelease>", update_rpm)
custom_secondary_rpm_entry = ttk.Entry(frame); custom_secondary_rpm_entry.insert(0, "800")
custom_secondary_rpm_entry.grid(row=4, column=2, padx=5, pady=5, ipadx=15, sticky=tk.W)
custom_secondary_rpm_entry.bind("<KeyRelease>", update_rpm)

# Row 5
operator_label = ttk.Label(frame, text="Operator: None")
operator_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
random_defense_operator_button = ttk.Button(frame, text="Select Random Defender", command=select_random_defense_operator)
random_defense_operator_button.grid(row=5, column=1, padx=5, pady=5, ipadx=18, sticky=tk.W)
random_attack_operator_button = ttk.Button(frame, text="Select Random Attacker", command=select_random_attack_operator)
random_attack_operator_button.grid(row=5, column=2, padx=5, pady=5, ipadx=21, sticky=tk.W)

# Row 6
config_menu = ttk.Button(frame, text="Config", command=open_config_window)
config_menu.grid(row=6, column=0, padx=5, pady=5, ipadx=43, sticky=tk.W)
toggle_main_button = ttk.Button(frame, text="Start", command=toggle_main_program)
toggle_main_button.grid(row=6, column=1, columnspan=4, padx=5, pady=5, ipadx=78, sticky=tk.W)
toggle_secondary_button = ttk.Button(frame, text="Start", command=toggle_secondary_program)
toggle_secondary_button.grid(row=6, column=2, columnspan=4, padx=5, pady=5, ipadx=78, sticky=tk.W)

on_speed_change(None)
toggle_always_on_top()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
