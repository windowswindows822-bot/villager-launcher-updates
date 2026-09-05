import tkinter as tk
from tkinter import messagebox, colorchooser
import json
from urllib.request import urlopen, Request
from urllib.error import URLError
import os
import sys
import tempfile
import subprocess

CURRENT_VERSION = "1.2.0"

VERSION_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main/version.json"
LAUNCHER_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main/launcher.py"

THEMES = {
    "Villager Green": {
        "bg": "#101810", "panel": "#182418", "card": "#223322",
        "fg": "#FFFFFF", "muted": "#AFC3AF", "accent": "#55AA55", "button": "#2D442D",
        "icons": {"mods": "🧩", "profile": "👤", "launcher": "🧑‍🌾", "settings": "⚙️"}
    },
    "Midnight": {
        "bg": "#0B1020", "panel": "#141B31", "card": "#202A46",
        "fg": "#FFFFFF", "muted": "#AAB6D3", "accent": "#667EEA", "button": "#29365B",
        "icons": {"mods": "🔷", "profile": "👤", "launcher": "🌙", "settings": "⚙️"}
    },
    "Sky": {
        "bg": "#DCEFF8", "panel": "#F7FCFF", "card": "#D4EAF4",
        "fg": "#173042", "muted": "#5C7180", "accent": "#3A91C9", "button": "#C7E0ED",
        "icons": {"mods": "☁️", "profile": "👤", "launcher": "☀️", "settings": "⚙️"}
    },
    "Nether": {
        "bg": "#180C0C", "panel": "#2A1212", "card": "#3B1B1B",
        "fg": "#FFFFFF", "muted": "#D0A8A8", "accent": "#C84B4B", "button": "#542626",
        "icons": {"mods": "🔥", "profile": "👤", "launcher": "💀", "settings": "⚙️"}
    },
    "Ocean": {
        "bg": "#071820", "panel": "#0D2833", "card": "#123B49",
        "fg": "#FFFFFF", "muted": "#9FC5D0", "accent": "#38A7C7", "button": "#1B4655",
        "icons": {"mods": "🌊", "profile": "👤", "launcher": "🐟", "settings": "⚙️"}
    }
}

current_theme_name = "Villager Green"
custom_theme = None


def get_theme():
    if current_theme_name == "Custom" and custom_theme:
        return custom_theme
    return THEMES[current_theme_name]


def get_latest_version():
    request = Request(VERSION_URL, headers={"User-Agent": "Villager-Launcher"})
    with urlopen(request, timeout=5) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("version")


def download_update():
    request = Request(LAUNCHER_URL, headers={"User-Agent": "Villager-Launcher"})
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
    new_launcher = current_file + ".new"
    with open(temp_file, "rb") as source, open(new_launcher, "wb") as destination:
        destination.write(source.read())

    updater_file = os.path.join(tempfile.gettempdir(), "villager_launcher_updater.bat")
    bat_contents = f'''@echo off
ping 127.0.0.1 -n 3 >nul
move /Y "{new_launcher}" "{current_file}" >nul
start "" "{sys.executable}" "{current_file}"
del "%~f0"
'''
    with open(updater_file, "w", encoding="utf-8") as file:
        file.write(bat_contents)

    subprocess.Popen(["cmd", "/c", updater_file], creationflags=subprocess.CREATE_NO_WINDOW)
    root.destroy()


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
        answer = messagebox.askyesno(
            "Update Available",
            f"Version {latest_version} is available!\n\n"
            f"Current version: {CURRENT_VERSION}\n"
            f"New version: {latest_version}\n\nInstall the update now?"
        )
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
        update_button.configure(state="normal")


def minecraft_directory_exists():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return False
    minecraft_dir = os.path.join(appdata, ".minecraft")
    return os.path.isdir(minecraft_dir)


def open_mods():
    if not minecraft_directory_exists():
        messagebox.showerror(
            "Mods Unavailable",
            "Can't access Minecraft.\n\n"
            "Villager Launcher could not find a Minecraft installation. "
            "You need an original Minecraft installation before mods can be accessed."
        )
        return
    messagebox.showinfo(
        "Mods",
        "Minecraft installation detected.\n\n"
        "The Mods browser is ready for the next module."
    )


def open_profile():
    messagebox.showinfo("Profile", "Profile\n\nNo Minecraft account is connected yet.")


def open_launcher_page():
    messagebox.showinfo("Launcher", f"Villager Launcher {CURRENT_VERSION}\n\nReady to launch Minecraft Java Edition.")


def apply_theme():
    theme = get_theme()
    root.configure(bg=theme["bg"])
    panel.configure(bg=theme["panel"])
    topbar.configure(bg=theme["panel"])
    center.configure(bg=theme["panel"])
    title.configure(bg=theme["panel"], fg=theme["fg"])
    subtitle.configure(bg=theme["panel"], fg=theme["muted"])
    version.configure(bg=theme["panel"], fg=theme["muted"])
    status.configure(bg=theme["panel"], fg=theme["muted"])
    nav_frame.configure(bg=theme["panel"])
    nav_buttons = [mods_button, profile_button, launcher_button]
    keys = ["mods", "profile", "launcher"]
    for button, key in zip(nav_buttons, keys):
        button.configure(bg=theme["button"], fg=theme["fg"], activebackground=theme["accent"], activeforeground=theme["fg"], text=f"{theme['icons'][key]}  {key.upper()}")
    settings_button.configure(bg=theme["button"], fg=theme["fg"], activebackground=theme["accent"], activeforeground=theme["fg"], text=f"{theme['icons']['settings']}  SETTINGS")
    play_button.configure(bg=theme["accent"], fg=theme["fg"], activebackground=theme["accent"], activeforeground=theme["fg"])
    update_button.configure(bg=theme["button"], fg=theme["fg"], activebackground=theme["accent"], activeforeground=theme["fg"])


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
    apply_theme()


def open_settings():
    settings = tk.Toplevel(root)
    settings.title("Villager Launcher Settings")
    settings.geometry("440x420")
    settings.resizable(False, False)
    theme = get_theme()
    settings.configure(bg=theme["panel"])

    heading = tk.Label(settings, text="⚙️ SETTINGS", font=("Segoe UI", 22, "bold"), bg=theme["panel"], fg=theme["fg"])
    heading.pack(pady=(25, 5))
    tk.Label(settings, text="Choose a launcher theme", font=("Segoe UI", 11), bg=theme["panel"], fg=theme["muted"]).pack(pady=(0, 15))

    def choose(name):
        global current_theme_name
        current_theme_name = name
        apply_theme()
        settings.destroy()

    for name in THEMES:
        button = tk.Button(settings, text=name, font=("Segoe UI", 11, "bold"), width=25, relief="flat", bg=theme["button"], fg=theme["fg"], command=lambda n=name: choose(n))
        button.pack(pady=4)

    custom = tk.Button(settings, text="🎨 Custom Theme", font=("Segoe UI", 11, "bold"), width=25, relief="flat", bg=theme["button"], fg=theme["fg"], command=lambda: [create_custom_theme(), settings.destroy()])
    custom.pack(pady=(12, 5))

    tk.Label(settings, text="Themes also change the launcher icons.", font=("Segoe UI", 9), bg=theme["panel"], fg=theme["muted"]).pack(pady=12)


def play():
    if not minecraft_directory_exists():
        messagebox.showinfo(
            "Minecraft Required",
            "You need to own Minecraft Java Edition to play using Villager Launcher."
        )
        return
    messagebox.showinfo("Minecraft", "Minecraft installation detected. Launch integration will be added next.")


root = tk.Tk()
root.title(f"Villager Launcher {CURRENT_VERSION}")
root.geometry("1000x620")
root.resizable(False, False)

panel = tk.Frame(root)
panel.pack(fill="both", expand=True, padx=20, pady=20)

topbar = tk.Frame(panel)
topbar.pack(fill="x", padx=20, pady=(18, 10))

nav_frame = tk.Frame(topbar)
nav_frame.pack(side="right")

mods_button = tk.Button(nav_frame, text="🧩  MODS", font=("Segoe UI", 10, "bold"), width=12, relief="flat", command=open_mods)
mods_button.pack(side="left", padx=4)
profile_button = tk.Button(nav_frame, text="👤  PROFILE", font=("Segoe UI", 10, "bold"), width=12, relief="flat", command=open_profile)
profile_button.pack(side="left", padx=4)
launcher_button = tk.Button(nav_frame, text="🧑‍🌾  LAUNCHER", font=("Segoe UI", 10, "bold"), width=13, relief="flat", command=open_launcher_page)
launcher_button.pack(side="left", padx=4)

center = tk.Frame(panel)
center.pack(fill="both", expand=True)

title = tk.Label(center, text="VILLAGER LAUNCHER", font=("Segoe UI", 36, "bold"))
title.pack(pady=(105, 5))
subtitle = tk.Label(center, text="Your Minecraft Java launcher", font=("Segoe UI", 14))
subtitle.pack()
version = tk.Label(center, text=f"Version {CURRENT_VERSION}", font=("Segoe UI", 10))
version.pack(pady=(8, 25))

play_button = tk.Button(center, text="▶  PLAY", font=("Segoe UI", 18, "bold"), width=18, height=2, relief="flat", command=play)
play_button.pack(pady=8)

update_button = tk.Button(center, text="🔄  Check for Updates", font=("Segoe UI", 11), width=24, relief="flat", command=check_for_updates)
update_button.pack(pady=8)

status = tk.Label(center, text=f"Ready • Villager Launcher {CURRENT_VERSION}", font=("Segoe UI", 10))
status.pack(pady=15)

settings_button = tk.Button(panel, text="⚙️  SETTINGS", font=("Segoe UI", 10, "bold"), width=15, relief="flat", command=open_settings)
settings_button.pack(side="left", padx=20, pady=(0, 15))

apply_theme()
root.mainloop()
