import tkinter as tk
from tkinter import messagebox, colorchooser
import json, os, sys, tempfile, subprocess, shutil, time, re
from urllib.request import urlopen, Request
from urllib.error import URLError

CURRENT_VERSION = "1.4.0"
BASE_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main"
VERSION_URL = BASE_URL + "/version.json"
LAUNCHER_URL = BASE_URL + "/launcher.py"
COMMITS_URL = "https://api.github.com/repos/windowswindows822-bot/villager-launcher-updates/commits?path=launcher.py&per_page=30"
APP_DIR = os.path.join(os.environ.get("APPDATA", tempfile.gettempdir()), "VillagerLauncher")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")

THEMES = {
    "Villager Green":{"bg":"#101810","panel":"#182418","fg":"#FFFFFF","muted":"#AFC3AF","accent":"#55AA55","button":"#2D442D","icons":{"mods":"🧩","profile":"👤","launcher":"🧑‍🌾"}},
    "Midnight":{"bg":"#0B1020","panel":"#141B31","fg":"#FFFFFF","muted":"#AAB6D3","accent":"#667EEA","button":"#29365B","icons":{"mods":"🔷","profile":"👤","launcher":"🌙"}},
    "Sky":{"bg":"#DCEFF8","panel":"#F7FCFF","fg":"#173042","muted":"#5C7180","accent":"#3A91C9","button":"#C7E0ED","icons":{"mods":"☁️","profile":"👤","launcher":"☀️"}},
    "Nether":{"bg":"#180C0C","panel":"#2A1212","fg":"#FFFFFF","muted":"#D0A8A8","accent":"#C84B4B","button":"#542626","icons":{"mods":"🔥","profile":"👤","launcher":"💀"}},
    "Ocean":{"bg":"#071820","panel":"#0D2833","fg":"#FFFFFF","muted":"#9FC5D0","accent":"#38A7C7","button":"#1B4655","icons":{"mods":"🌊","profile":"👤","launcher":"🐟"}}
}

DEFAULT_SETTINGS = {
    "theme":"Villager Green",
    "start_page":"Home",
    "show_release_notes":True,
    "confirm_updates":True,
    "check_updates_on_button_only":True,
    "keep_launcher_open":False,
    "remember_window":True,
    "window_width":1100,
    "window_height":700,
    "minecraft_path":"",
    "java_path":"",
    "use_custom_java":False,
    "show_advanced":False,
    "diagnostic_logging":False
}
settings = dict(DEFAULT_SETTINGS)
custom_theme = None
current_theme_name = "Villager Green"

FONT = "Segoe UI Variable"
FALLBACK_FONT = "Segoe UI"

def load_settings():
    global settings, current_theme_name, custom_theme
    try:
        with open(SETTINGS_FILE,"r",encoding="utf-8") as f:
            data=json.load(f)
        if isinstance(data,dict): settings.update({k:v for k,v in data.items() if k in DEFAULT_SETTINGS})
        if data.get("theme") in THEMES: current_theme_name=data["theme"]
        if data.get("theme")=="Custom" and isinstance(data.get("custom_theme"),dict):
            custom_theme=data["custom_theme"]; current_theme_name="Custom"
    except (OSError,json.JSONDecodeError):
        pass

def save_settings():
    try:
        os.makedirs(APP_DIR,exist_ok=True)
        data=dict(settings); data["theme"]=current_theme_name
        if current_theme_name=="Custom" and custom_theme: data["custom_theme"]=custom_theme
        with open(SETTINGS_FILE,"w",encoding="utf-8") as f: json.dump(data,f,indent=2)
    except OSError:
        pass

def get_theme():
    return custom_theme if current_theme_name=="Custom" and custom_theme else THEMES[current_theme_name]

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
        if (not settings.get("confirm_updates")) or messagebox.askyesno("Update Available",f"Version {latest} is available!\n\nInstalled version: {CURRENT_VERSION}\nServer version: {latest}\n\nWHAT'S NEW\n{release_text(info)}\n\nInstall the update now?"):
            install_update(path)
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

def minecraft_directory():
    if settings.get("minecraft_path") and os.path.isdir(settings["minecraft_path"]): return settings["minecraft_path"]
    app=os.environ.get("APPDATA")
    return os.path.join(app,".minecraft") if app else None

def minecraft_directory_exists(): return bool(minecraft_directory() and os.path.isdir(minecraft_directory()))

def open_mods():
    if not minecraft_directory_exists():
        messagebox.showerror("Mods Unavailable","Can't access Minecraft.\n\nVillager Launcher could not find a Minecraft installation. You need an original Minecraft installation before mods can be accessed."); return
    messagebox.showinfo("Mods","Minecraft installation detected.\n\nThe Mods browser is ready for the next module.")

def open_profile(): messagebox.showinfo("Profile","Profile\n\nNo Minecraft account is connected yet.")
def open_launcher_page(): messagebox.showinfo("Launcher",f"Villager Launcher {CURRENT_VERSION}\n\nManual updates are enabled.\nAutomatic updates are disabled.\nRollback support is enabled.")

def open_diagnostics():
    mc=minecraft_directory()
    messagebox.showinfo("Diagnostics",f"Villager Launcher {CURRENT_VERSION}\n\nMinecraft: {'Detected' if mc and os.path.isdir(mc) else 'Not detected'}\n\nMinecraft path: {mc or 'Not found'}\nImage system: Removed\nAutomatic updates: Disabled\nManual updates: Enabled\nRollback system: Enabled\nSettings file: {SETTINGS_FILE}")

def get_version_history():
    with github_request(COMMITS_URL,10) as r: commits=json.loads(r.read().decode("utf-8"))
    if not isinstance(commits,list): raise ValueError("Invalid GitHub commit history.")
    history=[]; seen=set()
    for commit in commits:
        try:
            sha=commit["sha"]; message=commit["commit"]["message"]
            match=re.search(r"\b(\d+\.\d+\.\d+(?:\.\d+)?)\b",message)
            if match and match.group(1) not in seen:
                version=match.group(1); seen.add(version); history.append({"version":version,"sha":sha,"message":message.splitlines()[0]})
        except (KeyError,TypeError): pass
    return history

def download_rollback(version_info):
    version=version_info["version"]; sha=version_info["sha"]
    url=f"https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/{sha}/launcher.py"
    return download_url(url,"villager_launcher_rollback_"+version.replace(".","_")+".py")

def ask_file_choice(version):
    return messagebox.askyesno("Rollback Files",f"Before rolling back to Villager Launcher {version}:\n\nDo you want to KEEP your Minecraft mods and texture/resource packs?\n\nYES = Keep them exactly where they are.\nNO = Move them out of the active folders into a safe Villager Launcher rollback backup.\n\nThe launcher itself never deletes these files.",default="yes")

def move_game_files_to_backup():
    mc=minecraft_directory()
    if not mc: return []
    backup=os.path.join(mc,"villager_launcher_rollback_backup"); moved=[]
    for folder in ("mods","resourcepacks"):
        source=os.path.join(mc,folder)
        if not os.path.isdir(source): continue
        target=os.path.join(backup,folder)
        try:
            os.makedirs(backup,exist_ok=True)
            if os.path.exists(target): target=os.path.join(backup,folder+"_"+str(int(time.time())))
            shutil.move(source,target); moved.append(folder)
        except OSError: pass
    return moved

def rollback_to_version(version_info,window):
    version=version_info["version"]
    if version==CURRENT_VERSION: messagebox.showinfo("Rollback","You are already using this version."); return
    if not messagebox.askyesno("Confirm Rollback",f"Roll back Villager Launcher to {version}?\n\nThe current launcher will be replaced and restarted."): return
    try:
        keep_files=ask_file_choice(version); moved=[]
        if not keep_files: moved=move_game_files_to_backup()
        status.configure(text=f"Downloading version {version}..."); root.update_idletasks(); path=download_rollback(version)
        if moved: status.configure(text="Game files moved to rollback backup..."); root.update_idletasks(); time.sleep(1)
        window.destroy(); install_update(path)
    except Exception as e: messagebox.showerror("Rollback Error",f"Could not complete the rollback.\n\n{e}")

def open_version_history():
    window=tk.Toplevel(root); window.title("Villager Launcher Version History"); window.geometry("650x500"); t=get_theme(); window.configure(bg=t["panel"])
    tk.Label(window,text="VERSION HISTORY",font=(FONT,22,"bold"),bg=t["panel"],fg=t["fg"]).pack(pady=(20,5))
    tk.Label(window,text="Choose an older release to roll back to.",font=(FONT,10),bg=t["panel"],fg=t["muted"]).pack(pady=(0,15))
    frame=tk.Frame(window,bg=t["panel"]); frame.pack(fill="both",expand=True,padx=25,pady=10)
    try:
        history=get_version_history()
        if not history: tk.Label(frame,text="No version history was found.",font=(FONT,11),bg=t["panel"],fg=t["fg"]).pack(pady=30); return
        for item in history:
            text=f"Version {item['version']}"+("  • CURRENT" if item["version"]==CURRENT_VERSION else "")
            tk.Button(frame,text=text,font=(FONT,11,"bold"),width=35,relief="flat",bg=t["button"],fg=t["fg"],activebackground=t["accent"],command=lambda x=item: rollback_to_version(x,window)).pack(pady=5)
    except Exception as e: tk.Label(frame,text="Could not load version history.\n\n"+str(e),wraplength=550,font=(FONT,10),bg=t["panel"],fg=t["fg"]).pack(pady=30)

def create_custom_theme():
    global custom_theme,current_theme_name
    selected=colorchooser.askcolor(title="Choose custom launcher color",initialcolor=get_theme()["accent"])
    if not selected[1]: return
    custom_theme=dict(get_theme()); custom_theme["accent"]=selected[1]; custom_theme["button"]=selected[1]; custom_theme["icons"]=dict(get_theme()["icons"]); current_theme_name="Custom"; save_settings(); apply_theme(); refresh_ui()

def choose_theme(name):
    global current_theme_name
    current_theme_name=name; save_settings(); apply_theme(); refresh_ui()

# ---------- 1.4.0 redesigned settings ----------
def setting_bool(parent,label,key,description=""):
    var=tk.BooleanVar(value=bool(settings.get(key,False)))
    row=tk.Frame(parent,bg=get_theme()["panel"]); row.pack(fill="x",pady=8)
    tk.Checkbutton(row,text=label,variable=var,font=(FONT,11,"bold"),bg=get_theme()["panel"],fg=get_theme()["fg"],selectcolor=get_theme()["button"],activebackground=get_theme()["panel"],activeforeground=get_theme()["fg"],command=lambda: (settings.__setitem__(key,var.get()),save_settings())).pack(anchor="w")
    if description: tk.Label(row,text=description,font=(FONT,9),bg=get_theme()["panel"],fg=get_theme()["muted"],wraplength=620,justify="left").pack(anchor="w",padx=26,pady=(2,0))

def settings_header(parent,title,subtitle):
    t=get_theme(); tk.Label(parent,text=title,font=(FONT,20,"bold"),bg=t["panel"],fg=t["fg"]).pack(anchor="w",pady=(0,3)); tk.Label(parent,text=subtitle,font=(FONT,10),bg=t["panel"],fg=t["muted"]).pack(anchor="w",pady=(0,18))

def settings_page(container,name):
    for child in container.winfo_children(): child.destroy()
    t=get_theme()
    if name=="Appearance":
        settings_header(container,"Appearance","Change launcher colors and interface preferences. Theme controls stay here — separate from general settings.")
        tk.Label(container,text="Launcher theme",font=(FONT,11,"bold"),bg=t["panel"],fg=t["fg"]).pack(anchor="w")
        for theme in THEMES:
            tk.Button(container,text=("✓ " if current_theme_name==theme else "")+theme,font=(FONT,10,"bold"),relief="flat",bg=t["button"],fg=t["fg"],activebackground=t["accent"],command=lambda n=theme: choose_theme(n)).pack(fill="x",pady=3)
        tk.Button(container,text="🎨 Custom Theme",font=(FONT,10,"bold"),relief="flat",bg=t["accent"],fg=t["fg"],command=create_custom_theme).pack(fill="x",pady=(8,3))
    elif name=="General":
        settings_header(container,"General","Control startup behavior, confirmations, and how the launcher remembers your choices.")
        setting_bool(container,"Remember window size","remember_window","Keeps the launcher window dimensions between sessions.")
        setting_bool(container,"Show release notes for updates","show_release_notes","Shows the release notes when a new launcher version is offered.")
        setting_bool(container,"Confirm before installing updates","confirm_updates","Manual update checking never installs an update silently when this is enabled.")
        setting_bool(container,"Keep launcher open after game launch","keep_launcher_open","Reserved for the future Minecraft launch integration.")
    elif name=="Minecraft":
        settings_header(container,"Minecraft","Choose where Villager Launcher should look for your Minecraft files.")
        tk.Label(container,text="Custom Minecraft directory",font=(FONT,11,"bold"),bg=t["panel"],fg=t["fg"]).pack(anchor="w")
        entry=tk.Entry(container,font=(FONT,10),bg=t["bg"],fg=t["fg"],insertbackground=t["fg"],relief="flat")
        entry.insert(0,settings.get("minecraft_path", "")); entry.pack(fill="x",pady=6)
        tk.Button(container,text="Save Minecraft Path",font=(FONT,10,"bold"),relief="flat",bg=t["accent"],fg=t["fg"],command=lambda:(settings.__setitem__("minecraft_path",entry.get().strip()),save_settings(),messagebox.showinfo("Saved","Minecraft path saved."))).pack(anchor="w",pady=4)
        setting_bool(container,"Use custom Java executable","use_custom_java","Stores a Java path for future Minecraft launch integration without changing your system Java installation.")
        java=tk.Entry(container,font=(FONT,10),bg=t["bg"],fg=t["fg"],insertbackground=t["fg"],relief="flat")
        java.insert(0,settings.get("java_path", "")); java.pack(fill="x",pady=6)
        tk.Button(container,text="Save Java Path",font=(FONT,10,"bold"),relief="flat",bg=t["button"],fg=t["fg"],command=lambda:(settings.__setitem__("java_path",java.get().strip()),save_settings())).pack(anchor="w",pady=4)
    elif name=="Updates":
        settings_header(container,"Updates","Villager Launcher uses manual update checks. Automatic updates remain disabled.")
        tk.Label(container,text="Update policy",font=(FONT,12,"bold"),bg=t["panel"],fg=t["fg"]).pack(anchor="w")
        tk.Label(container,text="CHECK FOR UPDATE → SHOW WHAT'S NEW → ASK → INSTALL → RESTART",font=(FONT,10,"bold"),bg=t["panel"],fg=t["accent"]).pack(anchor="w",pady=8)
        setting_bool(container,"Check only when I press Check for Updates","check_updates_on_button_only","No background or automatic update process is enabled.")
        tk.Button(container,text="Check for Updates Now",font=(FONT,10,"bold"),relief="flat",bg=t["accent"],fg=t["fg"],command=check_for_updates).pack(fill="x",pady=8)
        tk.Button(container,text="What's New",font=(FONT,10,"bold"),relief="flat",bg=t["button"],fg=t["fg"],command=show_release_notes).pack(fill="x",pady=3)
        tk.Button(container,text="Version History / Rollback",font=(FONT,10,"bold"),relief="flat",bg=t["button"],fg=t["fg"],command=open_version_history).pack(fill="x",pady=3)
    elif name=="Privacy":
        settings_header(container,"Privacy","Simple controls for launcher diagnostics and local data.")
        setting_bool(container,"Diagnostic logging","diagnostic_logging","When enabled, future diagnostic modules may record launcher troubleshooting information locally.")
        tk.Label(container,text="The launcher does not need your Minecraft password or a GitHub token to perform its public update check.",font=(FONT,10),bg=t["panel"],fg=t["muted"],wraplength=650,justify="left").pack(anchor="w",pady=15)
    elif name=="Advanced":
        settings_header(container,"Advanced","Developer-oriented launcher controls. These options do not modify Minecraft files automatically.")
        setting_bool(container,"Show advanced diagnostics","show_advanced","Enables additional diagnostic information in future launcher modules.")
        tk.Button(container,text="Open Diagnostics",font=(FONT,10,"bold"),relief="flat",bg=t["button"],fg=t["fg"],command=open_diagnostics).pack(fill="x",pady=4)
        tk.Button(container,text="Repair / Restart Launcher",font=(FONT,10,"bold"),relief="flat",bg=t["accent"],fg=t["fg"],command=repair_and_restart).pack(fill="x",pady=4)
        tk.Button(container,text="Reset All Settings",font=(FONT,10,"bold"),relief="flat",bg=t["button"],fg=t["fg"],command=reset_settings).pack(fill="x",pady=4)

def reset_settings():
    global settings,current_theme_name,custom_theme
    if not messagebox.askyesno("Reset Settings","Reset all Villager Launcher settings to their defaults?"): return
    settings=dict(DEFAULT_SETTINGS); current_theme_name="Villager Green"; custom_theme=None; save_settings(); refresh_ui()

def open_settings():
    w=tk.Toplevel(root); w.title("Villager Launcher Settings"); w.geometry("900x650"); t=get_theme(); w.configure(bg=t["bg"])
    sidebar=tk.Frame(w,bg=t["bg"],width=210); sidebar.pack(side="left",fill="y"); sidebar.pack_propagate(False)
    content=tk.Frame(w,bg=t["panel"]); content.pack(side="right",fill="both",expand=True,padx=10,pady=10)
    tk.Label(sidebar,text="SETTINGS",font=(FONT,20,"bold"),bg=t["bg"],fg=t["fg"]).pack(anchor="w",padx=22,pady=(25,5))
    tk.Label(sidebar,text="Villager Launcher 1.4.0",font=(FONT,9),bg=t["bg"],fg=t["muted"]).pack(anchor="w",padx=22,pady=(0,20))
    for name in ("General","Appearance","Minecraft","Updates","Privacy","Advanced"):
        tk.Button(sidebar,text=name,font=(FONT,10,"bold"),relief="flat",bg=t["button"],fg=t["fg"],activebackground=t["accent"],command=lambda n=name: settings_page(content,n)).pack(fill="x",padx=15,pady=3)
    settings_page(content,"General")

def play():
    if not minecraft_directory_exists():
        messagebox.showinfo("Minecraft Required","You need to own Minecraft Java Edition to play using Villager Launcher."); return
    messagebox.showinfo("Minecraft","Minecraft installation detected. Launch integration will be added next.")

def make_button(parent,text,command,accent=False):
    t=get_theme(); return tk.Button(parent,text=text,font=(FONT,11,"bold"),relief="flat",bd=0,bg=t["accent"] if accent else t["button"],fg=t["fg"],activebackground=t["accent"],activeforeground=t["fg"],cursor="hand2",padx=18,pady=11,command=command)

def refresh_ui():
    t=get_theme()
    for child in root.winfo_children(): child.destroy()
    build_ui()

def build_ui():
    global status,update_button,repair_button
    t=get_theme(); root.configure(bg=t["bg"])
    header=tk.Frame(root,bg=t["panel"],height=74); header.pack(fill="x"); header.pack_propagate(False)
    tk.Label(header,text="VILLAGER LAUNCHER",font=(FONT,20,"bold"),bg=t["panel"],fg=t["fg"]).pack(side="left",padx=25)
    tk.Label(header,text=f"v{CURRENT_VERSION}",font=(FONT,10,"bold"),bg=t["panel"],fg=t["accent"]).pack(side="left",padx=4)
    make_button(header,"⚙ Settings",open_settings).pack(side="right",padx=20,pady=14)
    body=tk.Frame(root,bg=t["bg"]); body.pack(fill="both",expand=True)
    nav=tk.Frame(body,bg=t["panel"],width=190); nav.pack(side="left",fill="y"); nav.pack_propagate(False)
    tk.Label(nav,text="MAIN",font=(FONT,9,"bold"),bg=t["panel"],fg=t["muted"]).pack(anchor="w",padx=20,pady=(24,8))
    for text,cmd in (("⌂  Home",lambda:None),("🧩  Mods",open_mods),("👤  Profile",open_profile),("🧑‍🌾  Launcher",open_launcher_page)):
        tk.Button(nav,text=text,font=(FONT,10,"bold"),anchor="w",relief="flat",bg=t["button"],fg=t["fg"],activebackground=t["accent"],command=cmd).pack(fill="x",padx=12,pady=4)
    tk.Label(nav,text="TOOLS",font=(FONT,9,"bold"),bg=t["panel"],fg=t["muted"]).pack(anchor="w",padx=20,pady=(25,8))
    tk.Button(nav,text="🛠  Diagnostics",font=(FONT,10,"bold"),anchor="w",relief="flat",bg=t["button"],fg=t["fg"],activebackground=t["accent"],command=open_diagnostics).pack(fill="x",padx=12,pady=4)
    main=tk.Frame(body,bg=t["bg"]); main.pack(side="left",fill="both",expand=True,padx=28,pady=26)
    tk.Label(main,text="Welcome back, Villager Commander.",font=(FONT,25,"bold"),bg=t["bg"],fg=t["fg"]).pack(anchor="w")
    tk.Label(main,text="A cleaner launcher, rebuilt settings, and a much sharper interface.",font=(FONT,11),bg=t["bg"],fg=t["muted"]).pack(anchor="w",pady=(4,22))
    card=tk.Frame(main,bg=t["panel"]); card.pack(fill="x",pady=8)
    tk.Label(card,text="MINECRAFT",font=(FONT,10,"bold"),bg=t["panel"],fg=t["muted"]).pack(anchor="w",padx=24,pady=(20,3))
    tk.Label(card,text="Ready when you are.",font=(FONT,18,"bold"),bg=t["panel"],fg=t["fg"]).pack(anchor="w",padx=24)
    tk.Label(card,text="Villager Launcher only launches an original Minecraft installation.",font=(FONT,10),bg=t["panel"],fg=t["muted"]).pack(anchor="w",padx=24,pady=(3,16))
    make_button(card,"▶  PLAY",play,True).pack(anchor="w",padx=24,pady=(0,20))
    row=tk.Frame(main,bg=t["bg"]); row.pack(fill="x",pady=10)
    update_button=make_button(row,"Check for Updates",check_for_updates); update_button.pack(side="left",padx=(0,8))
    repair_button=make_button(row,"Repair / Restart",repair_and_restart); repair_button.pack(side="left",padx=8)
    make_button(row,"What's New",show_release_notes).pack(side="left",padx=8)
    status=tk.Label(main,text="Manual updates • Automatic updates disabled • Rollback enabled",font=(FONT,9),bg=t["bg"],fg=t["muted"]); status.pack(anchor="w",pady=14)

load_settings()
if len(sys.argv)>=3 and sys.argv[1]=="--install-update":
    finish_update_from_temp(sys.argv[2]); raise SystemExit

root=tk.Tk(); root.title("Villager Launcher"); root.minsize(900,600)
if settings.get("remember_window"):
    root.geometry(f"{int(settings.get('window_width',1100))}x{int(settings.get('window_height',700))}")
else: root.geometry("1100x700")
root.option_add("*Font",(FONT,10))
build_ui()
root.protocol("WM_DELETE_WINDOW",lambda:(settings.update({"window_width":root.winfo_width(),"window_height":root.winfo_height()}) if settings.get("remember_window") else None,save_settings(),root.destroy()))
root.mainloop()
