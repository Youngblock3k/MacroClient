from ahk import AHK
import threading, time
import keyboard
import tkinter as tk
from tkinter import messagebox

ahk = AHK(executable_path=r"C:\Users\excee\Desktop\v1.1.37.02\AutoHotkeyU64.exe")

spinning = False
start_time = None
spin_thread = None

# 24 directions for a very big smooth circle (~50m radius)
circle_pattern = [
    ('w', None, 0.6),
    ('w', 'd', 0.6),
    ('d', None, 0.6),
    ('s', 'd', 0.6),
    ('s', None, 0.6),
    ('s', 'a', 0.6),
    ('a', None, 0.6),
    ('w', 'a', 0.6),
    ('w', None, 0.6),
    ('w', 'd', 0.6),
    ('d', None, 0.6),
    ('s', 'd', 0.6),
    ('s', None, 0.6),
    ('s', 'a', 0.6),
    ('a', None, 0.6),
    ('w', 'a', 0.6),
    ('w', None, 0.6),
    ('w', 'd', 0.6),
    ('d', None, 0.6),
    ('s', 'd', 0.6),
    ('s', None, 0.6),
    ('s', 'a', 0.6),
    ('a', None, 0.6),
    ('w', 'a', 0.6)
]

def spin_around():
    global spinning
    while spinning:
        for keys in circle_pattern:
            if not spinning:
                break
            k1, k2, duration = keys
            if k1: ahk.key_down(k1)
            if k2: ahk.key_down(k2)
            time.sleep(duration)
            if k1: ahk.key_up(k1)
            if k2: ahk.key_up(k2)
            time.sleep(0.05)

def toggle_spin():
    global spinning, start_time, spin_thread
    spinning = not spinning
    if spinning:
        start_time = time.time()
        label.config(text="Spinning...", fg="green")
        spin_thread = threading.Thread(target=spin_around, daemon=True)
        spin_thread.start()
    else:
        spinning = False
        release_keys()
        label.config(text="Inactive", fg="red")

def release_keys():
    for k in ['w', 'a', 's', 'd']:
        ahk.key_up(k)

def close_macro():
    global spinning
    spinning = False
    release_keys()
    # Show popup before closing
    messagebox.showinfo("Macro Closed", "THANK U FOR USING Game's MACRO")
    root.destroy()

# GUI floating label
root = tk.Tk()
root.overrideredirect(True)  # Remove window frame
root.attributes("-topmost", True)
root.attributes("-alpha", 0.9)
root.configure(bg="black")

label = tk.Label(root, text="Inactive", font=("Arial", 14, "bold"),
                 fg="red", bg="black")
label.pack(padx=10, pady=5)

root.geometry("+40+40")  # top-left corner

def update_timer():
    if spinning:
        elapsed = int(time.time() - start_time)
        label.config(text=f"Spinning... {elapsed}s")
        root.after(1000, update_timer)
    else:
        label.config(text="Inactive", fg="red")

root.protocol("WM_DELETE_WINDOW", close_macro)

# Hotkeys
keyboard.add_hotkey('f2', toggle_spin)  # start/stop spinning
keyboard.add_hotkey('f3', close_macro)  # fully close macro with popup

root.after(1000, update_timer)
root.mainloop()
