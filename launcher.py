import tkinter as tk
from tkinter import messagebox, colorchooser
import json
from urllib.request import urlopen, Request
from urllib.error import URLError
import os
import sys
import tempfile
import subprocess
import shutil
import time

CURRENT_VERSION = "1.3.2"
VERSION_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main/version.json"
LAUNCHER_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main/launcher.py"
SETTINGS_FILE = os.path.join(os.environ.get("APPDATA", tempfile.gettempdir()), "VillagerLauncher", "settings.json")

THEMES = {
    "Villager Green": {"bg":"#101810","panel":"#182418","fg":"#FFFFFF","muted":"#AFC3AF","accent":"#55AA55","button":"#2D442D","icons":{"mods":"🧩","profile":"👤","launcher":"🧑‍🌾","settings":"⚙️"}},
    "Midnight": {"bg":"#0B1020","panel":"#141B31","fg":"#FFFFFF","muted":"#AAB6D3","accent":"#667EEA","button":"#29365B","icons":{"mods":"🔷","profile":"👤","launcher":"🌙","settings":"⚙️"}},
    "Sky": {"bg":"#DCEFF8","panel":"#F7FCFF","fg":"#173042","muted":"#5C7180","accent":"#3A91C9","button":"#C7E0ED","icons":{"mods":"☁️","profile":"👤","launcher":"☀️","settings":"⚙️"}},
    "Nether": {"bg":"#180C0C","panel":"#2A1212","fg":"#FFFFFF","muted":"#D0A8A8","accent":"#C84B4B","button":"#542626","icons":{"mods":"🔥","profile":"👤","launcher":"💀","settings":"⚙️"}},
    "Ocean": {"bg":"#071820","panel":"#0D2833","fg":"#FFFFFF","muted":"#9FC5D0","accent":"#38A7C7","button":"#1B4655","icons":{"mods":"🌊","profile":"👤","launcher":"🐟","settings":"⚙️"}}
}
current_theme_name = "Villager Green"
custom_theme = None

def load_settings():
    global current_theme_name, custom_theme
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        name = data.get("theme")
        if name in THEMES:
            current_theme_name = name
        elif name == "Custom" and isinstance(data.get("custom_theme"), dict):
            custom_theme = data["custom_theme"]
            current_theme_name = "Custom"
    except (OSError, json.JSONDecodeError):
        pass

def save_settings():
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        data = {"theme": current_theme_name}
        if current_theme_name == "Custom" and custom_theme:
            data["custom_theme"] = custom_theme
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except OSError:
        pass

def finish_update_from_temp(target_file):
    source_file = os.path.abspath(sys.argv[0])
    target_file = os.path.abspath(target_file)
    time.sleep(2)
    for _ in range(30):
        try:
            shutil.copy2(source_file, target_file)
            subprocess.Popen([sys.executable, target_file], close_fds=True)
            try:
                os.remove(source_file)
            except OSError:
                pass
            return
        except OSError:
            time.sleep(1)

def get_theme():
    if current_theme_name == "Custom" and custom_theme:
        return custom_theme
    return THEMES[current_theme_name]

def get_latest_version():
    request = Request(VERSION_URL + "?t=" + str(time.time_ns()), headers={"User-Agent":"Villager-Launcher"})
    with urlopen(request, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("version")

def download_update():
    request = Request(LAUNCHER_URL + "?t=" + str(time.time_ns()), headers={"User-Agent":"Villager-Launcher"})
    with urlopen(request, timeout=15) as response:
        new_launcher = response.read()
    if not new_launcher:
        raise ValueError("Downloaded update is empty.")
    temp_file = os.path.join(tempfile.gettempdir(), "villager_launcher_update.py")
    with open(temp_file, "wb") as file:
        file.write(new_launcher)
    return temp_file

def install_update(temp_file):
    current_file = os.path.abspath(sys.argv[0])
    subprocess.Popen([sys.executable, temp_file, "--install-update", current_file], creationflags=subprocess.CREATE_NO_WINDOW, close_fds=True)
    root.destroy()

def repair_and_restart():
    try:
        status.configure(text="Checking launcher updater...")
        update_button.configure(state="disabled")
        repair_button.configure(state="disabled")
        root.update_idletasks()
        latest_version = get_latest_version()
        if not latest_version:
            raise ValueError("Version information is missing.")
        temp_file = os.path.join(tempfile.gettempdir(), "villager_launcher_update.py")
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except OSError:
            pass
        fresh_file = download_update()
        status.configure(text=f"Updater check passed • restarting with {latest_version}...")
        root.update_idletasks()
        time.sleep(1)
        install_update(fresh_file)
    except Exception as error:
        status.configure(text="Repair check failed")
        messagebox.showerror("Repair Error", f"Villager Launcher checked the updater but could not repair it.\n\n{error}")
        try:
            repair_button.configure(state="normal")
            update_button.configure(state="normal")
        except tk.TclError:
            pass

def check_for_updates():
    status.configure(text="Checking for updates...")
    update_button.configure(state="disabled")
    root.update_idletasks()
    try:
        latest_version = get_latest_version()
        if not latest_version:
            raise ValueError("Version information is missing.")
        if latest_version == CURRENT_VERSION:
            status.configure(text="Up to date ✓")
            messagebox.showinfo("Updates", f"Villager Launcher is up to date!\n\nVersion {CURRENT_VERSION}")
            return
        status.configure(text=f"Downloading {latest_version}...")
        root.update_idletasks()
        temp_file = download_update()
        answer = messagebox.askyesno("Update Available", f"Version {latest_version} is available!\n\nCurrent version: {CURRENT_VERSION}\nNew version: {latest_version}\n\nInstall the update now?")
        if answer:
            status.configure(text=f"Installing {latest_version}...")
            root.update_idletasks()
            install_update(temp_file)
        else:
            status.configure(text="Update canceled")
    except (URLError, TimeoutError) as error:
        status.configure(text="Update failed")
        messagebox.showerror("Update Error", f"Could not connect to the update server.\n\n{error}")
    except (json.JSONDecodeError, ValueError) as error:
        status.configure(text="Invalid update")
        messagebox.showerror("Update Error", f"The update information is invalid.\n\n{error}")
    except Exception as error:
        status.configure(text="Update failed")
        messagebox.showerror("Update Error", f"Something went wrong.\n\n{error}")
    finally:
        try:
            if root.winfo_exists() and update_button.winfo_exists():
                update_button.configure(state="normal")
        except tk.TclError:
            pass

def minecraft_directory_exists():
    appdata = os.environ.get("APPDATA")
    return bool(appdata and os.path.isdir(os.path.join(appdata, ".minecraft")))

def open_mods():
    if not minecraft_directory_exists():
        messagebox.showerror("Mods Unavailable", "Can't access Minecraft.\n\nVillager Launcher could not find a Minecraft installation. You need an original Minecraft installation before mods can be accessed.")
        return
    messagebox.showinfo("Mods", "Minecraft installation detected.\n\nThe Mods browser is ready for the next module.")

def open_profile():
    messagebox.showinfo("Profile", "Profile\n\nNo Minecraft account is connected yet.")

def open_launcher_page():
    messagebox.showinfo("Launcher", f"Villager Launcher {CURRENT_VERSION}\n\nManual updates are enabled.\nAutomatic updates are disabled.")

def open_diagnostics():
    appdata = os.environ.get("APPDATA", "Not found")
    mc_path = os.path.join(appdata, ".minecraft") if appdata != "Not found" else "Not found"
    status_text = "Detected" if os.path.isdir(mc_path) else "Not detected"
    messagebox.showinfo("Diagnostics", f"Villager Launcher {CURRENT_VERSION}\n\nLauncher file:\n{os.path.abspath(sys.argv[0])}\n\nMinecraft folder:\n{mc_path}\n\nMinecraft status: {status_text}\n\nUpdate mode: Manual")

def apply_theme():
    theme = get_theme()
    root.configure(bg=theme["bg"])
    panel.configure(bg=theme["panel"])
    topbar.configure(bg=theme["panel"])
    center.configure(bg=theme["panel"])
    title.configure(bg=theme["panel"], fg=theme["fg"])
    subtitle.configure(bg=theme["panel"], fg=theme["fg"])
    version.configure(bg=theme["panel"], fg=theme["muted"])
    status.configure(bg=theme["panel"], fg=theme["muted"])
    minecraft_status.configure(bg=theme["panel"], fg=theme["muted"])
    nav_frame.configure(bg=theme["panel"])
    for button, key in zip([mods_button, profile_button, launcher_button], ["mods", "profile", "launcher"]):
        button.configure(bg=theme["button"], fg=theme["fg"], activebackground=theme["accent"], activeforeground=theme["fg"], text=f"{theme['icons'][key]}  {key.upper()}")
    settings_button.configure(bg=theme["button"], fg=theme["fg"], activebackground=theme["accent"], activeforeground=theme["fg"])
    play_button.configure(bg=theme["accent"], fg=theme["fg"], activebackground=theme["accent"], activeforeground=theme["fg"])
    update_button.configure(bg=theme["button"], fg=theme["fg"], activebackground=theme["accent"], activeforeground=theme["fg"])
    repair_button.configure(bg=theme["button"], fg=theme["fg"], activebackground=theme["accent"], activeforeground=theme["fg"])
    diagnostics_button.configure(bg=theme["button"], fg=theme["fg"], activebackground=theme["accent"], activeforeground=theme["fg"])

def create_custom_theme():
    global custom_theme, current_theme_name
    base = get_theme()
    selected = colorchooser.askcolor(title="Choose custom launcher color", initialcolor=base["accent"])
    if not selected[1]:
        return
    custom_theme = dict(base)
    custom_theme["accent"] = selected[1]
    custom_theme["button"] = selected[1]
    custom_theme["icons"] = dict(base["icons"])
    current_theme_name = "Custom"
    save_settings()
    apply_theme()

def open_settings():
    settings = tk.Toplevel(root)
    settings.title("Villager Launcher Settings")
    settings.geometry("440x500")
    settings.resizable(False, False)
    theme = get_theme()
    settings.configure(bg=theme["panel"])
    tk.Label(settings, text="⚙️ SETTINGS", font=("Segoe UI",22,"bold"), bg=theme["panel"], fg=theme["fg"]).pack(pady=(25,5))
    tk.Label(settings, text="Choose a launcher theme", font=("Segoe UI",11), bg=theme["panel"], fg=theme["muted"]).pack(pady=(0,15))
    def choose(name):
        global current_theme_name
        current_theme_name = name
        save_settings()
        apply_theme()
        settings.destroy()
    for name in THEMES:
        tk.Button(settings, text=name, font=("Segoe UI",11,"bold"), width=25, relief="flat", bg=theme["button"], fg=theme["fg"], command=lambda n=name: choose(n)).pack(pady=4)
    tk.Button(settings, text="🎨 Custom Theme", font=("Segoe UI",11,"bold"), width=25, relief="flat", bg=theme["button"], fg=theme["fg"], command=lambda: [create_custom_theme(), settings.destroy()]).pack(pady=(12,5))
    tk.Button(settings, text="🛠️ Diagnostics", font=("Segoe UI",11,"bold"), width=25, relief="flat", bg=theme["button"], fg=theme["fg"], command=open_diagnostics).pack(pady=8)
    tk.Label(settings, text="Themes are saved automatically.\nThemes also change the launcher icons.", font=("Segoe UI",9), bg=theme["panel"], fg=theme["muted"]).pack(pady=12)

def play():
    if not minecraft_directory_exists():
        messagebox.showinfo("Minecraft Required", "You need to own Minecraft Java Edition to play using Villager Launcher.")
        return
    messagebox.showinfo("Minecraft", "Minecraft installation detected. Launch integration will be added next.")

if len(sys.argv) >= 3 and sys.argv[1] == "--install-update":
    finish_update_from_temp(sys.argv[2])
    raise SystemExit

load_settings()
root = tk.Tk()
root.title(f"Villager Launcher {CURRENT_VERSION}")
root.geometry("1000x660")
root.resizable(False, False)
panel = tk.Frame(root)
panel.pack(fill="both", expand=True, padx=20, pady=20)
topbar = tk.Frame(panel)
topbar.pack(fill="x", padx=20, pady=(18,10))
nav_frame = tk.Frame(topbar)
nav_frame.pack(side="right")
mods_button = tk.Button(nav_frame, text="🧩  MODS", font=("Segoe UI",10,"bold"), width=12, relief="flat", command=open_mods)
mods_button.pack(side="left", padx=4)
profile_button = tk.Button(nav_frame, text="👤  PROFILE", font=("Segoe UI",10,"bold"), width=12, relief="flat", command=open_profile)
profile_button.pack(side="left", padx=4)
launcher_button = tk.Button(nav_frame, text="🧑‍🌾  LAUNCHER", font=("Segoe UI",10,"bold"), width=13, relief="flat", command=open_launcher_page)
launcher_button.pack(side="left", padx=4)
center = tk.Frame(panel)
center.pack(fill="both", expand=True)
title = tk.Label(center, text="VILLAGER LAUNCHER", font=("Segoe UI",36,"bold"))
title.pack(pady=(70,5))
subtitle = tk.Label(center, text="Your Minecraft Java launcher", font=("Segoe UI",14))
subtitle.pack()
version = tk.Label(center, text=f"Version {CURRENT_VERSION}", font=("Segoe UI",10))
version.pack(pady=(8,15))
minecraft_status = tk.Label(center, text=("🟢 Minecraft installation detected" if minecraft_directory_exists() else "⚪ Minecraft installation not detected"), font=("Segoe UI",11,"bold"))
minecraft_status.pack(pady=(0,15))
play_button = tk.Button(center, text="▶  PLAY", font=("Segoe UI",18,"bold"), width=18, height=2, relief="flat", command=play)
play_button.pack(pady=5)
update_button = tk.Button(center, text="🔄  Check for Updates", font=("Segoe UI",11,"bold"), width=24, relief="flat", command=check_for_updates)
update_button.pack(pady=5)
repair_button = tk.Button(center, text="🧰  Fix Update & Restart", font=("Segoe UI",11,"bold"), width=24, relief="flat", command=repair_and_restart)
repair_button.pack(pady=5)
diagnostics_button = tk.Button(center, text="🛠️  Diagnostics", font=("Segoe UI",10,"bold"), width=24, relief="flat", command=open_diagnostics)
diagnostics_button.pack(pady=5)
status = tk.Label(center, text="Ready", font=("Segoe UI",9))
status.pack(pady=10)
settings_button = tk.Button(panel, text="⚙️  SETTINGS", font=("Segoe UI",10,"bold"), width=14, relief="flat", command=open_settings)
settings_button.place(relx=0.02, rely=0.96, anchor="sw")
# Reserved bottom-right area for the future “Download Other Great Launcher” button.
apply_theme()
root.mainloop()
