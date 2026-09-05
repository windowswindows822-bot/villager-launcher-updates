import tkinter as tk
from tkinter import messagebox, colorchooser
import json, os, sys, tempfile, subprocess, shutil, time, re
from urllib.request import urlopen, Request
from urllib.error import URLError

CURRENT_VERSION = "1.3.6"
BASE_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main"
VERSION_URL = BASE_URL + "/version.json"
LAUNCHER_URL = BASE_URL + "/launcher.py"
COMMITS_URL = "https://api.github.com/repos/windowswindows822-bot/villager-launcher-updates/commits?path=launcher.py&per_page=30"
SETTINGS_FILE = os.path.join(os.environ.get("APPDATA", tempfile.gettempdir()), "VillagerLauncher", "settings.json")

THEMES = {
    "Villager Green":{"bg":"#101810","panel":"#182418","fg":"#FFFFFF","muted":"#AFC3AF","accent":"#55AA55","button":"#2D442D","icons":{"mods":"🧩","profile":"👤","launcher":"🧑‍🌾"}},
    "Midnight":{"bg":"#0B1020","panel":"#141B31","fg":"#FFFFFF","muted":"#AAB6D3","accent":"#667EEA","button":"#29365B","icons":{"mods":"🔷","profile":"👤","launcher":"🌙"}},
    "Sky":{"bg":"#DCEFF8","panel":"#F7FCFF","fg":"#173042","muted":"#5C7180","accent":"#3A91C9","button":"#C7E0ED","icons":{"mods":"☁️","profile":"👤","launcher":"☀️"}},
    "Nether":{"bg":"#180C0C","panel":"#2A1212","fg":"#FFFFFF","muted":"#D0A8A8","accent":"#C84B4B","button":"#542626","icons":{"mods":"🔥","profile":"👤","launcher":"💀"}},
    "Ocean":{"bg":"#071820","panel":"#0D2833","fg":"#FFFFFF","muted":"#9FC5D0","accent":"#38A7C7","button":"#1B4655","icons":{"mods":"🌊","profile":"👤","launcher":"🐟"}}
}
current_theme_name="Villager Green"
custom_theme=None

def load_settings():
    global current_theme_name, custom_theme
    try:
        with open(SETTINGS_FILE,"r",encoding="utf-8") as f: data=json.load(f)
        if data.get("theme") in THEMES: current_theme_name=data["theme"]
        elif data.get("theme")=="Custom" and isinstance(data.get("custom_theme"),dict):
            custom_theme=data["custom_theme"]; current_theme_name="Custom"
    except (OSError,json.JSONDecodeError): pass

def save_settings():
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE),exist_ok=True)
        data={"theme":current_theme_name}
        if current_theme_name=="Custom" and custom_theme: data["custom_theme"]=custom_theme
        with open(SETTINGS_FILE,"w",encoding="utf-8") as f: json.dump(data,f,indent=2)
    except OSError: pass

def get_theme(): return custom_theme if current_theme_name=="Custom" and custom_theme else THEMES[current_theme_name]

def github_request(url,timeout=10):
    req=Request(url+("&" if "?" in url else "?")+"t="+str(time.time_ns()),headers={"User-Agent":"Villager-Launcher"})
    return urlopen(req,timeout=timeout)

def get_latest_info():
    with github_request(VERSION_URL,5) as r: data=json.loads(r.read().decode("utf-8"))
    if not isinstance(data,dict) or not data.get("version"): raise ValueError("Version information is missing.")
    return data

def download_url(url,filename):
    with github_request(url,15) as r: data=r.read()
    if not data: raise ValueError("Downloaded file is empty.")
    path=os.path.join(tempfile.gettempdir(),filename)
    with open(path,"wb") as f: f.write(data)
    return path

def download_update(): return download_url(LAUNCHER_URL,"villager_launcher_update.py")

def finish_update_from_temp(target):
    source=os.path.abspath(sys.argv[0]); target=os.path.abspath(target); time.sleep(2)
    for _ in range(30):
        try:
            shutil.copy2(source,target)
            subprocess.Popen([sys.executable,target],close_fds=True)
            try: os.remove(source)
            except OSError: pass
            return
        except OSError: time.sleep(1)
    try: messagebox.showerror("Update Error","Windows could not replace the old launcher file.")
    except tk.TclError: pass

def install_update(path):
    current=os.path.abspath(sys.argv[0])
    subprocess.Popen([sys.executable,path,"--install-update",current],creationflags=subprocess.CREATE_NO_WINDOW,close_fds=True)
    root.destroy()

def release_text(info):
    notes=info.get("notes",{})
    if not isinstance(notes,dict): return str(notes)
    parts=[]
    for key in ("Added","Changed","Removed","Fixed"):
        items=notes.get(key,[])
        if isinstance(items,str): items=[items]
        if items: parts.append(key.upper()+"\n"+"\n".join("• "+str(x) for x in items))
    return "\n\n".join(parts) or "No changes listed."

def check_for_updates():
    status.configure(text="Checking for updates..."); update_button.configure(state="disabled"); root.update_idletasks()
    try:
        info=get_latest_info(); latest=info["version"]
        if latest==CURRENT_VERSION:
            status.configure(text="Up to date")
            messagebox.showinfo("Updates",f"Villager Launcher is up to date!\n\nInstalled version: {CURRENT_VERSION}\nServer version: {latest}")
            return
        status.configure(text=f"Update found: {latest}"); root.update_idletasks(); path=download_update()
        if messagebox.askyesno("Update Available",f"Version {latest} is available!\n\nInstalled version: {CURRENT_VERSION}\nServer version: {latest}\n\nWHAT'S NEW\n{release_text(info)}\n\nInstall the update now?"): install_update(path)
        else: status.configure(text="Update canceled")
    except (URLError,TimeoutError) as e:
        status.configure(text="Update failed"); messagebox.showerror("Update Error",f"Could not connect to the update server.\n\n{e}")
    except Exception as e:
        status.configure(text="Update failed"); messagebox.showerror("Update Error",f"Something went wrong.\n\n{e}")
    finally:
        try:
            if root.winfo_exists() and update_button.winfo_exists(): update_button.configure(state="normal")
        except tk.TclError: pass

def repair_and_restart():
    try:
        status.configure(text="Checking launcher updater..."); update_button.configure(state="disabled"); repair_button.configure(state="disabled"); root.update_idletasks()
        latest=get_latest_info()["version"]; path=download_update()
        status.configure(text=f"Updater check passed • restarting with {latest}..."); root.update_idletasks(); time.sleep(1); install_update(path)
    except Exception as e:
        status.configure(text="Repair check failed"); messagebox.showerror("Repair Error",f"Villager Launcher could not repair itself.\n\n{e}")
        try: repair_button.configure(state="normal"); update_button.configure(state="normal")
        except tk.TclError: pass

def show_release_notes():
    try: info=get_latest_info()
    except Exception: info={"version":CURRENT_VERSION,"notes":{}}
    messagebox.showinfo("What's New",f"Villager Launcher {info.get('version',CURRENT_VERSION)}\n\n{release_text(info)}")

def minecraft_directory_exists():
    app=os.environ.get("APPDATA"); return bool(app and os.path.isdir(os.path.join(app,".minecraft")))

def get_minecraft_directory():
    app=os.environ.get("APPDATA")
    return os.path.join(app,".minecraft") if app else None

def open_mods():
    if not minecraft_directory_exists():
        messagebox.showerror("Mods Unavailable","Can't access Minecraft.\n\nVillager Launcher could not find a Minecraft installation. You need an original Minecraft installation before mods can be accessed."); return
    messagebox.showinfo("Mods","Minecraft installation detected.\n\nThe Mods browser is ready for the next module.")

def open_profile(): messagebox.showinfo("Profile","Profile\n\nNo Minecraft account is connected yet.")
def open_launcher_page(): messagebox.showinfo("Launcher",f"Villager Launcher {CURRENT_VERSION}\n\nManual updates are enabled.\nAutomatic updates are disabled.\nRollback support is enabled.")

def open_diagnostics():
    app=os.environ.get("APPDATA","Not found"); mc=os.path.join(app,".minecraft") if app!="Not found" else "Not found"
    messagebox.showinfo("Diagnostics",f"Villager Launcher {CURRENT_VERSION}\n\nMinecraft: {'Detected' if os.path.isdir(mc) else 'Not detected'}\n\nImage system: Removed\nAutomatic updates: Disabled\nManual updates: Enabled\nRollback system: Enabled")

def get_version_history():
    with github_request(COMMITS_URL,10) as r: commits=json.loads(r.read().decode("utf-8"))
    if not isinstance(commits,list): raise ValueError("Invalid GitHub commit history.")
    history=[]; seen=set()
    for commit in commits:
        try:
            sha=commit["sha"]; message=commit["commit"]["message"]
            match=re.search(r"\b(\d+\.\d+\.\d+(?:\.\d+)?)\b",message)
            if match and match.group(1) not in seen:
                version=match.group(1); seen.add(version)
                history.append({"version":version,"sha":sha,"message":message.splitlines()[0]})
        except (KeyError,TypeError): pass
    return history

def download_rollback(version_info):
    version=version_info["version"]; sha=version_info["sha"]
    url=f"https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/{sha}/launcher.py"
    return download_url(url,"villager_launcher_rollback_"+version.replace(".","_")+".py")

def ask_file_choice(version):
    return messagebox.askyesno("Rollback Files",f"Before rolling back to Villager Launcher {version}:\n\nDo you want to KEEP your Minecraft mods and texture/resource packs?\n\nYES = Keep them exactly where they are.\nNO = Move them out of the active folders into a safe Villager Launcher rollback backup.\n\nThe launcher itself never deletes these files.",default="yes")

def move_game_files_to_backup():
    mc=get_minecraft_directory()
    if not mc: return []
    backup=os.path.join(mc,"villager_launcher_rollback_backup")
    moved=[]
    for folder in ("mods","resourcepacks"):
        source=os.path.join(mc,folder)
        if not os.path.isdir(source): continue
        target=os.path.join(backup,folder)
        try:
            os.makedirs(backup,exist_ok=True)
            if os.path.exists(target):
                target=os.path.join(backup,folder+"_"+str(int(time.time())))
            shutil.move(source,target)
            moved.append(folder)
        except OSError:
            pass
    return moved

def rollback_to_version(version_info,window):
    version=version_info["version"]
    if version==CURRENT_VERSION:
        messagebox.showinfo("Rollback","You are already using this version."); return
    if not messagebox.askyesno("Confirm Rollback",f"Roll back Villager Launcher to {version}?\n\nThe current launcher will be replaced and restarted."): return
    try:
        keep_files=ask_file_choice(version)
        moved=[]
        if not keep_files:
            moved=move_game_files_to_backup()
        status.configure(text=f"Downloading version {version}..."); root.update_idletasks()
        path=download_rollback(version)
        if moved:
            status.configure(text="Game files moved to rollback backup..."); root.update_idletasks(); time.sleep(1)
        window.destroy(); install_update(path)
    except Exception as e:
        messagebox.showerror("Rollback Error",f"Could not complete the rollback.\n\n{e}")

def open_version_history():
    window=tk.Toplevel(root); window.title("Villager Launcher Version History"); window.geometry("650x500"); t=get_theme(); window.configure(bg=t["panel"])
    tk.Label(window,text="VERSION HISTORY",font=("Segoe UI",22,"bold"),bg=t["panel"],fg=t["fg"]).pack(pady=(20,5))
    tk.Label(window,text="Choose an older release to roll back to.",font=("Segoe UI",10),bg=t["panel"],fg=t["muted"]).pack(pady=(0,15))
    frame=tk.Frame(window,bg=t["panel"]); frame.pack(fill="both",expand=True,padx=25,pady=10)
    try:
        history=get_version_history()
        if not history:
            tk.Label(frame,text="No version history was found.",font=("Segoe UI",11),bg=t["panel"],fg=t["fg"]).pack(pady=30); return
        for item in history:
            text=f"Version {item['version']}" + ("  • CURRENT" if item["version"]==CURRENT_VERSION else "")
            tk.Button(frame,text=text,font=("Segoe UI",11,"bold"),width=35,relief="flat",bg=t["button"],fg=t["fg"],activebackground=t["accent"],command=lambda x=item: rollback_to_version(x,window)).pack(pady=5)
    except Exception as e:
        tk.Label(frame,text="Could not load version history.\n\n"+str(e),wraplength=550,font=("Segoe UI",10),bg=t["panel"],fg=t["fg"]).pack(pady=30)

def create_custom_theme():
    global custom_theme,current_theme_name
    selected=colorchooser.askcolor(title="Choose custom launcher color",initialcolor=get_theme()["accent"])
    if not selected[1]: return
    custom_theme=dict(get_theme()); custom_theme["accent"]=selected[1]; custom_theme["button"]=selected[1]; custom_theme["icons"]=dict(get_theme()["icons"]); current_theme_name="Custom"; save_settings(); apply_theme()

def open_settings():
    w=tk.Toplevel(root); w.title("Villager Launcher Settings"); w.geometry("440x600"); t=get_theme(); w.configure(bg=t["panel"])
    tk.Label(w,text="⚙️ SETTINGS",font=("Segoe UI",22,"bold"),bg=t["panel"],fg=t["fg"]).pack(pady=20)
    for name in THEMES:
        tk.Button(w,text=name,font=("Segoe UI",11,"bold"),width=25,relief="flat",bg=t["button"],fg=t["fg"],command=lambda n=name: choose_theme(n,w)).pack(pady=4)
    tk.Button(w,text="🎨 Custom Theme",font=("Segoe UI",11,"bold"),width=25,relief="flat",bg=t["button"],fg=t["fg"],command=lambda:(create_custom_theme(),w.destroy())).pack(pady=12)
    tk.Button(w,text="🛠️ Diagnostics",font=("Segoe UI",11,"bold"),width=25,relief="flat",bg=t["button"],fg=t["fg"],command=open_diagnostics).pack(pady=5)
    tk.Button(w,text="⏪ Version History / Rollback",font=("Segoe UI",11,"bold"),width=25,relief="flat",bg=t["accent"],fg=t["fg"],command=open_version_history).pack(pady=15)

def choose_theme(name,w):
    global current_theme_name
    current_theme_name=name; save_settings(); apply_theme(); w.destroy()

def play():
    if not minecraft_directory_exists():
        messagebox.showinfo("Minecraft Required","You need to own Minecraft Java Edition to play using Villager Launcher."); return
    messagebox.showinfo("Minecraft","Minecraft installation detected. Launch integration will be added next.")

def apply_theme():
    t=get_theme(); root.configure(bg=t["bg"]); panel.configure(bg=t["panel"]); topbar.configure(bg=t["panel"]); center.configure(bg=t["panel"])
    for x in (title,subtitle,version,status,minecraft_status): x.configure(bg=t["panel"],fg=t["fg"] if x in (title,subtitle) else t["muted"])
    for b,k in zip((mods_button,profile_button,launcher_button),("mods","profile","launcher")): b.configure(bg=t["button"],fg=t["fg"],activebackground=t["accent"],text=f"{t['icons'][k]}  {k.upper()}")
    for b in (settings_button,update_button,repair_button,diagnostics_button,notes_button): b.configure(bg=t["button"],fg=t["fg"],activebackground=t["accent"])
    play_button.configure(bg=t["accent"],fg=t["fg"],activebackground=t["accent"])

if len(sys.argv)>=3 and sys.argv[1]=="--install-update": finish_update_from_temp(sys.argv[2]); raise SystemExit
load_settings()
root=tk.Tk(); root.title(f"Villager Launcher {CURRENT_VERSION}"); root.geometry("1000x700"); root.resizable(False,False)
panel=tk.Frame(root); panel.pack(fill="both",expand=True,padx=20,pady=20)
topbar=tk.Frame(panel); topbar.pack(fill="x",padx=20,pady=(18,10)); nav_frame=tk.Frame(topbar); nav_frame.pack(side="right")
mods_button=tk.Button(nav_frame,text="🧩  MODS",font=("Segoe UI",10,"bold"),width=12,relief="flat",command=open_mods); mods_button.pack(side="left",padx=4)
profile_button=tk.Button(nav_frame,text="👤  PROFILE",font=("Segoe UI",10,"bold"),width=12,relief="flat",command=open_profile); profile_button.pack(side="left",padx=4)
launcher_button=tk.Button(nav_frame,text="🧑‍🌾  LAUNCHER",font=("Segoe UI",10,"bold"),width=13,relief="flat",command=open_launcher_page); launcher_button.pack(side="left",padx=4)
center=tk.Frame(panel); center.pack(fill="both",expand=True)
title=tk.Label(center,text="VILLAGER LAUNCHER",font=("Segoe UI",36,"bold")); title.pack(pady=(45,3))
subtitle=tk.Label(center,text="Your Minecraft Java launcher",font=("Segoe UI",14)); subtitle.pack()
version=tk.Label(center,text=f"Version {CURRENT_VERSION}",font=("Segoe UI",10)); version.pack(pady=(5,7))
minecraft_status=tk.Label(center,text=("🟢 Minecraft installation detected" if minecraft_directory_exists() else "⚪ Minecraft installation not detected"),font=("Segoe UI",11,"bold")); minecraft_status.pack(pady=(0,20))
play_button=tk.Button(center,text="▶  PLAY",font=("Segoe UI",18,"bold"),width=18,height=2,relief="flat",command=play); play_button.pack(pady=6)
update_button=tk.Button(center,text="🔄  Check for Updates",font=("Segoe UI",11,"bold"),width=24,relief="flat",command=check_for_updates); update_button.pack(pady=2)
repair_button=tk.Button(center,text="🧰  Fix Update & Restart",font=("Segoe UI",11,"bold"),width=24,relief="flat",command=repair_and_restart); repair_button.pack(pady=2)
diagnostics_button=tk.Button(center,text="🛠️  Diagnostics",font=("Segoe UI",10,"bold"),width=24,relief="flat",command=open_diagnostics); diagnostics_button.pack(pady=2)
notes_button=tk.Button(center,text="📝  What's New",font=("Segoe UI",10,"bold"),width=24,relief="flat",command=show_release_notes); notes_button.pack(pady=2)
status=tk.Label(center,text="Ready",font=("Segoe UI",9)); status.pack(pady=8)
settings_button=tk.Button(panel,text="⚙️  SETTINGS",font=("Segoe UI",10,"bold"),width=14,relief="flat",command=open_settings); settings_button.place(relx=.02,rely=.96,anchor="sw")
apply_theme(); root.mainloop()
