import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import json, os, sys, tempfile, subprocess, shutil, time, zipfile
from urllib.request import urlopen, Request
from urllib.error import URLError

CURRENT_VERSION = "1.5.0"
BASE_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main"
VERSION_URL = BASE_URL + "/version.json"
LAUNCHER_URL = BASE_URL + "/launcher.py"
COMMITS_URL = "https://api.github.com/repos/windowswindows822-bot/villager-launcher-updates/commits?path=launcher.py&per_page=50"
APP_DIR = os.path.join(os.environ.get("APPDATA", tempfile.gettempdir()), "VillagerLauncher")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
PROFILES_FILE = os.path.join(APP_DIR, "profiles.json")

FONT = "Segoe UI Variable"
FALLBACK_FONT = "Segoe UI"

THEMES = {
    "Villager Green": {"bg":"#101810","panel":"#182418","card":"#203020","fg":"#FFFFFF","muted":"#AFC3AF","accent":"#62C462","button":"#2D442D","danger":"#B94A48"},
    "Midnight": {"bg":"#0A0E18","panel":"#121827","card":"#1A2338","fg":"#FFFFFF","muted":"#AAB6D3","accent":"#7188FF","button":"#29365B","danger":"#D05B5B"},
    "Sky": {"bg":"#DCEFF8","panel":"#F7FCFF","card":"#EAF5FA","fg":"#173042","muted":"#5C7180","accent":"#3A91C9","button":"#C7E0ED","danger":"#B64E4E"},
    "Nether": {"bg":"#180C0C","panel":"#2A1212","card":"#391919","fg":"#FFFFFF","muted":"#D0A8A8","accent":"#E05A5A","button":"#542626","danger":"#FF8A70"},
    "Ocean": {"bg":"#071820","panel":"#0D2833","card":"#123743","fg":"#FFFFFF","muted":"#9FC5D0","accent":"#38A7C7","button":"#1B4655","danger":"#D45D67"}
}
DEFAULT_SETTINGS = {
    "theme":"Villager Green", "remember_window":True, "window_width":1120, "window_height":720,
    "minecraft_path":"", "java_path":"", "ui_scale":1.0, "show_release_notes":True,
    "confirm_updates":True, "keep_launcher_open":False, "diagnostic_logging":False,
    "start_page":"Home"
}
settings = dict(DEFAULT_SETTINGS)
current_theme_name = "Villager Green"
custom_theme = None
profiles = []
selected_profile = None

root = None
content = None
status = None


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (OSError, json.JSONDecodeError):
        return default


def load_settings():
    global settings, current_theme_name, custom_theme
    data = load_json(SETTINGS_FILE, {})
    if isinstance(data, dict):
        for key in DEFAULT_SETTINGS:
            if key in data:
                settings[key] = data[key]
        if data.get("theme") in THEMES:
            current_theme_name = data["theme"]
        elif data.get("theme") == "Custom" and isinstance(data.get("custom_theme"), dict):
            custom_theme = data["custom_theme"]
            current_theme_name = "Custom"


def save_settings():
    try:
        os.makedirs(APP_DIR, exist_ok=True)
        data = dict(settings)
        data["theme"] = current_theme_name
        if current_theme_name == "Custom" and custom_theme:
            data["custom_theme"] = custom_theme
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def load_profiles():
    global profiles
    data = load_json(PROFILES_FILE, [])
    profiles = data if isinstance(data, list) else []
    if not profiles:
        profiles.append({"name":"Default", "version":"", "loader":"Vanilla", "description":"Your first Villager Launcher profile.", "pfile":""})
        save_profiles()


def save_profiles():
    try:
        os.makedirs(APP_DIR, exist_ok=True)
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2)
    except OSError:
        pass


def theme():
    if current_theme_name == "Custom" and custom_theme:
        return custom_theme
    return THEMES.get(current_theme_name, THEMES["Villager Green"])


def github_request(url, timeout=10):
    request = Request(url + ("&" if "?" in url else "?") + "t=" + str(time.time_ns()), headers={"User-Agent":"Villager-Launcher"})
    return urlopen(request, timeout=timeout)


def latest_info():
    with github_request(VERSION_URL, 5) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict) or not data.get("version"):
        raise ValueError("Version information is missing.")
    return data


def download_url(url, filename):
    with github_request(url, 15) as response:
        data = response.read()
    if not data:
        raise ValueError("Downloaded file is empty.")
    path = os.path.join(tempfile.gettempdir(), filename)
    with open(path, "wb") as f:
        f.write(data)
    return path


def finish_update_from_temp(target):
    source = os.path.abspath(sys.argv[0])
    target = os.path.abspath(target)
    time.sleep(2)
    for _ in range(30):
        try:
            shutil.copy2(source, target)
            subprocess.Popen([sys.executable, target], close_fds=True)
            try: os.remove(source)
            except OSError: pass
            return
        except OSError:
            time.sleep(1)
    try: messagebox.showerror("Update Error", "Windows could not replace the old launcher file.")
    except tk.TclError: pass


def install_update(path):
    current = os.path.abspath(sys.argv[0])
    subprocess.Popen([sys.executable, path, "--install-update", current], creationflags=subprocess.CREATE_NO_WINDOW, close_fds=True)
    root.destroy()


def check_for_updates():
    try:
        status.config(text="Checking for updates...")
        info = latest_info()
        newest = str(info["version"])
        if newest == CURRENT_VERSION:
            status.config(text="Up to date")
            messagebox.showinfo("Updates", f"Villager Launcher is up to date!\n\nInstalled: {CURRENT_VERSION}\nServer: {newest}")
            return
        path = download_url(LAUNCHER_URL, "villager_launcher_update.py")
        notes = release_text(info)
        if settings.get("confirm_updates", True):
            if not messagebox.askyesno("Update Available", f"Version {newest} is available.\n\nWHAT'S NEW\n{notes}\n\nInstall now?"):
                status.config(text="Update canceled")
                return
        install_update(path)
    except Exception as e:
        status.config(text="Update failed")
        messagebox.showerror("Update Error", str(e))


def release_text(info):
    notes = info.get("notes", {})
    if not isinstance(notes, dict): return str(notes)
    parts = []
    for key in ("Added", "Changed", "Removed", "Fixed"):
        items = notes.get(key, [])
        if isinstance(items, str): items = [items]
        if items: parts.append(key.upper() + "\n" + "\n".join("• " + str(x) for x in items))
    return "\n\n".join(parts) or "No changes listed."


def minecraft_dir():
    custom = settings.get("minecraft_path", "")
    if custom and os.path.isdir(custom): return custom
    app = os.environ.get("APPDATA")
    return os.path.join(app, ".minecraft") if app else None


def choose_minecraft_dir():
    path = filedialog.askdirectory(title="Choose your Minecraft folder")
    if path:
        settings["minecraft_path"] = path
        save_settings()
        render_settings()


def choose_java():
    path = filedialog.askopenfilename(title="Choose Java executable", filetypes=[("Java executable", "java.exe"), ("All files", "*.*")])
    if path:
        settings["java_path"] = path
        save_settings()
        render_settings()


def installed_versions():
    base = minecraft_dir()
    folder = os.path.join(base, "versions") if base else ""
    if not os.path.isdir(folder): return []
    try: return sorted([x for x in os.listdir(folder) if os.path.isdir(os.path.join(folder, x))], reverse=True)
    except OSError: return []


def open_folder(path):
    if os.path.isdir(path):
        os.startfile(path)
    else:
        messagebox.showerror("Folder not found", "That folder does not exist yet.")


def play_selected():
    mc = minecraft_dir()
    if not mc or not os.path.isdir(mc):
        messagebox.showerror("Minecraft Required", "You need to buy and own an original Minecraft installation before Villager Launcher can use Minecraft.")
        root.destroy()
        return
    messagebox.showinfo("Minecraft", "Minecraft installation detected.\n\nLaunch integration will be enabled in a future release.")


def clear_content():
    for widget in content.winfo_children(): widget.destroy()


def label(parent, text, size=10, bold=False, fg=None):
    t = theme(); return tk.Label(parent, text=text, font=(FONT, size, "bold" if bold else "normal"), bg=t["panel"], fg=fg or t["fg"])


def button(parent, text, command, accent=False, width=None):
    t = theme(); return tk.Button(parent, text=text, command=command, font=(FONT, 10, "bold"), relief="flat", bd=0, bg=t["accent"] if accent else t["button"], fg="#FFFFFF" if accent else t["fg"], activebackground=t["accent"], activeforeground="#FFFFFF", padx=16, pady=9, cursor="hand2", width=width)


def card(parent):
    return tk.Frame(parent, bg=theme()["card"], bd=0, highlightthickness=0)


def home():
    clear_content(); t = theme()
    label(content, "Ready to meet your wishes?", 28, True).pack(anchor="w", pady=(0, 4))
    label(content, "Your Galaxy, Your Way.", 13, False, t["muted"]).pack(anchor="w", pady=(0, 22))
    p = selected_profile or profiles[0]
    c = card(content); c.pack(fill="x", pady=5)
    inner = tk.Frame(c, bg=t["card"]); inner.pack(fill="x", padx=24, pady=22)
    pfp = load_pfp(p, 82)
    if pfp:
        w = tk.Label(inner, image=pfp, bg=t["card"]); w.image=pfp; w.pack(side="left", padx=(0,20))
    else:
        tk.Label(inner, text="👤", font=(FONT, 40), bg=t["card"], fg=t["fg"]).pack(side="left", padx=(0,20))
    info = tk.Frame(inner, bg=t["card"]); info.pack(side="left", fill="x", expand=True)
    tk.Label(info, text=p.get("name","Profile"), font=(FONT,18,"bold"), bg=t["card"], fg=t["fg"]).pack(anchor="w")
    tk.Label(info, text=(p.get("version") or "No version selected") + "  •  " + p.get("loader","Vanilla"), font=(FONT,10), bg=t["card"], fg=t["muted"]).pack(anchor="w", pady=4)
    button(inner, "PLAY", play_selected, True).pack(side="right")
    stats = tk.Frame(content, bg=t["panel"]); stats.pack(fill="x", pady=18)
    for title, value in (("Profiles", str(len(profiles))), ("Versions", str(len(installed_versions()))), ("Mods", str(len(mod_files())))):
        c = card(stats); c.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(c, text=value, font=(FONT,22,"bold"), bg=t["card"], fg=t["accent"]).pack(pady=(14,0))
        tk.Label(c, text=title, font=(FONT,9), bg=t["card"], fg=t["muted"]).pack(pady=(0,14))


def load_pfp(profile, size):
    path = profile.get("pfile", "")
    if not path or not os.path.isfile(path): return None
    try:
        image = tk.PhotoImage(file=path)
        factor = max(1, int(max(image.width(), image.height()) / size))
        if factor > 1: image = image.subsample(factor, factor)
        return image
    except tk.TclError:
        return None


def choose_pfp(index):
    path = filedialog.askopenfilename(title="Choose profile picture", filetypes=[("PNG images","*.png"), ("GIF images","*.gif"), ("BMP images","*.bmp"), ("All files","*.*")])
    if path:
        profiles[index]["pfile"] = path
        save_profiles(); render_profiles()


def create_profile():
    name = simple_prompt("New Profile", "Profile name:")
    if not name: return
    profiles.append({"name":name, "version":"", "loader":"Vanilla", "description":"", "pfile":""})
    save_profiles(); render_profiles()


def simple_prompt(title, prompt):
    win = tk.Toplevel(root); win.title(title); win.geometry("430x170"); win.configure(bg=theme()["panel"]); win.grab_set()
    label(win, prompt, 11, True).pack(anchor="w", padx=25, pady=(25,8))
    entry = tk.Entry(win, font=(FONT,11)); entry.pack(fill="x", padx=25); entry.focus_set(); result=[]
    def done(): result.append(entry.get().strip()); win.destroy()
    button(win,"Create",done,True).pack(anchor="e", padx=25, pady=18)
    win.wait_window(); return result[0] if result else ""


def render_profiles():
    clear_content(); label(content,"PROFILES",24,True).pack(anchor="w"); label(content,"Separate Minecraft setups with their own identity and settings.",10,False,theme()["muted"]).pack(anchor="w",pady=(3,18)); button(content,"+ NEW PROFILE",create_profile,True).pack(anchor="w",pady=(0,12))
    for i,p in enumerate(profiles):
        c=card(content); c.pack(fill="x",pady=5); inner=tk.Frame(c,bg=theme()["card"]); inner.pack(fill="x",padx=18,pady=14)
        pic=load_pfp(p,55)
        if pic:
            x=tk.Label(inner,image=pic,bg=theme()["card"]); x.image=pic; x.pack(side="left",padx=(0,14))
        else: tk.Label(inner,text="👤",font=(FONT,27),bg=theme()["card"],fg=theme()["fg"]).pack(side="left",padx=(0,14))
        text=tk.Frame(inner,bg=theme()["card"]); text.pack(side="left",fill="x",expand=True); tk.Label(text,text=p.get("name","Profile"),font=(FONT,14,"bold"),bg=theme()["card"],fg=theme()["fg"]).pack(anchor="w"); tk.Label(text,text=(p.get("version") or "No version")+" • "+p.get("loader","Vanilla"),font=(FONT,9),bg=theme()["card"],fg=theme()["muted"]).pack(anchor="w")
        button(inner,"CHOOSE PFP",lambda n=i: choose_pfp(n)).pack(side="right",padx=5); button(inner,"SELECT",lambda n=i: select_profile(n),True).pack(side="right",padx=5)


def select_profile(index):
    global selected_profile
    selected_profile = profiles[index]; home()


def mod_files():
    mc=minecraft_dir(); folder=os.path.join(mc,"mods") if mc else ""
    if not os.path.isdir(folder): return []
    try: return [x for x in os.listdir(folder) if x.lower().endswith(".jar")]
    except OSError: return []


def render_mods():
    clear_content(); label(content,"MOD MANAGER",24,True).pack(anchor="w"); label(content,"Enable, disable and import mods without permanently deleting them.",10,False,theme()["muted"]).pack(anchor="w",pady=(3,18))
    mc=minecraft_dir(); folder=os.path.join(mc,"mods") if mc else ""
    if not mc or not os.path.isdir(mc):
        label(content,"Minecraft folder not detected.",12,True).pack(anchor="w",pady=25); button(content,"OPEN SETTINGS",render_settings,True).pack(anchor="w"); return
    button(content,"IMPORT .JAR",import_mod,True).pack(anchor="w",pady=(0,15));
    for name in mod_files():
        c=card(content); c.pack(fill="x",pady=3); tk.Label(c,text=name,font=(FONT,10),bg=theme()["card"],fg=theme()["fg"]).pack(side="left",padx=15,pady=10); button(c,"DISABLE",lambda n=name:disable_mod(n)).pack(side="right",padx=10,pady=5)


def import_mod():
    mc=minecraft_dir(); folder=os.path.join(mc,"mods") if mc else ""
    if not folder: return
    files=filedialog.askopenfilenames(title="Import Minecraft mods",filetypes=[("Minecraft mods","*.jar"),("All files","*.*")])
    if files:
        os.makedirs(folder,exist_ok=True)
        for f in files:
            try: shutil.copy2(f,os.path.join(folder,os.path.basename(f)))
            except OSError: pass
        render_mods()


def disable_mod(name):
    mc=minecraft_dir(); src=os.path.join(mc,"mods",name); dst=os.path.join(mc,"mods_disabled",name)
    try: os.makedirs(os.path.dirname(dst),exist_ok=True); shutil.move(src,dst); render_mods()
    except OSError as e: messagebox.showerror("Mod Error",str(e))


def render_versions():
    clear_content(); label(content,"MINECRAFT VERSIONS",24,True).pack(anchor="w"); label(content,"Versions already installed in your Minecraft folder.",10,False,theme()["muted"]).pack(anchor="w",pady=(3,18))
    versions=installed_versions()
    if not versions: label(content,"No installed versions were found.",12,False,theme()["muted"]).pack(anchor="w",pady=25); return
    for v in versions:
        c=card(content); c.pack(fill="x",pady=3); tk.Label(c,text=v,font=(FONT,11,"bold"),bg=theme()["card"],fg=theme()["fg"]).pack(side="left",padx=18,pady=12); tk.Label(c,text="Installed",font=(FONT,9),bg=theme()["card"],fg=theme()["muted"]).pack(side="right",padx=18)


def render_backups():
    clear_content(); label(content,"BACKUP CENTER",24,True).pack(anchor="w"); label(content,"Protect important Minecraft data before making changes.",10,False,theme()["muted"]).pack(anchor="w",pady=(3,18)); button(content,"CREATE BACKUP",create_backup,True).pack(anchor="w")
    mc=minecraft_dir(); backup=os.path.join(mc,"villager_launcher_backups") if mc else ""
    if os.path.isdir(backup):
        label(content,"Existing backups",13,True).pack(anchor="w",pady=(25,10))
        for n in sorted(os.listdir(backup),reverse=True):
            tk.Label(content,text=n,font=(FONT,10),bg=theme()["panel"],fg=theme()["fg"]).pack(anchor="w",pady=3)


def create_backup():
    mc=minecraft_dir()
    if not mc or not os.path.isdir(mc): messagebox.showerror("Backup","Minecraft folder not found."); return
    backup=os.path.join(mc,"villager_launcher_backups"); os.makedirs(backup,exist_ok=True); stamp=time.strftime("backup_%Y%m%d_%H%M%S"); target=os.path.join(backup,stamp+".zip")
    try:
        with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED) as z:
            for folder in ("saves","mods","resourcepacks","config"):
                source=os.path.join(mc,folder)
                if os.path.isdir(source):
                    for base,_,files in os.walk(source):
                        for f in files:
                            path=os.path.join(base,f); z.write(path,os.path.relpath(path,mc))
        messagebox.showinfo("Backup Created","Minecraft backup created safely.\n\n"+target); render_backups()
    except OSError as e: messagebox.showerror("Backup Error",str(e))


def render_repair():
    clear_content(); label(content,"REPAIR CENTER",24,True).pack(anchor="w"); label(content,"Diagnostics that explain what Villager Launcher can see.",10,False,theme()["muted"]).pack(anchor="w",pady=(3,18))
    mc=minecraft_dir(); checks=[("Minecraft folder",bool(mc and os.path.isdir(mc))), ("Versions folder",bool(mc and os.path.isdir(os.path.join(mc,"versions")))), ("Mods folder",bool(mc and os.path.isdir(os.path.join(mc,"mods")))), ("Settings",os.path.isfile(SETTINGS_FILE))]
    for name,ok in checks:
        c=card(content); c.pack(fill="x",pady=3); tk.Label(c,text=("✓" if ok else "⚠")+"  "+name,font=(FONT,11,"bold"),bg=theme()["card"],fg=theme()["accent"] if ok else theme()["danger"]).pack(anchor="w",padx=18,pady=12)
    button(content,"RESTART LAUNCHER",repair_restart,True).pack(anchor="w",pady=18)


def repair_restart():
    path=download_url(LAUNCHER_URL,"villager_launcher_repair.py"); install_update(path)


def render_settings():
    clear_content(); label(content,"SETTINGS",24,True).pack(anchor="w"); label(content,"Make Villager Launcher yours. Settings are stored locally.",10,False,theme()["muted"]).pack(anchor="w",pady=(3,18))
    settings_section("GENERAL", [("Remember window size", "remember_window", True), ("Keep launcher open after Play", "keep_launcher_open", False), ("Show release notes", "show_release_notes", True)])
    label(content,"APPEARANCE",14,True).pack(anchor="w",pady=(22,8));
    row=tk.Frame(content,bg=theme()["panel"]); row.pack(fill="x",pady=5); tk.Label(row,text="Theme",font=(FONT,10,"bold"),bg=theme()["panel"],fg=theme()["fg"]).pack(side="left")
    for name in list(THEMES)+["Custom"]: button(row,name,lambda n=name: choose_theme(n),name==current_theme_name).pack(side="left",padx=3)
    button(content,"CREATE CUSTOM THEME",custom_theme_editor).pack(anchor="w",pady=8)
    label(content,"MINECRAFT",14,True).pack(anchor="w",pady=(22,8));
    tk.Label(content,text=settings.get("minecraft_path") or "Default: %APPDATA%\\.minecraft",font=(FONT,9),bg=theme()["panel"],fg=theme()["muted"],wraplength=750).pack(anchor="w"); button(content,"CHOOSE MINECRAFT FOLDER",choose_minecraft_dir).pack(anchor="w",pady=6)
    tk.Label(content,text=settings.get("java_path") or "Java path not set",font=(FONT,9),bg=theme()["panel"],fg=theme()["muted"],wraplength=750).pack(anchor="w"); button(content,"CHOOSE JAVA",choose_java).pack(anchor="w",pady=6)
    label(content,"UPDATES",14,True).pack(anchor="w",pady=(22,8)); settings_section("", [("Confirm before installing updates", "confirm_updates", True)])
    button(content,"CHECK FOR UPDATES",check_for_updates,True).pack(anchor="w",pady=5); button(content,"RESET ALL SETTINGS",reset_settings).pack(anchor="w",pady=5)


def settings_section(title, items):
    if title: label(content,title,14,True).pack(anchor="w",pady=(0,8))
    for text,key,default in items:
        var=tk.BooleanVar(value=bool(settings.get(key,default))); row=tk.Frame(content,bg=theme()["panel"]); row.pack(fill="x",pady=3); tk.Checkbutton(row,text=text,variable=var,font=(FONT,10,"bold"),bg=theme()["panel"],fg=theme()["fg"],selectcolor=theme()["button"],activebackground=theme()["panel"],activeforeground=theme()["fg"],command=lambda k=key,v=var:(settings.__setitem__(k,v.get()),save_settings())).pack(anchor="w")


def choose_theme(name):
    global current_theme_name, custom_theme
    if name in THEMES: current_theme_name=name
    elif name=="Custom" and custom_theme: current_theme_name="Custom"
    save_settings(); apply_theme(); render_current()


def custom_theme_editor():
    global custom_theme,current_theme_name
    base=dict(theme()); chosen=colorchooser.askcolor(title="Choose theme accent",initialcolor=base["accent"])[1]
    if not chosen: return
    custom_theme=dict(base); custom_theme["accent"]=chosen; custom_theme["button"]=chosen; current_theme_name="Custom"; save_settings(); apply_theme(); render_settings()


def reset_settings():
    global settings,current_theme_name,custom_theme
    if not messagebox.askyesno("Reset Settings","Reset Villager Launcher settings? Your Minecraft files and profiles will not be deleted."): return
    settings=dict(DEFAULT_SETTINGS); current_theme_name="Villager Green"; custom_theme=None; save_settings(); apply_theme(); render_settings()


def apply_theme():
    t=theme(); root.configure(bg=t["bg"])
    try: root.option_add("*Font", (FONT,10))
    except tk.TclError: pass


def render_current():
    page=settings.get("start_page","Home")
    if page=="Home": home()
    elif page=="Profiles": render_profiles()
    elif page=="Mods": render_mods()
    elif page=="Versions": render_versions()
    elif page=="Backups": render_backups()
    elif page=="Repair": render_repair()
    else: render_settings()


def navigate(page):
    settings["start_page"]=page; save_settings(); render_current()


def build_ui():
    global content,status
    t=theme(); root.configure(bg=t["bg"])
    sidebar=tk.Frame(root,bg=t["panel"],width=225); sidebar.pack(side="left",fill="y"); sidebar.pack_propagate(False)
    tk.Label(sidebar,text="VILLAGER",font=(FONT,18,"bold"),bg=t["panel"],fg=t["fg"]).pack(anchor="w",padx=22,pady=(24,0)); tk.Label(sidebar,text="LAUNCHER",font=(FONT,9,"bold"),bg=t["panel"],fg=t["accent"]).pack(anchor="w",padx=22,pady=(0,25))
    for text,page in (("HOME","Home"),("PROFILES","Profiles"),("MODS","Mods"),("VERSIONS","Versions"),("BACKUPS","Backups"),("REPAIR","Repair"),("SETTINGS","Settings")):
        b=tk.Button(sidebar,text=text,command=lambda p=page:navigate(p),font=(FONT,10,"bold"),relief="flat",bg=t["panel"],fg=t["fg"],activebackground=t["button"],activeforeground=t["fg"],anchor="w",padx=22,pady=11,cursor="hand2"); b.pack(fill="x")
    main=tk.Frame(root,bg=t["bg"]); main.pack(side="left",fill="both",expand=True)
    top=tk.Frame(main,bg=t["bg"]); top.pack(fill="x",padx=30,pady=(22,0)); tk.Label(top,text="Villager Launcher",font=(FONT,10,"bold"),bg=t["bg"],fg=t["muted"]).pack(side="left"); status=tk.Label(top,text="Ready",font=(FONT,9),bg=t["bg"],fg=t["muted"]); status.pack(side="right")
    content=tk.Frame(main,bg=t["panel"]); content.pack(fill="both",expand=True,padx=25,pady=18); 
    render_current()


def save_window():
    if settings.get("remember_window",True):
        settings["window_width"]=root.winfo_width(); settings["window_height"]=root.winfo_height(); save_settings()


if len(sys.argv)>=3 and sys.argv[1]=="--install-update":
    finish_update_from_temp(sys.argv[2]); raise SystemExit

load_settings(); load_profiles()
root=tk.Tk(); root.title("Villager Launcher 1.5.0"); root.geometry(f"{int(settings.get('window_width',1120))}x{int(settings.get('window_height',720))}"); root.minsize(900,600)
build_ui(); root.protocol("WM_DELETE_WINDOW", lambda:(save_window(),root.destroy())); root.mainloop()
