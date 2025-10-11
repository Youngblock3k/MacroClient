import threading
import time
import tkinter as tk
from pynput import keyboard
import ctypes

# Windows API setup for SendInput
SendInput = ctypes.windll.user32.SendInput

# Key codes for E and R
KEY_E = 0x45
KEY_R = 0x52

running = False
start_time = None
window = None
label = None

# Structures for Windows key events
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ki", KeyBdInput)]

def press_key(hexKeyCode):
    x = Input(type=1, ki=KeyBdInput(wVk=hexKeyCode, wScan=0, dwFlags=0, time=0, dwExtraInfo=None))
    SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def release_key(hexKeyCode):
    x = Input(type=1, ki=KeyBdInput(wVk=hexKeyCode, wScan=0, dwFlags=2, time=0, dwExtraInfo=None))
    SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def macro():
    global running
    while running:
        press_key(KEY_E)
        release_key(KEY_E)
        press_key(KEY_R)
        release_key(KEY_R)
        time.sleep(1)

def update_timer():
    global running, start_time, label
    if running and label:
        elapsed = int(time.time() - start_time)
        label.config(text=f"Macro running: {elapsed} seconds")
        root.after(1000, update_timer)  # schedule next update

def create_window():
    global window, label
    if window is None:
        window = tk.Toplevel(root)
        window.title("Macro Timer")
        window.geometry("250x100")
        window.attributes("-topmost", True)
        label = tk.Label(window, text="Macro running: 0 seconds", font=("Arial", 12))
        label.pack(expand=True)
        window.protocol("WM_DELETE_WINDOW", toggle_macro)
        update_timer()

def destroy_window():
    global window, label
    if window:
        window.destroy()
        window = None
        label = None

def toggle_macro():
    global running, start_time
    if running:
        running = False
        destroy_window()
        status_label.config(text="Inactive", fg="red")
        print("Macro stopped")
    else:
        running = True
        start_time = time.time()
        print("Macro started")
        threading.Thread(target=macro, daemon=True).start()
        create_window()
        status_label.config(text="Active", fg="lime")

def stop_all():
    global running
    running = False
    destroy_window()
    print("Exiting...")
    root.quit()

def on_press(key):
    try:
        if key == keyboard.Key.f6:
            root.after(0, toggle_macro)  # safely toggle macro from main thread
        elif key == keyboard.Key.esc:
            root.after(0, stop_all)     # safely stop from main thread
            return False
    except Exception as e:
        print("Error:", e)

# Main GUI root window (status display)
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.9)
root.configure(bg="black")

status_label = tk.Label(root, text="Inactive", font=("Arial", 14, "bold"),
                 fg="red", bg="black")
status_label.pack(padx=10, pady=5)
root.geometry("+40+40")

print("Press F6 to start/stop the macro. Press ESC to quit.")

# Start the keyboard listener in a separate thread
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Run the Tkinter event loop in the main thread
root.mainloop()
