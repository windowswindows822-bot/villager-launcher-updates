import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import json, os, sys, tempfile, subprocess, shutil, time, zipfile
from urllib.request import urlopen, Request

CURRENT_VERSION = "1.6.1"
BASE_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main"
VERSION_URL = BASE_URL + "/version.json"
LAUNCHER_URL = BASE_URL + "/launcher.py"
APP_DIR = os.path.join(os.environ.get("APPDATA", tempfile.gettempdir()), "VillagerLauncher")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
PROFILES_FILE = os.path.join(APP_DIR, "profiles.json")
FONT = "Segoe UI Variable"

THEMES = {
    "Villager Green": {"bg":"#101810","panel":"#182418","card":"#203020","fg":"#FFFFFF","muted":"#AFC3AF","accent":"#62C462","button":"#2D442D","danger":"#B94A48"},
    "Midnight": {"bg":"#0A0E18","panel":"#121827","card":"#1A2338","fg":"#FFFFFF","muted":"#AAB6D3","accent":"#7188FF","button":"#29365B","danger":"#D05B5B"},
    "Sky": {"bg":"#DCEFF8","panel":"#F7FCFF","card":"#EAF5FA","fg":"#173042","muted":"#5C7180","accent":"#3A91C9","button":"#C7E0ED","danger":"#B64E4E"},
    "Nether": {"bg":"#180C0C","panel":"#2A1212","card":"#391919","fg":"#FFFFFF","muted":"#D0A8A8","accent":"#E05A5A","button":"#542626","danger":"#FF8A70"},
    "Ocean": {"bg":"#071820","panel":"#0D2833","card":"#123743","fg":"#FFFFFF","muted":"#9FC5D0","accent":"#38A7C7","button":"#1B4655","danger":"#D45D67"}
}
DEFAULT_SETTINGS = {"theme":"Villager Green","remember_window":True,"window_width":1120,"window_height":720,"minecraft_path":"","java_path":"","confirm_updates":True,"start_page":"Home"}
settings = dict(DEFAULT_SETTINGS)
profiles = []
selected_profile = 0
current_theme = "Villager Green"
custom_theme = None
root = None
content = None
status = None
sidebar = None


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except (OSError, json.JSONDecodeError): return default


def save_settings():
    try:
        os.makedirs(APP_DIR, exist_ok=True)
        data = dict(settings); data["theme"] = current_theme
        if current_theme == "Custom" and custom_theme: data["custom_theme"] = custom_theme
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
    except OSError: pass


def load_settings():
    global settings, current_theme, custom_theme
    data = load_json(SETTINGS_FILE, {})
    if isinstance(data, dict):
        for k in DEFAULT_SETTINGS:
            if k in data: settings[k] = data[k]
        if data.get("theme") in THEMES: current_theme = data["theme"]
        elif data.get("theme") == "Custom" and isinstance(data.get("custom_theme"), dict): custom_theme = data["custom_theme"]; current_theme = "Custom"


def save_profiles():
    try:
        os.makedirs(APP_DIR, exist_ok=True)
        with open(PROFILES_FILE, "w", encoding="utf-8") as f: json.dump(profiles, f, indent=2)
    except OSError: pass


def load_profiles():
    global profiles
    data = load_json(PROFILES_FILE, [])
    profiles = data if isinstance(data, list) else []
    if not profiles:
        profiles = [{"name":"Default","version":"","loader":"Vanilla","description":"Your first Villager Launcher profile.","pfile":""}]
        save_profiles()


def theme(): return custom_theme if current_theme == "Custom" and custom_theme else THEMES.get(current_theme, THEMES["Villager Green"])


def github_request(url, timeout=10):
    return urlopen(Request(url + ("&" if "?" in url else "?") + "t=" + str(time.time_ns()), headers={"User-Agent":"Villager-Launcher"}), timeout=timeout)


def latest_info():
    with github_request(VERSION_URL, 5) as r: data = json.loads(r.read().decode("utf-8"))
    if not isinstance(data, dict) or not data.get("version"): raise ValueError("Version information is missing.")
    return data


def download_update():
    with github_request(LAUNCHER_URL, 15) as r: data = r.read()
    if not data: raise ValueError("Downloaded launcher is empty.")
    path = os.path.join(tempfile.gettempdir(), "villager_launcher_update.py")
    with open(path, "wb") as f: f.write(data)
    return path


def finish_update(target):
    source = os.path.abspath(sys.argv[0]); target = os.path.abspath(target); time.sleep(2)
    for _ in range(30):
        try:
            shutil.copy2(source, target); subprocess.Popen([sys.executable, target], close_fds=True)
            try: os.remove(source)
            except OSError: pass
            return
        except OSError: time.sleep(1)
    try: messagebox.showerror("Update Error", "Windows could not replace the launcher file.")
    except tk.TclError: pass


def install_update(path):
    subprocess.Popen([sys.executable, path, "--install-update", os.path.abspath(sys.argv[0])], creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0), close_fds=True); root.destroy()


def release_text(info):
    notes = info.get("notes", {})
    if not isinstance(notes, dict): return str(notes)
    parts=[]
    for k in ("Added","Changed","Removed","Fixed"):
        items=notes.get(k,[])
        if isinstance(items,str): items=[items]
        if items: parts.append(k.upper()+"\n"+"\n".join("• "+str(x) for x in items))
    return "\n\n".join(parts) or "No changes listed."


def check_updates():
    try:
        status.config(text="Checking for updates..."); info=latest_info(); newest=str(info["version"])
        if newest == CURRENT_VERSION:
            status.config(text="Up to date"); messagebox.showinfo("Updates",f"Villager Launcher is up to date!\n\nInstalled: {CURRENT_VERSION}\nServer: {newest}"); return
        notes=release_text(info)
        if settings.get("confirm_updates",True) and not messagebox.askyesno("Update Available",f"Version {newest} is available.\n\nWHAT'S NEW\n{notes}\n\nInstall now?"): return
        install_update(download_update())
    except Exception as e:
        status.config(text="Update failed"); messagebox.showerror("Update Error",str(e))


def mc_dir():
    p=settings.get("minecraft_path","")
    if p and os.path.isdir(p): return p
    app=os.environ.get("APPDATA"); return os.path.join(app,".minecraft") if app else None


def ownership_verified():
    mc=mc_dir()
    if not mc or not os.path.isdir(mc): return False
    return os.path.isfile(os.path.join(mc,"launcher_accounts.json")) or os.path.isfile(os.path.join(mc,"launcher_profiles.json"))


def require_minecraft(feature):
    if ownership_verified(): return True
    messagebox.showwarning("Minecraft Required",f"{feature} is locked until an original Minecraft installation is detected.\n\nSign in through the official Minecraft launcher and select its Minecraft data folder in Villager Launcher Settings.")
    return False


def installed_versions():
    d=mc_dir(); folder=os.path.join(d,"versions") if d else ""
    if not os.path.isdir(folder): return []
    try: return sorted([x for x in os.listdir(folder) if os.path.isdir(os.path.join(folder,x))], reverse=True)
    except OSError: return []


def mod_files():
    d=mc_dir(); folder=os.path.join(d,"mods") if d else ""
    if not os.path.isdir(folder): return []
    try: return [x for x in os.listdir(folder) if x.lower().endswith(".jar")]
    except OSError: return []


def load_pfp(profile,size):
    path=profile.get("pfile","")
    if not path or not os.path.isfile(path): return None
    try:
        im=tk.PhotoImage(file=path); factor=max(1,int(max(im.width(),im.height())/size)); return im.subsample(factor,factor) if factor>1 else im
    except tk.TclError: return None


def pick_pfp(index):
    if not require_minecraft("Profile pictures"): return
    path=filedialog.askopenfilename(title="Choose profile picture",filetypes=[("PNG images","*.png"),("GIF images","*.gif"),("BMP images","*.bmp")])
    if path: profiles[index]["pfile"]=path; save_profiles(); render_profiles()


def create_profile():
    if not require_minecraft("Profiles"): return
    win=tk.Toplevel(root); win.title("New Profile"); win.geometry("430x180"); win.configure(bg=theme()["panel"]); win.grab_set()
    tk.Label(win,text="Profile name",font=(FONT,11,"bold"),bg=theme()["panel"],fg=theme()["fg"]).pack(anchor="w",padx=25,pady=(25,8))
    e=tk.Entry(win,font=(FONT,11)); e.pack(fill="x",padx=25); e.focus_set()
    def done():
        n=e.get().strip()
        if n: profiles.append({"name":n,"version":"","loader":"Vanilla","description":"","pfile":""}); save_profiles(); win.destroy(); render_profiles()
    btn(win,"CREATE",done,True).pack(anchor="e",padx=25,pady=18)


def choose_mc():
    p=filedialog.askdirectory(title="Choose Minecraft folder")
    if p: settings["minecraft_path"]=p; save_settings(); render_settings()


def choose_java():
    p=filedialog.askopenfilename(title="Choose Java executable",filetypes=[("Java executable","java.exe"),("All files","*.*")])
    if p: settings["java_path"]=p; save_settings(); render_settings()


def set_theme(name):
    global current_theme
    if name in THEMES: current_theme=name
    elif name=="Custom" and custom_theme: current_theme="Custom"
    save_settings(); rebuild_ui()


def custom_theme_editor():
    global custom_theme,current_theme
    chosen=colorchooser.askcolor(title="Choose theme accent",initialcolor=theme()["accent"])[1]
    if chosen:
        custom_theme=dict(theme()); custom_theme["accent"]=chosen; custom_theme["button"]=chosen; current_theme="Custom"; save_settings(); rebuild_ui()


def reset_settings():
    global settings,current_theme,custom_theme
    if not messagebox.askyesno("Reset Settings","Reset Villager Launcher settings? Your Minecraft files and profiles will not be deleted."): return
    settings=dict(DEFAULT_SETTINGS); current_theme="Villager Green"; custom_theme=None; save_settings(); rebuild_ui()


def play_selected():
    if not require_minecraft("Minecraft launching"): return
    messagebox.showinfo("Minecraft","Original Minecraft installation detected.\n\nLaunch integration will be enabled in a future release.")


def import_mod():
    if not require_minecraft("Mods"): return
    folder=os.path.join(mc_dir(),"mods"); files=filedialog.askopenfilenames(title="Import Minecraft mods",filetypes=[("Minecraft mods","*.jar")]); os.makedirs(folder,exist_ok=True)
    for f in files:
        try: shutil.copy2(f,os.path.join(folder,os.path.basename(f)))
        except OSError: pass
    render_mods()


def disable_mod(name):
    if not require_minecraft("Mods"): return
    try:
        os.makedirs(os.path.join(mc_dir(),"mods_disabled"),exist_ok=True); shutil.move(os.path.join(mc_dir(),"mods",name),os.path.join(mc_dir(),"mods_disabled",name)); render_mods()
    except OSError as e: messagebox.showerror("Mod Error",str(e))


def create_backup():
    if not require_minecraft("Backups"): return
    mc=mc_dir(); folder=os.path.join(mc,"villager_launcher_backups"); os.makedirs(folder,exist_ok=True); target=os.path.join(folder,time.strftime("backup_%Y%m%d_%H%M%S.zip"))
    try:
        with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED) as z:
            for part in ("saves","mods","resourcepacks","config"):
                src=os.path.join(mc,part)
                if os.path.isdir(src):
                    for base,_,files in os.walk(src):
                        for f in files:
                            path=os.path.join(base,f); z.write(path,os.path.relpath(path,mc))
        messagebox.showinfo("Backup Created","Minecraft backup created safely.\n\n"+target); render_backups()
    except OSError as e: messagebox.showerror("Backup Error",str(e))


def clear_content():
    for w in content.winfo_children(): w.destroy()


def label(parent,text,size=10,bold=False,fg=None,bg=None):
    t=theme(); return tk.Label(parent,text=text,font=(FONT,size,"bold" if bold else "normal"),bg=bg or t["panel"],fg=fg or t["fg"])


def btn(parent,text,command,accent=False):
    t=theme(); return tk.Button(parent,text=text,command=command,font=(FONT,10,"bold"),relief="flat",bd=0,bg=t["accent"] if accent else t["button"],fg="white" if accent else t["fg"],activebackground=t["accent"],activeforeground="white",padx=16,pady=9,cursor="hand2")


def card(parent): return tk.Frame(parent,bg=theme()["card"],bd=0,highlightthickness=0)


def render_home():
    clear_content(); t=theme(); p=profiles[selected_profile] if profiles else {"name":"Profile","version":"","loader":"Vanilla","pfile":""}
    label(content,"Ready to meet your wishes?",28,True).pack(anchor="w",pady=(0,4))
    label(content,"Your Minecraft, Your Way.",13,False,t["muted"]).pack(anchor="w",pady=(0,22))
    c=card(content); c.pack(fill="x",pady=5)
    inner=tk.Frame(c,bg=t["card"]); inner.pack(fill="x",padx=24,pady=22)
    info=tk.Frame(inner,bg=t["card"]); info.pack(side="left",fill="x",expand=True)
    tk.Label(info,text=p.get("name","Profile"),font=(FONT,18,"bold"),bg=t["card"],fg=t["fg"]).pack(anchor="w")
    tk.Label(info,text=(p.get("version") or "No version selected")+"  •  "+p.get("loader","Vanilla"),font=(FONT,10),bg=t["card"],fg=t["muted"]).pack(anchor="w",pady=4)
    if ownership_verified(): btn(inner,"PLAY",play_selected,True).pack(side="right")
    else: btn(inner,"🔒 PLAY — OWN MINECRAFT",lambda:require_minecraft("Minecraft features")).pack(side="right")
    stats=tk.Frame(content,bg=t["panel"]); stats.pack(fill="x",pady=18)
    values=(("Profiles",str(len(profiles)) if ownership_verified() else "Locked"),("Versions",str(len(installed_versions())) if ownership_verified() else "Locked"),("Mods",str(len(mod_files())) if ownership_verified() else "Locked"))
    for title,value in values:
        c=card(stats); c.pack(side="left",fill="both",expand=True,padx=5)
        tk.Label(c,text=value,font=(FONT,22,"bold"),bg=t["card"],fg=t["accent"] if ownership_verified() else t["danger"]).pack(pady=(14,0))
        tk.Label(c,text=title,font=(FONT,9),bg=t["card"],fg=t["muted"]).pack(pady=(0,14))


def render_profiles():
    clear_content(); t=theme(); label(content,"PROFILES",24,True).pack(anchor="w"); label(content,"Separate Minecraft setups with their own identity and settings.",10,False,t["muted"]).pack(anchor="w",pady=(3,18))
    if not ownership_verified(): btn(content,"🔒 PROFILES LOCKED",lambda:require_minecraft("Profiles"),True).pack(anchor="w",pady=12); return
    btn(content,"+ NEW PROFILE",create_profile,True).pack(anchor="w",pady=(0,12))
    for i,p in enumerate(profiles):
        c=card(content); c.pack(fill="x",pady=5); inner=tk.Frame(c,bg=t["card"]); inner.pack(fill="x",padx=18,pady=14)
        pic=load_pfp(p,55)
        if pic: x=tk.Label(inner,image=pic,bg=t["card"]); x.image=pic; x.pack(side="left",padx=(0,14))
        else: tk.Label(inner,text="PFP",font=(FONT,10,"bold"),bg=t["card"],fg=t["muted"],width=6,height=2).pack(side="left",padx=(0,14))
        text=tk.Frame(inner,bg=t["card"]); text.pack(side="left",fill="x",expand=True); tk.Label(text,text=p.get("name","Profile"),font=(FONT,14,"bold"),bg=t["card"],fg=t["fg"]).pack(anchor="w"); tk.Label(text,text=(p.get("version") or "No version")+" • "+p.get("loader","Vanilla"),font=(FONT,9),bg=t["card"],fg=t["muted"]).pack(anchor="w")
        btn(inner,"CHOOSE PFP",lambda n=i:pick_pfp(n)).pack(side="right",padx=5); btn(inner,"SELECT",lambda n=i:select_profile(n),True).pack(side="right",padx=5)


def select_profile(i):
    global selected_profile
    if not require_minecraft("Profiles"): return
    selected_profile=i; settings["start_page"]="Home"; save_settings(); render_home()


def render_mods():
    clear_content(); t=theme(); label(content,"MOD MANAGER",24,True).pack(anchor="w"); label(content,"Enable, disable and import mods without permanently deleting them.",10,False,t["muted"]).pack(anchor="w",pady=(3,18))
    if not ownership_verified(): btn(content,"🔒 MODS LOCKED",lambda:require_minecraft("Mods"),True).pack(anchor="w",pady=12); return
    btn(content,"IMPORT .JAR",import_mod,True).pack(anchor="w",pady=(0,15))
    for name in mod_files():
        c=card(content); c.pack(fill="x",pady=3); tk.Label(c,text=name,font=(FONT,10),bg=t["card"],fg=t["fg"]).pack(side="left",padx=15,pady=10); btn(c,"DISABLE",lambda n=name:disable_mod(n)).pack(side="right",padx=10,pady=5)


def render_versions():
    clear_content(); t=theme(); label(content,"MINECRAFT VERSIONS",24,True).pack(anchor="w"); label(content,"Versions already installed in your Minecraft folder.",10,False,t["muted"]).pack(anchor="w",pady=(3,18))
    if not ownership_verified(): btn(content,"🔒 VERSIONS LOCKED",lambda:require_minecraft("Minecraft versions"),True).pack(anchor="w",pady=12); return
    for v in installed_versions():
        c=card(content); c.pack(fill="x",pady=3); tk.Label(c,text=v,font=(FONT,11,"bold"),bg=t["card"],fg=t["fg"]).pack(side="left",padx=18,pady=12); tk.Label(c,text="Installed",font=(FONT,9),bg=t["card"],fg=t["muted"]).pack(side="right",padx=18)


def render_backups():
    clear_content(); label(content,"BACKUP CENTER",24,True).pack(anchor="w"); label(content,"Protect important Minecraft data before making changes.",10,False,theme()["muted"]).pack(anchor="w",pady=(3,18)); btn(content,"CREATE BACKUP",create_backup,True).pack(anchor="w")


def render_repair():
    clear_content(); t=theme(); label(content,"REPAIR CENTER",24,True).pack(anchor="w"); label(content,"Diagnostics that explain what Villager Launcher can see.",10,False,t["muted"]).pack(anchor="w",pady=(3,18)); mc=mc_dir()
    checks=[("Minecraft folder",bool(mc and os.path.isdir(mc))),("Official launcher evidence",ownership_verified()),("Versions folder",bool(mc and os.path.isdir(os.path.join(mc,"versions")))), ("Mods folder",bool(mc and os.path.isdir(os.path.join(mc,"mods")))), ("Launcher settings",os.path.isfile(SETTINGS_FILE))]
    for name,ok in checks:
        c=card(content); c.pack(fill="x",pady=3); tk.Label(c,text=("✓" if ok else "⚠")+"  "+name,font=(FONT,11,"bold"),bg=t["card"],fg=t["accent"] if ok else t["danger"]).pack(anchor="w",padx=18,pady=12)


def render_settings():
    clear_content(); t=theme(); label(content,"SETTINGS",24,True).pack(anchor="w"); label(content,"Make Villager Launcher yours. Settings are stored locally.",10,False,t["muted"]).pack(anchor="w",pady=(3,18))
    label(content,"GENERAL",14,True).pack(anchor="w",pady=(0,8));
    var=tk.BooleanVar(value=settings.get("remember_window",True)); tk.Checkbutton(content,text="Remember window size",variable=var,command=lambda:(settings.__setitem__("remember_window",var.get()),save_settings()),font=(FONT,10,"bold"),bg=t["panel"],fg=t["fg"],selectcolor=t["button"],activebackground=t["panel"],activeforeground=t["fg"]).pack(anchor="w")
    label(content,"APPEARANCE",14,True).pack(anchor="w",pady=(22,8)); row=tk.Frame(content,bg=t["panel"]); row.pack(fill="x")
    for n in list(THEMES)+["Custom"]: btn(row,n,lambda x=n:set_theme(x),n==current_theme).pack(side="left",padx=3)
    btn(content,"CREATE CUSTOM THEME",custom_theme_editor).pack(anchor="w",pady=8)
    label(content,"MINECRAFT",14,True).pack(anchor="w",pady=(22,8)); label(content,settings.get("minecraft_path") or "Default: %APPDATA%\\.minecraft",9,False,t["muted"]).pack(anchor="w"); btn(content,"CHOOSE MINECRAFT FOLDER",choose_mc).pack(anchor="w",pady=6); btn(content,"CHOOSE JAVA",choose_java).pack(anchor="w",pady=6)
    label(content,"UPDATES",14,True).pack(anchor="w",pady=(22,8)); btn(content,"CHECK FOR UPDATES",check_updates,True).pack(anchor="w",pady=5)
    label(content,"MINECRAFT OWNERSHIP",14,True).pack(anchor="w",pady=(22,8)); label(content,"Original Minecraft detected" if ownership_verified() else "Not detected — Profiles, PFPs, Mods and Minecraft management are locked.",10,True,t["accent"] if ownership_verified() else t["danger"]).pack(anchor="w")
    btn(content,"RESET ALL SETTINGS",reset_settings).pack(anchor="w",pady=18)


def navigate(page):
    settings["start_page"]=page; save_settings(); render_current()


def render_current():
    {"Home":render_home,"Profiles":render_profiles,"Mods":render_mods,"Versions":render_versions,"Backups":render_backups,"Repair":render_repair,"Settings":render_settings}.get(settings.get("start_page","Home"),render_home)()


def build_ui():
    global sidebar,content,status
    t=theme(); root.configure(bg=t["bg"])
    sidebar=tk.Frame(root,bg=t["panel"],width=225); sidebar.pack(side="left",fill="y"); sidebar.pack_propagate(False)
    tk.Label(sidebar,text="VILLAGER",font=(FONT,18,"bold"),bg=t["panel"],fg=t["fg"]).pack(anchor="w",padx=22,pady=(24,0)); tk.Label(sidebar,text="LAUNCHER",font=(FONT,9,"bold"),bg=t["panel"],fg=t["accent"]).pack(anchor="w",padx=22,pady=(0,25))
    for text,page in (("HOME","Home"),("PROFILES","Profiles"),("MODS","Mods"),("VERSIONS","Versions"),("BACKUPS","Backups"),("REPAIR","Repair"),("SETTINGS","Settings")):
        tk.Button(sidebar,text=text,command=lambda p=page:navigate(p),font=(FONT,10,"bold"),relief="flat",bg=t["panel"],fg=t["fg"],activebackground=t["button"],activeforeground=t["fg"],anchor="w",padx=22,pady=11,cursor="hand2").pack(fill="x")
    main=tk.Frame(root,bg=t["bg"]); main.pack(side="left",fill="both",expand=True)
    top=tk.Frame(main,bg=t["bg"]); top.pack(fill="x",padx=30,pady=(22,0)); tk.Label(top,text="Villager Launcher",font=(FONT,10,"bold"),bg=t["bg"],fg=t["muted"]).pack(side="left"); status=tk.Label(top,text="Ready",font=(FONT,9),bg=t["bg"],fg=t["muted"]); status.pack(side="right")
    content=tk.Frame(main,bg=t["panel"]); content.pack(fill="both",expand=True,padx=25,pady=18)
    render_current()


def rebuild_ui():
    for w in root.winfo_children(): w.destroy()
    build_ui()


def save_window():
    if settings.get("remember_window",True): settings["window_width"]=root.winfo_width(); settings["window_height"]=root.winfo_height(); save_settings()


if len(sys.argv)>=3 and sys.argv[1]=="--install-update": finish_update(sys.argv[2]); raise SystemExit
load_settings(); load_profiles()
root=tk.Tk(); root.title("Villager Launcher 1.6.1"); root.geometry(f"{int(settings.get('window_width',1120))}x{int(settings.get('window_height',720))}"); root.minsize(900,600)
build_ui(); root.protocol("WM_DELETE_WINDOW",lambda:(save_window(),root.destroy())); root.mainloop()
