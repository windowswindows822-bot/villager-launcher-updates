# Villager Launcher 1.9.5 release bootstrap
import tkinter as tk
from tkinter import messagebox
import os, sys, json, tempfile, subprocess, shutil, time, re
from urllib.request import Request, urlopen

CURRENT_VERSION = "1.9.5"
BASE_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main"
VERSION_URL = BASE_URL + "/version.json"
LAUNCHER_URL = BASE_URL + "/launcher.py"

def vt(v):
    nums = re.findall(r"\d+", str(v))
    return tuple(int(x) for x in (nums + ["0","0","0"])[:3])

def get_update_info():
    req = Request(VERSION_URL + "?nocache=" + str(time.time_ns()), headers={"User-Agent":"Villager-Launcher/1.9.5"})
    with urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))

def download_latest():
    req = Request(LAUNCHER_URL + "?nocache=" + str(time.time_ns()), headers={"User-Agent":"Villager-Launcher/1.9.5"})
    with urlopen(req, timeout=30) as r:
        data = r.read()
    path = os.path.join(tempfile.gettempdir(), "villager_launcher_latest.py")
    with open(path, "wb") as f: f.write(data)
    return path

def install_update(source):
    target = os.path.abspath(sys.argv[0])
    helper = os.path.join(tempfile.gettempdir(), "villager_launcher_update_helper.py")
    code = '''import sys,time,shutil,subprocess,os
source,target=sys.argv[1],sys.argv[2]
time.sleep(1.2)
backup=target+".backup"
try:
    if os.path.exists(target): shutil.copy2(target,backup)
    shutil.copy2(source,target)
    subprocess.Popen([sys.executable,target])
except Exception:
    if os.path.exists(backup): shutil.copy2(backup,target)
'''
    with open(helper,"w",encoding="utf-8") as f: f.write(code)
    subprocess.Popen([sys.executable,helper,source,target], creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0), close_fds=True)

def check_updates():
    try:
        info=get_update_info()
        latest=str(info.get("version",CURRENT_VERSION))
        if vt(latest) <= vt(CURRENT_VERSION):
            messagebox.showinfo("Updates",f"Villager Launcher is up to date.\n\nVersion: {CURRENT_VERSION}")
            return
        beta="BETA / TESTING" if info.get("beta",False) else "RELEASE"
        if not messagebox.askyesno("Update Available",f"Villager Launcher {latest} is available.\n\nInstalled: {CURRENT_VERSION}\nAvailable: {latest}\nStatus: {beta}\n\nUpdate now?"):
            return
        source=download_latest()
        if not messagebox.askyesno("Ready to Update","The update downloaded successfully.\n\nThe launcher will close and restart with the new version.\n\nContinue?"):
            return
        install_update(source)
        root.destroy()
    except Exception as e:
        messagebox.showerror("Update Error",f"Could not check for updates.\n\n{e}")

def main():
    global root
    root=tk.Tk(); root.title("Villager Launcher 1.9.5"); root.geometry("720x430"); root.configure(bg="#0b120d")
    tk.Label(root,text="🧑‍🌾 Villager Launcher",font=("Segoe UI",25,"bold"),bg="#0b120d",fg="white").pack(pady=(55,8))
    tk.Label(root,text="Version 1.9.5 • RELEASE",font=("Segoe UI",12),bg="#0b120d",fg="#62c462").pack(pady=5)
    tk.Label(root,text="1.9.5 is released. Installer Wizard is intentionally coming later.",font=("Segoe UI",10),bg="#0b120d",fg="#a9b9aa").pack(pady=18)
    tk.Button(root,text="CHECK FOR UPDATES",command=check_updates,font=("Segoe UI",11,"bold"),bg="#2d442d",fg="white",relief="flat",padx=25,pady=12).pack(pady=10)
    root.mainloop()

if __name__=="__main__": main()
