import tkinter as tk
from tkinter import ttk
import threading
import ctypes
from pynput import mouse
import sv_ttk
import pydirectinput
import sys
import os

sleep_duration = 600
vert_speed = 1
horiz_speed = 1
active = False
both_buttons_held = False
listener_active = False
listener_thread = None
mouse_listener = None
pressed_buttons = set()
moving = False

# Function to update sleep duration from GUI
def set_sleep_duration(duration):
    global sleep_duration
    sleep_duration = float(duration)  # Ensure sleep_duration is a float
    print(f"Set RPM to: {sleep_duration} RPM")

# Function to update mouse speed from GUI
def set_vert_speed(vertspeed):
    global vert_speed
    vert_speed = int(vertspeed)  # Ensure mouse_speed is an integer
    print(f"Vertical: {vertspeed}")

# Function to update mouse speed from GUI
def set_horiz_speed(horizspeed):
    global horiz_speed
    horiz_speed = int(horizspeed)  # Ensure mouse_speed is an integer
    print(f"Horizontal: {horizspeed}")

def is_caps_lock_on():
    return True if ctypes.windll.user32.GetKeyState(0x14) & 1 else False

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
move_mouse_lock = threading.Lock()

# Main function for recoil
def start_moving():
    global moving
    def move_mouse():
        global moving
        if not moving:
            print("Started moving mouse")
            moving = True
        while both_buttons_held and is_caps_lock_on() and listener_active:
            pydirectinput.moveRel(horiz_speed, vert_speed, relative=True, duration=sleep_duration, disable_mouse_acceleration=True, _pause=False, attempt_pixel_perfect=True)
        if moving:
            print("Stopped moving mouse")
            moving = False
    with move_mouse_lock:
        if not moving:
            threading.Thread(target=move_mouse, daemon=True).start()

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
root.title("6Recoil Pre-Release Alpha")
root.geometry("350x190")  # Set the window size
sv_ttk.set_theme("dark")  # Set the theme to dark
root.attributes("-topmost", True)  # Keep the window on top
root.resizable(False, False)  # Disable resizing
root.iconbitmap(resource_path("icon.ico"))  # Set the custom icon

# Create a frame for padding
frame = ttk.Frame(root, padding="10")
frame.pack(fill=tk.BOTH, expand=True)

vert_input_var = tk.IntVar()
vert_input_label = ttk.Label(frame, text="Vertical Speed:")
vert_input_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
vert_input = ttk.Entry(frame)
vert_input.insert(0, int(vert_speed))  # Set default vertical speed in entry
vert_input.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
vert_input.bind("<KeyRelease>", lambda event: set_vert_speed(vert_input.get()))

horiz_input_var = tk.IntVar()
horiz_input_label = ttk.Label(frame, text="Horizontal Speed:")
horiz_input_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
horiz_input = ttk.Entry(frame)
horiz_input.insert(0, int(horiz_speed))  # Set default vertical speed in entry
horiz_input.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
horiz_input.bind("<KeyRelease>", lambda event: set_horiz_speed(horiz_input.get()))

# Create a label and entry for sleep duration
sleep_duration_label = ttk.Label(frame, text="Set RPM:")
sleep_duration_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

sleep_duration_entry = ttk.Entry(frame)
sleep_duration_entry.insert(0, int(sleep_duration))
sleep_duration_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

def update_sleep_duration(*args):
    try:
        set_sleep_duration(60/int(sleep_duration_entry.get()))
    except ValueError:
        pass  # Ignore invalid input

sleep_duration_entry.bind("<KeyRelease>", update_sleep_duration)

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
    global listener_thread, mouse_listener
    if listener_active:
        stop_mouse_movement()
    else:
        start_mouse_movement()
        listener_thread = threading.Thread(target=run_listener)
        listener_thread.start()

def run_listener():
    global mouse_listener
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

toggle_button = ttk.Button(frame, text="Start", command=toggle_program)
toggle_button.grid(row=3, column=0, columnspan=4, padx=5, pady=5, ipadx=135, sticky=tk.W)

# Run the GUI loop
root.mainloop()