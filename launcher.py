import tkinter as tk
from tkinter import messagebox
import json
from urllib.request import urlopen, Request
from urllib.error import URLError
import os
import sys
import tempfile
import subprocess

CURRENT_VERSION = "1.1.0"

VERSION_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main/version.json"
LAUNCHER_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main/launcher.py"


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
            f"New version: {latest_version}\n\n"
            "Install the update now?"
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


def play():
    messagebox.showinfo(
        "Minecraft Required",
        "You need to own Minecraft Java Edition to play using Villager Launcher."
    )


def change_theme():
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        root.configure(bg="#101820")
        panel.configure(bg="#18232F")
        title.configure(bg="#18232F", fg="white")
        version.configure(bg="#18232F", fg="#9FB3C8")
        edition.configure(bg="#18232F", fg="white")
        status.configure(bg="#18232F", fg="#9FB3C8")
        theme_button.configure(text="☀️ Light Theme", bg="#263646", fg="white")
        update_button.configure(bg="#263646", fg="white")
    else:
        root.configure(bg="#E9EEF2")
        panel.configure(bg="white")
        title.configure(bg="white", fg="#17202A")
        version.configure(bg="white", fg="#5D6D7E")
        edition.configure(bg="white", fg="#17202A")
        status.configure(bg="white", fg="#5D6D7E")
        theme_button.configure(text="🌙 Dark Theme", bg="#DDE5EC", fg="#17202A")
        update_button.configure(bg="#DDE5EC", fg="#17202A")


dark_mode = True

root = tk.Tk()
root.title("Villager Launcher 1.1.0")
root.geometry("900x560")
root.resizable(False, False)
root.configure(bg="#101820")

panel = tk.Frame(root, bg="#18232F")
panel.pack(fill="both", expand=True, padx=25, pady=25)

title = tk.Label(panel, text="🧑‍🌾 VILLAGER LAUNCHER", font=("Segoe UI", 28, "bold"), bg="#18232F", fg="white")
title.pack(pady=(40, 5))

version = tk.Label(panel, text=f"Version {CURRENT_VERSION} • UPDATE EDITION", font=("Segoe UI", 11), bg="#18232F", fg="#9FB3C8")
version.pack()

edition = tk.Label(panel, text="Minecraft Java Edition", font=("Segoe UI", 15), bg="#18232F", fg="white")
edition.pack(pady=(25, 10))

play_button = tk.Button(panel, text="▶  PLAY", font=("Segoe UI", 18, "bold"), width=18, height=2, bg="#55AA55", fg="white", relief="flat", command=play)
play_button.pack(pady=12)

update_button = tk.Button(panel, text="🔄  Check for Updates", font=("Segoe UI", 11), width=24, bg="#263646", fg="white", relief="flat", command=check_for_updates)
update_button.pack(pady=7)

theme_button = tk.Button(panel, text="☀️  Light Theme", font=("Segoe UI", 11), width=24, bg="#263646", fg="white", relief="flat", command=change_theme)
theme_button.pack(pady=7)

status = tk.Label(panel, text="Ready • Villager Launcher 1.1.0", font=("Segoe UI", 10), bg="#18232F", fg="#9FB3C8")
status.pack(pady=25)

root.mainloop()
