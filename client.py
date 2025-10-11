import tkinter as tk
from tkinter import ttk, messagebox
import sys, os, time, subprocess
import requests
from datetime import datetime

class MacroClient(tk.Tk):
    def __init__(self, icon_path):
        super().__init__()

        self.title("Macro Client")
        self.geometry("800x500")

        # Set window icon
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"⚠ Could not set icon: {e}")

        # State
        self.dark_mode = True
        self.active_macro = None
        self.macro_running = False
        self.start_time = None
        self.process = None  
        self.verified_until = None  
        self.gameboard_process = None
        self.gameboard_running = False

        # Styles
        self.style = ttk.Style(self)

        # Sidebar
        self.sidebar = tk.Frame(self, bg="#252526", width=200)
        self.sidebar.pack(side="left", fill="y")

        tk.Label(
            self.sidebar, 
            text="⚡ Macros", 
            bg="#252526", 
            fg="white", 
            font=("Segoe UI", 14, "bold")
        ).pack(pady=15)

        # Macro buttons
        self.macros = ["AutoHatch -1", "AutoBubble -2", "Autofish -3", "Auto-Collect -4"]
        for m in self.macros:
            ttk.Button(
                self.sidebar, text=m, command=lambda x=m: self.show_macro_ui(x)
            ).pack(fill="x", padx=10, pady=5)

        # Gameboard button
        ttk.Button(
            self.sidebar,
            text="🎮 Gameboard",
            command=lambda: self.show_gameboard_ui()
        ).pack(fill="x", padx=10, pady=5)

        # Discord Verification button
        self.verify_btn = ttk.Button(
            self.sidebar,
            text="🔑 Verify Discord",
            command=lambda: self.open_verification_ui()
        )
        self.verify_btn.pack(fill="x", padx=10, pady=5)

        # Timer Button (disabled display)
        self.timer_btn = ttk.Button(
            self.sidebar,
            text="⏳ Not Verified",
            state="disabled"
        )
        self.timer_btn.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            self.sidebar, text="🌗 Toggle Dark Mode", command=self.toggle_dark_mode
        ).pack(side="bottom", pady=15, padx=10, fill="x")

        ttk.Label(
            self.sidebar, text="Version: V0.1", font=("TkDefaultFont", 9, "bold")
        ).pack(side="bottom", pady=(0, 2))


        # Main area
        self.main_area = tk.Frame(self, bg="#1e1e1e")
        self.main_area.pack(side="right", expand=True, fill="both")

        # Apply dark mode
        self._apply_dark_mode()

        # Timer update loop
        self.update_timer_loop()

    # ---------------- Macro UI ----------------
    def show_macro_ui(self, macro_name):
        if not self.verified_until or datetime.utcnow() >= self.verified_until:
            messagebox.showwarning("⚠ Verification Required", "You must verify Discord before using this macro.")
            return

        self.active_macro = macro_name
        for widget in self.main_area.winfo_children():
            widget.destroy()

        tk.Label(
            self.main_area,
            text=f"{macro_name} Controls",
            bg="#1e1e1e" if self.dark_mode else "white",
            fg="white" if self.dark_mode else "black",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=20)

        self.start_stop_btn = tk.Button(
            self.main_area,
            text="START",
            bg="green",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            command=self.toggle_macro
        )
        self.start_stop_btn.pack(pady=10)

        tk.Button(
            self.main_area,
            text="EDIT",
            bg="yellow",
            fg="black",
            font=("Segoe UI", 12, "bold"),
        ).pack(pady=10)

    def toggle_macro(self):
        if not self.macro_running:  
            self.macro_running = True
            self.start_time = time.time()
            self.start_stop_btn.config(text="STOP", bg="red")

            script_map = {
                "AutoHatch": "auto-hatch.py",
                "AutoBubble": "auto-bubble.py",
                "Autofish": "auto-fish.py"
            }
            for key, file in script_map.items():
                if key in self.active_macro:
                    script_path = os.path.join(os.path.dirname(__file__), file)
                    self.process = subprocess.Popen([sys.executable, script_path])
                    break

        else:
            self.macro_running = False
            elapsed = int(time.time() - self.start_time)
            self.start_stop_btn.config(text="START", bg="green")

            if self.process:
                self.process.terminate()
                self.process = None

            self.show_popup(self.active_macro, elapsed)

    def show_popup(self, macro_name, elapsed_time):
        popup = tk.Toplevel(self)
        popup.title("Macro Summary")
        popup.geometry("250x150")
        popup.configure(bg="#2b2b2b")

        def start_move(event): popup.x, popup.y = event.x, event.y
        def stop_move(event): popup.x, popup.y = None, None
        def do_move(event):
            x = popup.winfo_x() + event.x - popup.x
            y = popup.winfo_y() + event.y - popup.y
            popup.geometry(f"+{x}+{y}")

        popup.bind("<Button-1>", start_move)
        popup.bind("<ButtonRelease-1>", stop_move)
        popup.bind("<B1-Motion>", do_move)

        tk.Label(popup, text="Macro Stopped", fg="white", bg="#2b2b2b", font=("Segoe UI", 12, "bold")).pack(pady=10)
        tk.Label(popup, text=f"Macro: {macro_name}", fg="yellow", bg="#2b2b2b", font=("Segoe UI", 10)).pack(pady=5)
        tk.Label(popup, text=f"Ran for: {elapsed_time} sec", fg="cyan", bg="#2b2b2b", font=("Segoe UI", 10)).pack(pady=5)

    # ---------------- Dark Mode ----------------
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self._apply_dark_mode()

    def _apply_dark_mode(self):
        if self.dark_mode:
            self.configure(bg="#1e1e1e")
            self.main_area.config(bg="#1e1e1e")
            self.style.theme_use("clam")
            self.style.configure("TButton", background="#2d2d30", foreground="white", padding=6, relief="flat")
        else:
            self.configure(bg="white")
            self.main_area.config(bg="white")
            self.style.theme_use("clam")
            self.style.configure("TButton", background="#f0f0f0", foreground="black", padding=6, relief="flat")

    # ---------------- Discord Verification ----------------
    def open_verification_ui(self):
        if self.verified_until and datetime.utcnow() < self.verified_until:
            messagebox.showinfo("Already Verified", "You are already verified until expiry.")
            return

        # Step 1: Ask for User ID first
        id_window = tk.Toplevel(self)
        id_window.title("User ID Verification")
        id_window.geometry("300x150")
        id_window.configure(bg="#1e1e1e" if self.dark_mode else "white")

        tk.Label(
            id_window,
            text="Enter your User ID:",
            bg="#1e1e1e" if self.dark_mode else "white",
            fg="white" if self.dark_mode else "black",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=10)

        id_entry = tk.Entry(id_window, font=("Segoe UI", 12))
        id_entry.pack(pady=5, padx=10, fill="x")

        def submit_id():
            user_id = id_entry.get().strip()
            if not user_id:
                return

            BOT_API_URL = "https://panel.gurgangmc.net/server/dc643c58"
            response = requests.post(f"{BOT_API_URL}/check_id", json={"user_id": user_id})
            try:
                data = response.json()
            except ValueError:
                messagebox.showerror(
                    "❌ Error",
                    f"Invalid response from server:\n{response.text[:200]}"
                )
                return



            try:

                # Step 1: Check ID
                response = requests.post(f"{BOT_API_URL}/check_id", json={"user_id": user_id})
                data = response.json()
                if data.get("status") != "success":
                    messagebox.showerror("❌ Invalid ID", data.get("message", "ID not found"))
                    return

                # Step 2: Request code from Discord bot
                response = requests.post(f"{BOT_API_URL}/get_code", json={"user_id": user_id})
                data = response.json()
                if data.get("status") != "success":
                    messagebox.showerror("❌ Error", data.get("message", "Could not send code"))
                    return

                messagebox.showinfo("✅ Code Sent", "Check your Discord DM for the verification code.")
                id_window.destroy()
                self.open_code_entry_ui(user_id)

            except Exception as e:
                messagebox.showerror("❌ Error", str(e))



## ---------------------
        tk.Button(id_window, text="NEXT", bg="green", fg="white", command=submit_id).pack(pady=5)

    def open_code_entry_ui(self, user_id):
        window = tk.Toplevel(self)
        window.title("Discord Verification")
        window.geometry("300x150")
        window.configure(bg="#1e1e1e" if self.dark_mode else "white")

        tk.Label(
            window,
            text="Enter Discord verification code:",
            bg="#1e1e1e" if self.dark_mode else "white",
            fg="white" if self.dark_mode else "black",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=10)

        code_entry = tk.Entry(window, font=("Segoe UI", 12))
        code_entry.pack(pady=5, padx=10, fill="x")

        def submit_code():
            code = code_entry.get().strip()
            if not code:
                return
            self.verify_discord_code(code, user_id, window)

        tk.Button(window, text="SUBMIT", bg="green", fg="white", command=submit_code).pack(pady=5)

    def verify_discord_code(self, code, user_id, window):
        BOT_API_URL = "https://panel.gurgangmc.net/server/dc643c58"

        try:
            response = requests.post(BOT_API_URL, json={"user_id": user_id, "code": code})
            data = response.json()

            if data.get("status") == "success":
                self.verified_until = datetime.fromisoformat(data['expiry'])
                self.verify_btn.config(state="disabled")
                messagebox.showinfo("✅ Verified", f"Access valid until {data['expiry']}")
                window.destroy()
            else:
                messagebox.showerror("❌ Failed", data.get("message", "Invalid code. Use the link: xxxx-xxxx-xxxx"))

        except requests.exceptions.ConnectionError:
            messagebox.showerror("❌ Error", "Could not connect to the verification server.")
    # ---------------- Timer ----------------
    def update_timer_loop(self):
        if self.verified_until:
            now = datetime.utcnow()
            if now < self.verified_until:
                remaining = self.verified_until - now
                minutes, seconds = divmod(remaining.seconds, 60)
                hours, minutes = divmod(minutes, 60)
                self.timer_btn.config(text=f"⏳ {hours:02}:{minutes:02}:{seconds:02} left")
            else:
                self.verified_until = None
                self.verify_btn.config(state="normal")
                self.timer_btn.config(text="⏳ Not Verified")

        self.after(1000, self.update_timer_loop)

    # ---------------- Gameboard ----------------
    def show_gameboard_ui(self):
        if not self.verified_until or datetime.utcnow() >= self.verified_until:
            messagebox.showwarning("⚠ Verification Required", "You must verify Discord before using the Gameboard.")
            return

        self.active_macro = "Gameboard"
        for widget in self.main_area.winfo_children():
            widget.destroy()

        tk.Label(
            self.main_area,
            text="Gameboard Controls",
            bg="#1e1e1e" if self.dark_mode else "white",
            fg="white" if self.dark_mode else "black",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=40)

        self.start_stop_btn = tk.Button(
            self.main_area,
            text="START",
            bg="green",
            fg="white",
            font=("Segoe UI", 12, "bold"),
            command=self.toggle_gameboard
        )
        self.start_stop_btn.pack(pady=10)

    def toggle_gameboard(self):
        if not self.gameboard_running:
            script_path = os.path.join(os.path.dirname(__file__), "MacroClient", "gameboard.py")
            if os.path.exists(script_path):
                self.gameboard_process = subprocess.Popen([sys.executable, script_path])
                self.start_stop_btn.config(text="STOP", bg="red")
                self.gameboard_running = True
            else:
                messagebox.showerror("❌ Error", f"{script_path} not found!")
        else:
            if self.gameboard_process:
                self.gameboard_process.terminate()
                self.gameboard_process = None
            self.start_stop_btn.config(text="START", bg="green")
            self.gameboard_running = False

# ---------------- Run ----------------
if __name__ == "__main__":
    icon_path = "icon.ico"  # Change to your icon path
    app = MacroClient(icon_path)
    app.mainloop()