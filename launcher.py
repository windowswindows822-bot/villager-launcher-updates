import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import json, os, sys, tempfile, subprocess, shutil, time, zipfile
from urllib.request import urlopen, Request

CURRENT_VERSION = "1.6.2"
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


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def save_settings():
    try:
        os.makedirs(APP_DIR, exist_ok=True)
        data = dict(settings)
        data["theme"] = current_theme
        if current_theme == "Custom" and custom_theme:
            data["custom_theme"] = custom_theme
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def load_settings():
    global settings, current_theme, custom_theme
    data = load_json(SETTINGS_FILE, {})
    if isinstance(data, dict):
        for key in DEFAULT_SETTINGS:
            if key in data:
                settings[key] = data[key]
        if data.get("theme") in THEMES:
            current_theme = data["theme"]
        elif data.get("theme") == "Custom" and isinstance(data.get("custom_theme"), dict):
            custom_theme = data["custom_theme"]
            current_theme = "Custom"


def save_profiles():
    try:
        os.makedirs(APP_DIR, exist_ok=True)
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2)
    except OSError:
        pass


def load_profiles():
    global profiles, selected_profile
    data = load_json(PROFILES_FILE, [])
    profiles = data if isinstance(data, list) else []
    if not profiles:
        profiles = [{"name":"Default","version":"","loader":"Vanilla","description":"Your first Villager Launcher profile.","pfile":""}]
        save_profiles()
    selected_profile = min(selected_profile, len(profiles) - 1)


def theme():
    if current_theme == "Custom" and custom_theme:
        return custom_theme
    return THEMES.get(current_theme, THEMES["Villager Green"])


def github_request(url, timeout=10):
    cache_buster = "&" if "?" in url else "?"
    return urlopen(Request(url + cache_buster + "t=" + str(time.time_ns()), headers={"User-Agent":"Villager-Launcher"}), timeout=timeout)


def latest_info():
    with github_request(VERSION_URL, 5) as response:
        data = json.loads(response.read().decode("utf-8"))
    if not isinstance(data, dict) or not data.get("version"):
        raise ValueError("Version information is missing.")
    return data


def download_update():
    with github_request(LAUNCHER_URL, 15) as response:
        data = response.read()
    if not data:
        raise ValueError("Downloaded launcher is empty.")
    path = os.path.join(tempfile.gettempdir(), "villager_launcher_update.py")
    with open(path, "wb") as f:
        f.write(data)
    return path


def finish_update(target):
    source = os.path.abspath(sys.argv[0])
    target = os.path.abspath(target)
    time.sleep(2)
    for _ in range(30):
        try:
            shutil.copy2(source, target)
            subprocess.Popen([sys.executable, target], close_fds=True)
            try:
                os.remove(source)
            except OSError:
                pass
            return
        except OSError:
            time.sleep(1)
    try:
        messagebox.showerror("Update Error", "Windows could not replace the launcher file.")
    except tk.TclError:
        pass


def install_update(path):
    subprocess.Popen([sys.executable, path, "--install-update", os.path.abspath(sys.argv[0])], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), close_fds=True)
    root.destroy()


def release_text(info):
    notes = info.get("notes", {})
    if not isinstance(notes, dict):
        return str(notes)
    parts = []
    for key in ("Added", "Changed", "Removed", "Fixed"):
        items = notes.get(key, [])
        if isinstance(items, str):
            items = [items]
        if items:
            parts.append(key.upper() + "\n" + "\n".join("• " + str(x) for x in items))
    return "\n\n".join(parts) or "No changes listed."


def check_updates():
    try:
        status.config(text="Checking for updates...")
        info = latest_info()
        newest = str(info["version"])
        if newest == CURRENT_VERSION:
            status.config(text="Up to date")
            messagebox.showinfo("Updates", f"Villager Launcher is up to date!\n\nInstalled: {CURRENT_VERSION}\nServer: {newest}")
            return
        notes = release_text(info)
        if settings.get("confirm_updates", True) and not messagebox.askyesno("Update Available", f"Version {newest} is available.\n\nWHAT'S NEW\n{notes}\n\nInstall now?"):
            status.config(text="Update available")
            return
        status.config(text="Installing update...")
        install_update(download_update())
    except Exception as exc:
        status.config(text="Update failed")
        messagebox.showerror("Update Error", str(exc))


def mc_dir():
    configured = settings.get("minecraft_path", "")
    if configured and os.path.isdir(configured):
        return configured
    appdata = os.environ.get("APPDATA")
    return os.path.join(appdata, ".minecraft") if appdata else None


def ownership_verified():
    folder = mc_dir()
    if not folder or not os.path.isdir(folder):
        return False
    return os.path.isfile(os.path.join(folder, "launcher_accounts.json")) or os.path.isfile(os.path.join(folder, "launcher_profiles.json"))


def require_minecraft(feature):
    if ownership_verified():
        return True
    messagebox.showwarning("Minecraft Required", f"{feature} is locked until an original Minecraft installation is detected.\n\nSign in through the official Minecraft launcher and select its Minecraft data folder in Villager Launcher Settings.")
    return False


def installed_versions():
    folder = os.path.join(mc_dir(), "versions") if mc_dir() else ""
    if not os.path.isdir(folder):
        return []
    try:
        return sorted([x for x in os.listdir(folder) if os.path.isdir(os.path.join(folder, x))], reverse=True)
    except OSError:
        return []


def mod_files():
    folder = os.path.join(mc_dir(), "mods") if mc_dir() else ""
    if not os.path.isdir(folder):
        return []
    try:
        return sorted([x for x in os.listdir(folder) if x.lower().endswith(".jar")])
    except OSError:
        return []


def load_pfp(profile, size):
    path = profile.get("pfile", "")
    if not path or not os.path.isfile(path):
        return None
    try:
        image = tk.PhotoImage(file=path)
        factor = max(1, int(max(image.width(), image.height()) / size))
        return image.subsample(factor, factor) if factor > 1 else image
    except tk.TclError:
        return None


def pick_pfp(index):
    if not require_minecraft("Profile pictures"):
        return
    path = filedialog.askopenfilename(title="Choose profile picture", filetypes=[("PNG images", "*.png"), ("GIF images", "*.gif"), ("BMP images", "*.bmp")])
    if path:
        profiles[index]["pfile"] = path
        save_profiles()
        rebuild_ui()


def create_profile():
    if not require_minecraft("Profiles"):
        return
    win = tk.Toplevel(root)
    win.title("New Profile")
    win.geometry("430x180")
    win.configure(bg=theme()["panel"])
    win.grab_set()
    label(win, "Profile name", 11, True).pack(anchor="w", padx=25, pady=(25, 8))
    entry = tk.Entry(win, font=(FONT, 11))
    entry.pack(fill="x", padx=25)
    entry.focus_set()
    def done():
        name = entry.get().strip()
        if name:
            profiles.append({"name":name,"version":"","loader":"Vanilla","description":"","pfile":""})
            save_profiles()
            win.destroy()
            rebuild_ui()
    btn(win, "CREATE", done, True).pack(anchor="e", padx=25, pady=18)


def choose_mc():
    path = filedialog.askdirectory(title="Choose Minecraft folder")
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


def set_theme(name):
    global current_theme
    if name in THEMES:
        current_theme = name
    elif name == "Custom" and custom_theme:
        current_theme = "Custom"
    save_settings()
    rebuild_ui()


def custom_theme_editor():
    global custom_theme, current_theme
    chosen = colorchooser.askcolor(title="Choose theme accent", initialcolor=theme()["accent"])[1]
    if chosen:
        custom_theme = dict(theme())
        custom_theme["accent"] = chosen
        custom_theme["button"] = chosen
        current_theme = "Custom"
        save_settings()
        rebuild_ui()


def reset_settings():
    global settings, current_theme, custom_theme
    if not messagebox.askyesno("Reset Settings", "Reset Villager Launcher settings? Your Minecraft files and profiles will not be deleted."):
        return
    settings = dict(DEFAULT_SETTINGS)
    current_theme = "Villager Green"
    custom_theme = None
    save_settings()
    rebuild_ui()


def play_selected():
    if not require_minecraft("Minecraft launching"):
        return
    messagebox.showinfo("Minecraft", "Original Minecraft installation detected.\n\nLaunch integration will be enabled in a future release.")


def import_mod():
    if not require_minecraft("Mods"):
        return
    folder = os.path.join(mc_dir(), "mods")
    files = filedialog.askopenfilenames(title="Import Minecraft mods", filetypes=[("Minecraft mods", "*.jar")])
    if not files:
        return
    try:
        os.makedirs(folder, exist_ok=True)
        for source in files:
            shutil.copy2(source, os.path.join(folder, os.path.basename(source)))
        render_mods()
    except OSError as exc:
        messagebox.showerror("Mod Error", str(exc))


def disable_mod(name):
    if not require_minecraft("Mods"):
        return
    try:
        disabled = os.path.join(mc_dir(), "mods_disabled")
        os.makedirs(disabled, exist_ok=True)
        shutil.move(os.path.join(mc_dir(), "mods", name), os.path.join(disabled, name))
        render_mods()
    except OSError as exc:
        messagebox.showerror("Mod Error", str(exc))


def create_backup():
    if not require_minecraft("Backups"):
        return
    mc = mc_dir()
    folder = os.path.join(mc, "villager_launcher_backups")
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, time.strftime("backup_%Y%m%d_%H%M%S.zip"))
    try:
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            for part in ("saves", "mods", "resourcepacks", "config"):
                source = os.path.join(mc, part)
                if os.path.isdir(source):
                    for base, _, files in os.walk(source):
                        for name in files:
                            path = os.path.join(base, name)
                            archive.write(path, os.path.relpath(path, mc))
        messagebox.showinfo("Backup Created", "Minecraft backup created safely.\n\n" + target)
        render_backups()
    except OSError as exc:
        messagebox.showerror("Backup Error", str(exc))


def clear_content():
    for widget in content.winfo_children():
        widget.destroy()


def label(parent, text, size=10, bold=False, fg=None, bg=None):
    colors = theme()
    return tk.Label(parent, text=text, font=(FONT, size, "bold" if bold else "normal"), bg=bg or colors["panel"], fg=fg or colors["fg"])


def btn(parent, text, command, accent=False):
    colors = theme()
    return tk.Button(parent, text=text, command=command, font=(FONT, 10, "bold"), relief="flat", bd=0, bg=colors["accent"] if accent else colors["button"], fg="white" if accent else colors["fg"], activebackground=colors["accent"], activeforeground="white", padx=16, pady=9, cursor="hand2")


def card(parent):
    return tk.Frame(parent, bg=theme()["card"], bd=0, highlightthickness=0)


def render_home():
    clear_content()
    colors = theme()
    profile = profiles[selected_profile] if profiles else {"name":"Profile","version":"","loader":"Vanilla","pfile":""}
    label(content, "Ready to meet your wishes?", 28, True).pack(anchor="w", pady=(0, 4))
    label(content, "Your Minecraft, Your Way.", 13, False, colors["muted"]).pack(anchor="w", pady=(0, 22))
    c = card(content)
    c.pack(fill="x", pady=5)
    inner = tk.Frame(c, bg=colors["card"])
    inner.pack(fill="x", padx=24, pady=22)
    info = tk.Frame(inner, bg=colors["card"])
    info.pack(side="left", fill="x", expand=True)
    tk.Label(info, text=profile.get("name", "Profile"), font=(FONT, 18, "bold"), bg=colors["card"], fg=colors["fg"]).pack(anchor="w")
    tk.Label(info, text=(profile.get("version") or "No version selected") + "  •  " + profile.get("loader", "Vanilla"), font=(FONT, 10), bg=colors["card"], fg=colors["muted"]).pack(anchor="w", pady=4)
    if ownership_verified():
        btn(inner, "PLAY", play_selected, True).pack(side="right")
    else:
        btn(inner, "LOCKED — OWN MINECRAFT", lambda: require_minecraft("Minecraft features")).pack(side="right")
    stats = tk.Frame(content, bg=colors["panel"])
    stats.pack(fill="x", pady=18)
    values = (("Profiles", str(len(profiles)) if ownership_verified() else "Locked"), ("Versions", str(len(installed_versions())) if ownership_verified() else "Locked"), ("Mods", str(len(mod_files())) if ownership_verified() else "Locked"))
    for title, value in values:
        box = card(stats)
        box.pack(side="left", fill="both", expand=True, padx=5)
        tk.Label(box, text=value, font=(FONT, 22, "bold"), bg=colors["card"], fg=colors["fg"]).pack(pady=(18, 0))
        tk.Label(box, text=title, font=(FONT, 9), bg=colors["card"], fg=colors["muted"]).pack(pady=(2, 18))


def render_profiles():
    clear_content()
    colors = theme()
    label(content, "Profiles", 26, True).pack(anchor="w")
    label(content, "Manage Minecraft profiles and profile pictures.", 11, False, colors["muted"]).pack(anchor="w", pady=(3, 18))
    if not ownership_verified():
        c = card(content); c.pack(fill="x", pady=5)
        label(c, "Profiles are locked", 16, True, bg=colors["card"]).pack(anchor="w", padx=22, pady=(20, 5))
        label(c, "Original Minecraft must be detected before profiles and PFPs can be used.", 10, False, colors["muted"], colors["card"]).pack(anchor="w", padx=22, pady=(0, 20))
        return
    btn(content, "+ NEW PROFILE", create_profile, True).pack(anchor="e", pady=(0, 12))
    for index, profile in enumerate(profiles):
        c = card(content); c.pack(fill="x", pady=5)
        inner = tk.Frame(c, bg=colors["card"]); inner.pack(fill="x", padx=20, pady=15)
        image = load_pfp(profile, 54)
        if image:
            pic = tk.Label(inner, image=image, bg=colors["card"]); pic.image=image; pic.pack(side="left", padx=(0, 16))
        else:
            tk.Label(inner, text="PFP", font=(FONT, 9, "bold"), width=6, height=3, bg=colors["button"], fg=colors["muted"]).pack(side="left", padx=(0, 16))
        info = tk.Frame(inner, bg=colors["card"]); info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=profile.get("name", "Profile"), font=(FONT, 14, "bold"), bg=colors["card"], fg=colors["fg"]).pack(anchor="w")
        tk.Label(info, text=profile.get("description") or "No description", font=(FONT, 9), bg=colors["card"], fg=colors["muted"]).pack(anchor="w", pady=2)
        btn(inner, "CHANGE PFP", lambda i=index: pick_pfp(i)).pack(side="right")


def render_mods():
    clear_content(); colors = theme()
    label(content, "Mods", 26, True).pack(anchor="w")
    label(content, "Import and disable installed Minecraft .jar mods.", 11, False, colors["muted"]).pack(anchor="w", pady=(3, 18))
    if not ownership_verified():
        c=card(content); c.pack(fill="x", pady=5)
        label(c,"Mods are locked",16,True,bg=colors["card"]).pack(anchor="w",padx=22,pady=(20,5))
        label(c,"Original Minecraft must be detected before mods can be managed.",10,False,colors["muted"],colors["card"]).pack(anchor="w",padx=22,pady=(0,20)); return
    btn(content,"+ IMPORT MODS",import_mod,True).pack(anchor="e",pady=(0,12))
    files=mod_files()
    if not files: label(content,"No .jar mods found in the Minecraft mods folder.",10,False,colors["muted"]).pack(anchor="w")
    for name in files:
        c=card(content); c.pack(fill="x",pady=4)
        tk.Label(c,text=name,font=(FONT,10,"bold"),bg=colors["card"],fg=colors["fg"]).pack(side="left",padx=18,pady=14)
        btn(c,"DISABLE",lambda n=name:disable_mod(n)).pack(side="right",padx=12,pady=7)


def render_versions():
    clear_content(); colors=theme()
    label(content,"Versions",26,True).pack(anchor="w")
    label(content,"Installed Minecraft versions found in the selected data folder.",11,False,colors["muted"]).pack(anchor="w",pady=(3,18))
    if not ownership_verified():
        c=card(content); c.pack(fill="x",pady=5); label(c,"Versions are locked",16,True,bg=colors["card"]).pack(anchor="w",padx=22,pady=(20,5)); label(c,"Original Minecraft must be detected before versions can be managed.",10,False,colors["muted"],colors["card"]).pack(anchor="w",padx=22,pady=(0,20)); return
    versions=installed_versions()
    if not versions: label(content,"No installed versions found.",10,False,colors["muted"]).pack(anchor="w")
    for name in versions:
        c=card(content); c.pack(fill="x",pady=4); tk.Label(c,text=name,font=(FONT,11,"bold"),bg=colors["card"],fg=colors["fg"]).pack(anchor="w",padx=18,pady=14)


def render_backups():
    clear_content(); colors=theme()
    label(content,"Backups",26,True).pack(anchor="w")
    label(content,"Create safe ZIP backups of important Minecraft folders.",11,False,colors["muted"]).pack(anchor="w",pady=(3,18))
    if not ownership_verified():
        c=card(content); c.pack(fill="x",pady=5); label(c,"Backups are locked",16,True,bg=colors["card"]).pack(anchor="w",padx=22,pady=(20,5)); label(c,"Original Minecraft must be detected before backups can be created.",10,False,colors["muted"],colors["card"]).pack(anchor="w",padx=22,pady=(0,20)); return
    btn(content,"CREATE BACKUP",create_backup,True).pack(anchor="e",pady=(0,12))
    folder=os.path.join(mc_dir(),"villager_launcher_backups")
    if os.path.isdir(folder):
        for name in sorted(os.listdir(folder),reverse=True):
            if name.lower().endswith(".zip"): label(content,name,10,True).pack(anchor="w",pady=4)


def render_repair():
    clear_content(); colors=theme()
    label(content,"Repair",26,True).pack(anchor="w")
    label(content,"Diagnostics that do not modify Minecraft files automatically.",11,False,colors["muted"]).pack(anchor="w",pady=(3,18))
    c=card(content); c.pack(fill="x",pady=5)
    detected=ownership_verified()
    label(c,"Minecraft data folder",13,True,bg=colors["card"]).pack(anchor="w",padx=22,pady=(20,4))
    label(c,mc_dir() or "Not available",10,False,colors["muted"],colors["card"]).pack(anchor="w",padx=22,pady=(0,5))
    label(c,"Official launcher evidence: " + ("Detected" if detected else "Not detected"),10,False,colors["fg"],colors["card"]).pack(anchor="w",padx=22,pady=(0,20))


def render_settings():
    clear_content(); colors=theme()
    label(content,"Settings",26,True).pack(anchor="w")
    label(content,"Configure Villager Launcher without changing Minecraft files automatically.",11,False,colors["muted"]).pack(anchor="w",pady=(3,18))
    c=card(content); c.pack(fill="x",pady=5)
    label(c,"General",16,True,bg=colors["card"]).pack(anchor="w",padx=22,pady=(20,12))
    row=tk.Frame(c,bg=colors["card"]); row.pack(fill="x",padx=22,pady=5)
    label(row,"Theme",10,True,bg=colors["card"]).pack(side="left")
    variable=tk.StringVar(value=current_theme)
    menu=tk.OptionMenu(row,variable,*list(THEMES.keys()) + (["Custom"] if custom_theme else []),command=set_theme)
    menu.config(font=(FONT,9),bg=colors["button"],fg=colors["fg"],relief="flat",highlightthickness=0); menu.pack(side="right")
    btn(c,"CUSTOM ACCENT",custom_theme_editor).pack(anchor="e",padx=22,pady=8)
    row=tk.Frame(c,bg=colors["card"]); row.pack(fill="x",padx=22,pady=8)
    label(row,"Minecraft folder",10,True,bg=colors["card"]).pack(side="left")
    label(row,settings.get("minecraft_path") or "Default .minecraft",9,False,colors["muted"],colors["card"]).pack(side="left",padx=15)
    btn(row,"CHOOSE",choose_mc).pack(side="right")
    row=tk.Frame(c,bg=colors["card"]); row.pack(fill="x",padx=22,pady=8)
    label(row,"Java path",10,True,bg=colors["card"]).pack(side="left")
    label(row,settings.get("java_path") or "Not set",9,False,colors["muted"],colors["card"]).pack(side="left",padx=15)
    btn(row,"CHOOSE",choose_java).pack(side="right")
    tk.Checkbutton(c,text="Ask before installing launcher updates",variable=tk.BooleanVar(value=settings.get("confirm_updates",True)),bg=colors["card"],fg=colors["fg"],selectcolor=colors["button"],activebackground=colors["card"],activeforeground=colors["fg"],command=lambda: save_checkbox("confirm_updates")).pack(anchor="w",padx=18,pady=10)
    tk.Checkbutton(c,text="Remember launcher window size",variable=tk.BooleanVar(value=settings.get("remember_window",True)),bg=colors["card"],fg=colors["fg"],selectcolor=colors["button"],activebackground=colors["card"],activeforeground=colors["fg"],command=lambda: save_checkbox("remember_window")).pack(anchor="w",padx=18,pady=2)
    btn(c,"RESET ALL SETTINGS",reset_settings).pack(anchor="e",padx=22,pady=18)
    u=card(content); u.pack(fill="x",pady=(15,5))
    label(u,"Updates",16,True,bg=colors["card"]).pack(anchor="w",padx=22,pady=(18,8))
    label(u,"Updates are manual. Villager Launcher never installs an update automatically.",10,False,colors["muted"],colors["card"]).pack(anchor="w",padx=22,pady=(0,10))
    btn(u,"CHECK FOR UPDATES",check_updates,True).pack(anchor="e",padx=22,pady=(0,18))


def save_checkbox(key):
    # Find the active checkbutton variable by reading its text from the UI is fragile, so settings are toggled by the current value.
    # This helper is intentionally simple: the checkbuttons are rebuilt with their current setting after each click.
    settings[key] = not bool(settings.get(key, True))
    save_settings()
    render_settings()


def render_current(page):
    pages={"Home":render_home,"Profiles":render_profiles,"Mods":render_mods,"Versions":render_versions,"Backups":render_backups,"Repair":render_repair,"Settings":render_settings}
    pages.get(page,render_home)()


def build_ui():
    global content, status
    for widget in root.winfo_children():
        widget.destroy()
    colors=theme()
    root.configure(bg=colors["bg"])
    root.title(f"Villager Launcher {CURRENT_VERSION}")
    root.geometry(f"{settings.get('window_width',1120)}x{settings.get('window_height',720)}")
    root.minsize(900,600)
    shell=tk.Frame(root,bg=colors["bg"]); shell.pack(fill="both",expand=True)
    sidebar=tk.Frame(shell,bg=colors["panel"],width=225); sidebar.pack(side="left",fill="y"); sidebar.pack_propagate(False)
    tk.Label(sidebar,text="VILLAGER",font=(FONT,18,"bold"),bg=colors["panel"],fg=colors["fg"]).pack(anchor="w",padx=24,pady=(28,0))
    tk.Label(sidebar,text="LAUNCHER",font=(FONT,10,"bold"),bg=colors["panel"],fg=colors["accent"]).pack(anchor="w",padx=24,pady=(0,24))
    pages=["Home","Profiles","Mods","Versions","Backups","Repair","Settings"]
    for page_name in pages:
        tk.Button(sidebar,text=page_name,command=lambda p=page_name: render_current(p),font=(FONT,10,"bold" if page_name==settings.get("start_page","Home") else "normal"),relief="flat",bd=0,bg=colors["panel"],fg=colors["fg"],activebackground=colors["button"],activeforeground=colors["fg"],anchor="w",padx=24,pady=11,cursor="hand2").pack(fill="x")
    tk.Label(sidebar,text=f"Version {CURRENT_VERSION}",font=(FONT,8),bg=colors["panel"],fg=colors["muted"]).pack(side="bottom",anchor="w",padx=24,pady=20)
    main=tk.Frame(shell,bg=colors["bg"]); main.pack(side="left",fill="both",expand=True)
    top=tk.Frame(main,bg=colors["bg"]); top.pack(fill="x",padx=30,pady=(22,0))
    tk.Label(top,text="Villager Launcher",font=(FONT,10,"bold"),bg=colors["bg"],fg=colors["muted"]).pack(side="left")
    status=tk.Label(top,text="Ready",font=(FONT,9),bg=colors["bg"],fg=colors["muted"]); status.pack(side="right")
    if profiles:
        image=load_pfp(profiles[selected_profile],44)
        if image:
            pfp=tk.Label(top,image=image,bg=colors["bg"]); pfp.image=image; pfp.pack(side="right",padx=(0,12))
        else:
            tk.Label(top,text="PFP",font=(FONT,8,"bold"),width=5,height=2,bg=colors["button"],fg=colors["muted"]).pack(side="right",padx=(0,12))
    content=tk.Frame(main,bg=colors["panel"]); content.pack(fill="both",expand=True,padx=30,pady=18)
    page=settings.get("start_page","Home")
    render_current(page if page in pages else "Home")


def rebuild_ui():
    save_settings()
    build_ui()


def save_window():
    if root and settings.get("remember_window",True):
        try:
            settings["window_width"]=root.winfo_width()
            settings["window_height"]=root.winfo_height()
            save_settings()
        except tk.TclError:
            pass


load_settings()
load_profiles()

if len(sys.argv) >= 3 and sys.argv[1] == "--install-update":
    finish_update(sys.argv[2])
    raise SystemExit

root=tk.Tk()
build_ui()
root.protocol("WM_DELETE_WINDOW",lambda:(save_window(),root.destroy()))
root.mainloop()
