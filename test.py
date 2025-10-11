import pyautogui
import tkinter as tk
from pynput import keyboard
import threading
import time

# ---------------- Settings ----------------
CLICK_POSITION = (600, 400)  # Replace with your bubble button coordinates
CLICK_INTERVAL = 0.255       # 255 ms

# ---------------- Global State ----------------
macro_active = False

# ---------------- Functions ----------------
def run_macro_precise():
    global macro_active
    next_click = time.perf_counter()
    while True:
        now = time.perf_counter()
        if macro_active and now >= next_click:
            pyautogui.click(CLICK_POSITION)
            next_click = now + CLICK_INTERVAL

def toggle_macro():
    global macro_active
    macro_active = not macro_active
    status_label.config(
        text="ACTIVE" if macro_active else "INACTIVE",
        fg="green" if macro_active else "red"
    )

# ---------------- Keyboard Listener ----------------
def on_press(key):
    try:
        if key == keyboard.Key.f2:  # F2 toggles macro
            toggle_macro()
    except AttributeError:
        pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

# ---------------- GUI ----------------
root = tk.Tk()
root.title("BGSI Auto Clicker")
root.geometry("200x50")
root.attributes("-topmost", True)

status_label = tk.Label(root, text="INACTIVE", fg="red", font=("Segoe UI", 14, "bold"))
status_label.pack(pady=10, padx=10)

# ---------------- Start Macro Thread ----------------
threading.Thread(target=run_macro_precise, daemon=True).start()

root.mainloop()
