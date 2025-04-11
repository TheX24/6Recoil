import tkinter as tk
from tkinter import ttk
import threading
import time
import ctypes
from ctypes import wintypes
import pyautogui
from pynput import keyboard, mouse
import os
import random
import sv_ttk
import sys

# Define global variables
primary_weapon = True
mouse_speed = 1
sleep_duration = 0.012  # <-- CHANGE THIS DONT TOUCH ANYTHING ELSE
active = False
both_buttons_held = False
listener_active = False
listener_thread = None
keyboard_listener = None
mouse_listener = None
pressed_buttons = set()
moving = False  # Flag to track moving state
use_custom_speed = False  # Flag to use custom speed
custom_speed = 0  # Custom speed value

# ctypes bypass
user32 = ctypes.WinDLL('user32', use_last_error=True)
INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
MAPVK_VK_TO_VSC = 0
wintypes.ULONG_PTR = wintypes.WPARAM
class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))
class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))
    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)
class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))
class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))
LPINPUT = ctypes.POINTER(INPUT)
def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
def press_t():
    PressKey(0x54)
    time.sleep(0.1)
    ReleaseKey(0x54)
    print("T pressed")
def press_enter():
    PressKey(0x0D)
    time.sleep(0.1)
    ReleaseKey(0x0D)
    print("Enter pressed")

# Define constants for mouse input
MOUSEEVENTF_MOVE = 0x0001

# Function to update mouse speed from GUI
def set_speed(name, speed):
    global mouse_speed
    mouse_speed = int(speed)  # Ensure mouse_speed is an integer
    print(f"Selected speed: {name}, {mouse_speed}")

# Function to update sleep duration from GUI
def set_sleep_duration(duration):
    global sleep_duration
    sleep_duration = float(duration)  # Ensure sleep_duration is a float
    print(f"Set interval to: {sleep_duration} seconds")

# Function to toggle Caps Lock state
def toggle_caps_lock(state):
    if state:
        pyautogui.press('capslock')
    else:
        pyautogui.press('capslock')

# Function to check if Caps Lock is on
def is_caps_lock_on():
    return ctypes.windll.user32.GetKeyState(0x14) & 1

# Function to type a message
def type_message(message, delay=0.2):
    was_caps_lock_on = is_caps_lock_on()
    if was_caps_lock_on:
        toggle_caps_lock(False)
    print(f"Typing message: {message}")
    press_t()
    time.sleep(delay)
    pyautogui.typewrite(message, interval=delay)
    time.sleep(delay)
    press_enter()
    if was_caps_lock_on:
        toggle_caps_lock(True)

# Functions to toggle the program activation state
def on_press(key):
    global active, listener_active
    try:
        # Check if Caps Lock key is pressed
        if key == keyboard.Key.caps_lock:
            active = not active
            print("CapsLock ON" if active else "CapsLock OFF")
        # Checks for chat keys are pressed
        elif hasattr(key, 'char') and key.char == 't' and toggle_caps_lock_var.get():
            if is_caps_lock_on():
                toggle_caps_lock(False)
                print("T pressed, Caps Lock turned off")
        elif hasattr(key, 'char') and key.char == 'y' and toggle_caps_lock_var.get():
            if is_caps_lock_on():
                toggle_caps_lock(False)
                print("Y pressed, Caps Lock turned off")
        elif key == keyboard.Key.enter and toggle_caps_lock_var.get():
            if not is_caps_lock_on():
                toggle_caps_lock(True)
                print("Enter pressed, Caps Lock turned on")
        elif key == keyboard.Key.esc and toggle_caps_lock_var.get():
            if not is_caps_lock_on():
                toggle_caps_lock(True)
                print("Esc pressed, Caps Lock turned on")
        # Check for F1 and F2 keys to trigger messages
        elif macros_enabled_var.get():  # Check if the macros checkbox is checked
            if key == keyboard.Key.f1:
                type_message("glhf")
            elif key == keyboard.Key.f2:
                type_message("ggwp")
            elif key == keyboard.Key.f3:
                type_message("nt")
            elif key == keyboard.Key.f4:
                type_message("nice")
        # SWD function
        if listen_keys_var.get():  # Check if the checkbox is checked
            if hasattr(key, 'char') and key.char == '1':
                if not is_caps_lock_on():
                    toggle_caps_lock(True)
                    print("1 pressed, Caps Lock turned on")
            elif hasattr(key, 'char') and key.char == '2':
                if is_caps_lock_on():
                    toggle_caps_lock(False)
                    print("2 pressed, Caps Lock turned off")
    except AttributeError:
        if key == keyboard.Key.caps_lock:
            active = not active
            print("CapsLock ON" if active else "CapsLock OFF")

# Checks for mouse buttons being held
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

# Main function for recoil
def start_moving():
    global moving
    def move_mouse():
        global moving
        if not moving:
            print("Started moving mouse")
            moving = True
        while both_buttons_held and active and listener_active:
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE, 0, mouse_speed, 0, 0)
            time.sleep(sleep_duration)
        if moving:
            print("Stopped moving mouse")
            moving = False
    threading.Thread(target=move_mouse).start()

# Function to read speed options from a text file
def read_speed_options(file_name):
    speed_options = {}
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, 'r') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=')
                speed_options[key.strip()] = int(value.strip())
    return speed_options

# Function to read operators from a text file
def read_operators(file_name):
    operators = []
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, 'r') as file:
        operators = [line.strip() for line in file]
    return operators

# Function to select a random attack operator
def select_random_attack_operator():
    operators = read_operators('attack_operators.txt')
    if operators:
        selected_operator = random.choice(operators)
        operator_label.config(text=f"Operator: {selected_operator}")
    else:
        operator_label.config(text="No attack operators found")

# Function to select a random defense operator
def select_random_defense_operator():
    operators = read_operators('defense_operators.txt')
    if operators:
        selected_operator = random.choice(operators)
        operator_label.config(text=f"Operator: {selected_operator}")
    else:
        operator_label.config(text="No defense operators found")

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
root.title("6Recoil")
root.geometry("560x230")  # Set the window size
root.resizable(False, False)
root.iconbitmap(resource_path("icon.ico"))  # Set the custom icon
sv_ttk.set_theme("light")

# Initialize the toggle_caps_lock_var after creating the root window
toggle_caps_lock_var = tk.IntVar()  # Variable to track the state of the Caps Lock toggle checkbox
macros_enabled_var = tk.IntVar()  # Variable to track the state of the macros enabled checkbox

# Create a frame for padding
frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

# Create a label for speed selection
speed_label = ttk.Label(frame, text="Select Weapon:")
speed_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

# Read speed options from the text file
speed_options = read_speed_options('speed_options.txt')

# Create a dropdown menu for speed selection
speed_var = tk.StringVar(root)
speed_var.set(next(iter(speed_options)))  # Default value

def on_speed_change(event):
    selected_speed = speed_var.get()
    if not use_custom_speed:
        set_speed(selected_speed, speed_options[selected_speed])

speed_menu = ttk.Combobox(frame, textvariable=speed_var, values=list(speed_options.keys()), height=5)
speed_menu.bind("<<ComboboxSelected>>", on_speed_change)
speed_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

# Create a checkbox and number input for custom speed
custom_speed_var = tk.IntVar()

def toggle_custom_speed():
    global use_custom_speed
    use_custom_speed = custom_speed_var.get()
    if use_custom_speed:
        set_speed("Custom", custom_speed)
    else:
        on_speed_change(None)

custom_speed_check = ttk.Checkbutton(frame, text="Use Custom Speed", variable=custom_speed_var, command=toggle_custom_speed)
custom_speed_check.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

def update_custom_speed(*args):
    global custom_speed
    try:
        custom_speed = int(custom_speed_entry.get())  # Convert to integer
        if use_custom_speed:
            set_speed("Custom", custom_speed)
    except ValueError:
        pass  # Ignore invalid input

custom_speed_entry = ttk.Entry(frame)
custom_speed_entry.insert(0, "1")
custom_speed_entry.grid(row=1, column=1, padx=5, pady=5, ipadx=15, sticky=tk.W)
custom_speed_entry.bind("<KeyRelease>", update_custom_speed)

# Create a label and entry for sleep duration
sleep_duration_label = ttk.Label(frame, text="Set Interval (seconds):")
sleep_duration_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

sleep_duration_entry = ttk.Entry(frame)
sleep_duration_entry.insert(0, str(sleep_duration))
sleep_duration_entry.grid(row=2, column=1, padx=5, pady=5, ipadx=15, sticky=tk.W)

def update_sleep_duration(*args):
    try:
        set_sleep_duration(sleep_duration_entry.get())
    except ValueError:
        pass  # Ignore invalid input

sleep_duration_entry.bind("<KeyRelease>", update_sleep_duration)

# Function to toggle the "always on top" attribute
def toggle_always_on_top():
    root.attributes("-topmost", always_on_top_var.get())

# Create a checkbox for "always on top"
always_on_top_var = tk.IntVar()
always_on_top_check = ttk.Checkbutton(frame, text="Always on Top", variable=always_on_top_var, command=toggle_always_on_top)
always_on_top_check.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

# Create a checkbox to toggle listening for key.char == '1' and key.char == '2'
listen_keys_var = tk.IntVar()
listen_keys_check = ttk.Checkbutton(frame, text="Enable SWD", variable=listen_keys_var)
listen_keys_check.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

# Create a checkbox to toggle Caps Lock functionality
toggle_caps_lock_check = ttk.Checkbutton(frame, text="Enable CD", variable=toggle_caps_lock_var)
toggle_caps_lock_check.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)

# Create a checkbox to enable/disable rep farm
macros_enabled_check = ttk.Checkbutton(frame, text="Enable RF", variable=macros_enabled_var)
macros_enabled_check.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)

# Create a button to select a random attack operator
random_attack_operator_button = ttk.Button(frame, text="Select Random Attacker", command=select_random_attack_operator)
random_attack_operator_button.grid(row=4, column=0, padx=5, pady=5, ipadx=8, sticky=tk.W)

# Create a button to select a random defense operator
random_defense_operator_button = ttk.Button(frame, text="Select Random Defender", command=select_random_defense_operator)
random_defense_operator_button.grid(row=4, column=1, padx=5, pady=5, ipadx=18, sticky=tk.W)

# Create a label to display the selected operator
operator_label = ttk.Label(frame, text="Operator: None")
operator_label.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)

# Function to start mouse movement
def start_mouse_movement():
    global listener_active, active
    active = is_caps_lock_on()  # Check Caps Lock state when starting
    listener_active = True
    toggle_button.config(text="Stop")
    print("Script ON")

# Function to stop mouse movement
def stop_mouse_movement():
    global listener_active, active
    listener_active = False
    active = False  # Reset active state
    toggle_button.config(text="Start")
    print("Script OFF")

# Create a start/stop button to toggle the program
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
    # Collect events until released
    with keyboard.Listener(on_press=on_press) as k_listener, mouse.Listener(on_click=on_click) as m_listener:
        keyboard_listener = k_listener
        mouse_listener = m_listener
        k_listener.join()
        m_listener.join()

toggle_button = ttk.Button(frame, text="Start", command=toggle_program)
toggle_button.grid(row=3, column=1, columnspan=4, padx=5, pady=5, ipadx=78, sticky=tk.W)

credits_label = ttk.Label(frame, text="Made by TX24 (v1.2.1)")
credits_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

# Run the GUI loop
root.mainloop()