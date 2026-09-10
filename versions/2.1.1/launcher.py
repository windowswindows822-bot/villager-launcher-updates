import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser, simpledialog, ttk
import os, sys, json, tempfile, subprocess, time, re, io, threading, webbrowser
from urllib.request import Request, urlopen
from urllib.parse import quote
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
CURRENT_VERSION = "2.1.2"
BETA = True
BASE_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main"
VERSION_URL = BASE_URL + "/version.json"
LAUNCHER_URL = BASE_URL + "/launcher.py"
UPDATE_VERSION_URL = VERSION_URL
UPDATE_LAUNCHER_URL = LAUNCHER_URL
MODRINTH = "https://api.modrinth.com/v2"
APP = os.path.join(os.environ.get("APPDATA", tempfile.gettempdir()), "VillagerLauncher")
SETTINGS_FILE = os.path.join(APP, "settings.json")
PROFILES_FILE = os.path.join(APP, "profiles.json")
PREVIOUS_LAUNCHER_FILE = os.path.join(APP, "previous_launcher.py")
PREVIOUS_VERSION_FILE = os.path.join(APP, "previous_version.json")
FONT = "Segoe UI"
LOADERS = ["Vanilla", "Forge", "Fabric", "Quilt", "NeoForge"]
LOADER_ICON = {"Vanilla": "◆", "Forge": "▲", "Fabric": "◇", "Quilt": "●", "NeoForge": "■"}
PAGE_TITLES = {"Home": "Home", "Profiles": "Profiles", "Workshop": "Mod Workshop", "Installations": "Installations", "Repair": "Repair Center", "Ideas": "500+ Features", "Settings": "Settings", "Feedback": "Feedback"}
WORKSHOP_PAGE_SIZE = 18
FEATURE_CATEGORIES = [
    ("Home & Dashboard", [
        "Quick launch card", "Recent profile list", "Recent version list", "Pinned profiles", "Pinned versions",
        "Favorite tools", "Launcher status summary", "Minecraft folder status", "Java status summary", "Update badge",
        "Workshop shortcut", "Repair shortcut", "Settings shortcut", "Feedback shortcut", "Ideas shortcut",
        "Session timer", "Last launch timestamp", "Last update timestamp", "Download summary", "Storage summary",
        "Welcome message", "Daily villager tip", "Random Minecraft fact", "Quick search box", "Command palette shortcut",
    ]),
    ("Profiles", [
        "Profile duplication", "Profile import", "Profile export", "Profile backup", "Profile restore",
        "Profile notes", "Profile tags", "Profile favorites", "Profile color", "Profile icon",
        "Profile sorting", "Profile search", "Profile archive", "Profile reset", "Profile statistics",
        "Profile last-played time", "Profile play count", "Profile folder view", "Profile clone name", "Profile validation",
        "Profile loader presets", "Profile JVM presets", "Profile memory presets", "Profile resolution presets", "Profile modpack association",
    ]),
    ("Minecraft Launching", [
        "Real Java launch pipeline", "Automatic Java detection", "Java version check", "Java compatibility warning", "Launch argument editor",
        "JVM argument presets", "Game argument editor", "Window size presets", "Fullscreen toggle", "Resolution memory",
        "Launch logging", "Launch history", "Last launched version", "Launch failure diagnostics", "Crash exit detection",
        "Offline validation", "Account-folder detection", "Version JSON validation", "JAR validation", "Libraries validation",
        "Assets validation", "Natives validation", "Game directory override", "Per-profile Java path", "Per-profile memory limit",
    ]),
    ("Version Management", [
        "Version scanner", "Version search", "Version sorting", "Version filtering", "Version details",
        "Version JSON viewer", "Version JAR metadata", "Version size display", "Version last-used marker", "Version cleanup preview",
        "Version backup", "Version restore", "Version duplicate detection", "Missing-file detection", "Broken-version badge",
        "Snapshot grouping", "Release grouping", "Old-version grouping", "Version favorites", "Version notes",
        "Version compatibility view", "Loader compatibility view", "Version directory opener", "Version refresh button", "Version scan timestamp",
    ]),
    ("Workshop & Mods", [
        "Modrinth search", "Shader search", "Resource-pack search", "Data-pack search", "Project type filter",
        "Loader filter", "Minecraft version filter", "Downloads sorting", "Updated sorting", "Relevance sorting",
        "Load more", "Project icons", "Installed badges", "Compatible release selection", "Primary-file selection",
        "Mod update checker", "Mod version history", "Mod dependency viewer", "Mod conflict checker", "Duplicate mod detector",
        "Mod enable/disable", "Mod profile assignment", "Mod favorites", "Mod search history", "Mod install log",
    ]),
    ("Downloads", [
        "Download progress", "Download speed", "Download ETA", "Download queue", "Download pause",
        "Download resume", "Download retry", "Download cancel", "Download history", "Download destination preview",
        "Download checksum", "Download size check", "Download timeout control", "Download connection test", "Download error log",
        "Parallel downloads", "Sequential downloads", "Bandwidth limit", "Automatic retry count", "Temporary-file cleanup",
        "Failed-download recovery", "Download notification", "Download completion sound", "Download statistics", "Download cache",
    ]),
    ("Repair Center", [
        "Launcher folder check", "Settings check", "Profiles check", "Minecraft directory check", "Official launcher evidence check",
        "Installed versions check", "Java check", "Updater check", "Workshop check", "Theme check",
        "UI check", "Bot knowledge check", "Version JSON check", "Version JAR check", "Libraries check",
        "Assets check", "Mods folder check", "Resource-pack folder check", "Shader folder check", "Data-pack folder check",
        "Backup check", "Permissions check", "Disk-space check", "Path-length warning", "Repair report export",
    ]),
    ("Updater", [
        "GitHub version check", "Automatic update prompt", "Automatic update download", "Update progress", "Update verification",
        "Update staging", "Update retry", "Update error report", "Update notes viewer",
        "Update history", "Skipped-version memory", "Release-channel selector", "Beta-channel selector", "Stable-channel selector",
        "Update-on-startup", "Update-after-launch", "Update reminder", "Update package size", "Update source display",
        "Update timeout", "Update cache cleanup", "Update helper cleanup", "Old-version backup", "Post-update validation",
    ]),
    ("UI & Navigation", [
        "Global search", "Command palette", "Keyboard shortcuts", "Shortcut editor", "Breadcrumb navigation",
        "Back navigation", "Home button", "Sidebar collapse", "Compact sidebar", "Large text mode",
        "High contrast mode", "Reduced motion mode", "Tooltips", "Status bar", "Notification center",
        "Toast messages", "Modal history", "Resizable cards", "Dense layout", "Comfortable layout",
        "Remember scroll position", "Remember window size", "Remember selected page", "Page refresh button", "UI debug overlay",
    ]),
    ("Themes & Personalization", [
        "Villager Green theme", "Midnight theme", "Sky theme", "Nether theme", "Ocean theme",
        "Diamond theme", "Gold theme", "Amethyst theme", "Forest theme", "Cherry Grove theme",
        "Deep Dark theme", "Custom accent", "Custom background", "Custom panel color", "Custom card color",
        "Custom text color", "Custom muted color", "Custom danger color", "Custom border color", "Theme export",
        "Theme import", "Theme reset", "Theme preview", "Random theme button", "Theme favorites",
    ]),
    ("Villager Bot", [
        "Offline Q&A", "Question search", "Keyword matching", "Knowledge count", "Bot test suite",
        "Bot knowledge export", "Bot knowledge import", "Bot response history", "Clear bot history", "Bot welcome message",
        "Minecraft facts", "Mod facts", "Windows facts", "Python facts", "Java facts",
        "Roblox facts", "PC hardware facts", "Launcher facts", "Repair tips", "Troubleshooting tips",
        "Random fact button", "Hmm button", "Bot diagnostics", "Bot response counter", "Bot knowledge categories",
    ]),
    ("Statistics", [
        "Profile count", "Installed-version count", "Workshop install count", "Launch count", "Session count",
        "Update count", "Repair test count", "Feedback count", "Search count", "Download count",
        "Favorite count", "Enabled-feature count", "Theme usage", "Most-used profile", "Most-used version",
        "Last activity", "First launch date", "Total session time", "Average session time", "Workshop projects viewed",
        "Workshop searches", "Update checks", "Repair passes", "Bot questions", "Settings changes",
    ]),
    ("Backup & Restore", [
        "Settings backup", "Profiles backup", "Themes backup", "Feedback backup", "Launcher-state backup",
        "Backup timestamp", "Backup list", "Backup validation", "Backup size", "Backup destination chooser",
        "Restore settings", "Restore profiles", "Restore themes", "Restore feedback", "Restore launcher state",
        "Export all configuration", "Import all configuration", "Backup reminder", "Automatic backup", "Backup retention",
        "Backup cleanup", "Backup notes", "Backup verification", "Backup error log", "Backup status badge",
    ]),
    ("File Management", [
        "Open Minecraft folder", "Open versions folder", "Open mods folder", "Open resource-packs folder", "Open shaderpacks folder",
        "Open datapacks folder", "Open launcher data folder", "Open feedback folder", "Open backup folder", "Path copy button",
        "Path validation", "Path normalization", "Folder existence badges", "File count display", "Folder size display",
        "Hidden-file awareness", "Safe file preview", "JSON viewer", "Text log viewer", "File timestamp viewer",
        "File extension filter", "File search", "Recent files", "Favorite folders", "Folder refresh",
    ]),
    ("Network & Diagnostics", [
        "Internet connectivity check", "GitHub connectivity check", "Modrinth connectivity check", "DNS failure message", "Timeout diagnostics",
        "Proxy-awareness warning", "HTTP status display", "Download retry diagnostics", "Connection latency display", "Network test history",
        "Offline mode indicator", "Network error copy button", "Request timing", "API response summary", "API endpoint viewer",
        "User-agent display", "Cache status", "Connection reset retry", "Network debug log", "Safe error redaction",
        "Workshop API health", "Updater API health", "Connection notification", "Offline fallback", "Network diagnostics export",
    ]),
    ("Feedback & Support", [
        "Star rating", "Local feedback saving", "Feedback history", "Feedback export", "Feedback folder opener",
        "Bug report template", "Feature request template", "Crash report template", "UI issue template", "Workshop issue template",
        "Updater issue template", "Repair issue template", "Copy diagnostics", "Support bundle", "Version information",
        "System information summary", "Python information", "Java information", "Minecraft path summary", "Launcher path summary",
        "Safe privacy filter", "Feedback timestamp", "Feedback search", "Feedback deletion", "Feedback statistics",
    ]),
    ("Developer & Debug", [
        "Debug mode", "Verbose logging", "UI widget inspector", "State inspector", "Profile JSON inspector",
        "Settings JSON inspector", "Feature registry inspector", "Network log", "Update log", "Workshop log",
        "Repair log", "Bot log", "Exception capture", "Traceback viewer", "Copy traceback",
        "Environment viewer", "Python path viewer", "Executable path viewer", "Working-directory viewer", "Thread monitor",
        "Render timing", "Page render counter", "API timing counter", "Memory-friendly mode", "Developer status badge",
    ]),
    ("Fun & Villager", [
        "Random villager quote", "Villager mood", "Villager of the day", "Emerald counter", "Emerald-style progress",
        "Hmm sound toggle", "Hmm button animation", "Villager loading text", "Villager success message", "Villager error message",
        "Creeper warning badge", "Diamond achievement", "Nether achievement", "End achievement", "Overworld achievement",
        "Launcher level", "Feature unlock counter", "Secret button", "Easter egg counter", "Random Minecraft tip",
        "Villager naming", "Villager commander mode", "Fun status messages", "Celebration popup", "Achievement panel",
    ]),
    ("Safety & Reliability", [
        "No-delete repair policy", "Confirm destructive actions", "Safe update staging", "Atomic update replacement", "Update interruption notice",
        "Temporary-file cleanup", "Malformed JSON protection", "Network exception protection", "Missing-folder protection", "Missing-file protection",
        "Invalid-version protection", "Invalid-loader protection", "Invalid-theme protection", "Invalid-profile protection", "UI exception protection",
        "Timeout protection", "Empty-download protection", "Path safety check", "File-write error handling", "Permission error handling",
        "Graceful shutdown", "State-save on close", "State-save before update", "Update interruption recovery", "Diagnostic-only repair",
    ]),
    ("Advanced Launcher", [
        "Per-profile game directory", "Per-profile loader", "Per-profile Java", "Per-profile memory", "Per-profile arguments",
        "Per-profile resolution", "Per-profile fullscreen", "Per-profile mod set", "Per-profile notes", "Per-profile backups",
        "Launch presets", "Import preset", "Export preset", "Preset duplication", "Preset validation",
        "Advanced settings search", "Feature dependencies", "Feature compatibility", "Feature categories", "Feature enable all",
        "Feature disable all", "Feature reset", "Feature favorites", "Feature search", "Feature statistics",
    ]),
]
FEATURES = []
for category, names in FEATURE_CATEGORIES:
    for name in names:
        FEATURES.append({"name": name, "category": category, "description": f"{name} is part of the Villager Launcher feature registry."})
_extra_base = ["Quick action", "Status badge", "History view", "Search helper", "Diagnostic helper", "Settings toggle", "Export helper", "Import helper", "Preview panel", "Reset control"]
_i = 1
while len(FEATURES) < 500:
    category = "Expansion Pack"
    name = f"Villager Expansion Feature {_i:03d} — {_extra_base[(_i - 1) % len(_extra_base)]}"
    FEATURES.append({"name": name, "category": category, "description": "Reserved expansion feature in the 500-feature Villager Launcher registry."})
    _i += 1
FEATURES = FEATURES[:500]
FEATURE_STATE = {}
hmm_clicks = 0
ICON_SIZE = 44
workshop_icon_cache = {}
THEMES = {
    "Villager Green": dict(bg="#07110c", panel="#101c14", card="#18261c", fg="#f4faf4", muted="#9fb3a4", accent="#5ec75e", button="#24382a", input="#0b1610", menu="#24382a", hover="#78dd78", selected="#5ec75e", danger="#d45c5c", border="#2a4332"),
    "Midnight": dict(bg="#080d17", panel="#111a29", card="#1a263b", fg="#ffffff", muted="#a9b5c9", accent="#7188ff", button="#29385e", input="#080d17", menu="#29385e", hover="#8c9cff", selected="#7188ff", danger="#d65b68", border="#31456a"),
    "Sky": dict(bg="#dff1fa", panel="#f5fbff", card="#ffffff", fg="#173042", muted="#5c7180", accent="#3a91c9", button="#c7e0ed", input="#ffffff", menu="#c7e0ed", hover="#57a9d8", selected="#3a91c9", danger="#c95353", border="#b7d3e2"),
    "Nether": dict(bg="#180c0c", panel="#2a1212", card="#3a1919", fg="#ffffff", muted="#d0a8a8", accent="#e05a5a", button="#542626", input="#180c0c", menu="#542626", hover="#f07070", selected="#e05a5a", danger="#ff7070", border="#5c2d2d"),
    "Ocean": dict(bg="#071820", panel="#0d2833", card="#123845", fg="#ffffff", muted="#9fc5d0", accent="#38a7c7", button="#1b4655", input="#071820", menu="#1b4655", hover="#62c8e3", selected="#38a7c7", danger="#e05a5a", border="#1f5364"),
    "Diamond": dict(bg="#07171a", panel="#0d2930", card="#123c46", fg="#eaffff", muted="#9ed2d8", accent="#59d8e4", button="#1d5962", input="#07171a", menu="#1d5962", hover="#86edf5", selected="#59d8e4", danger="#e05a5a", border="#226874"),
    "Gold": dict(bg="#171207", panel="#2a210d", card="#3c3012", fg="#fff8df", muted="#d8c58b", accent="#e8c84a", button="#5a4818", input="#171207", menu="#5a4818", hover="#f4dc72", selected="#e8c84a", danger="#d65b53", border="#6a5520"),
    "Amethyst": dict(bg="#120a18", panel="#24122f", card="#321b42", fg="#fff5ff", muted="#c7afd2", accent="#b66cde", button="#4b2a5c", input="#120a18", menu="#4b2a5c", hover="#cf8cef", selected="#b66cde", danger="#e05a6a", border="#563368"),
    "Forest": dict(bg="#08150d", panel="#10261a", card="#173622", fg="#f3fff6", muted="#a6c5ae", accent="#55b96a", button="#285336", input="#08150d", menu="#285336", hover="#72d486", selected="#55b96a", danger="#d65b53", border="#2f6340"),
    "Cherry Grove": dict(bg="#190b12", panel="#301321", card="#421b2c", fg="#fff5f8", muted="#d7aebe", accent="#f083b0", button="#613047", input="#190b12", menu="#613047", hover="#ff9bc4", selected="#f083b0", danger="#e45b66", border="#734058"),
    "Deep Dark": dict(bg="#07080e", panel="#10111d", card="#171a2b", fg="#eef0ff", muted="#a2a6bf", accent="#27d0c0", button="#173d3b", input="#07080e", menu="#173d3b", hover="#52e5d7", selected="#27d0c0", danger="#db5d6b", border="#1e4a48"),
}
DEFAULTS = {"theme": "Villager Green", "minecraft_path": "", "java_path": "", "window_width": 1260, "window_height": 800}
settings = dict(DEFAULTS)
custom_themes = {}
profiles = []
selected = 0
page = "Home"
root = None
body = None
workshop_results = []
workshop_offset = 0
workshop_query = ""
workshop_more_available = False
workshop_loading = False
workshop_error = ""
workshop_filters = {"content_type": "Mod", "version": "", "sort": "Relevance", "loader": "Any"}
last_tests = []
workshop_checked = False
ideas_query = ""
ideas_category = "All"
def read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default
def load_state():
    global settings, custom_themes, profiles, selected
    d = read_json(SETTINGS_FILE, {})
    if isinstance(d, dict):
        for k in DEFAULTS:
            if k in d:
                settings[k] = d[k]
        if isinstance(d.get("custom_themes"), dict):
            custom_themes = d["custom_themes"]
    profiles = read_json(PROFILES_FILE, [])
    if not isinstance(profiles, list) or not profiles:
        profiles = [{"name": "Default", "version": "", "loader": "Vanilla"}]
    for p in profiles:
        p.setdefault("loader", "Vanilla")
        if p["loader"] not in LOADERS:
            p["loader"] = "Vanilla"
    selected = min(selected, len(profiles) - 1)
def save_state():
    os.makedirs(APP, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({**settings, "custom_themes": custom_themes}, f, indent=2)
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)
def T():
    theme = custom_themes.get(settings.get("theme")) or THEMES.get(settings.get("theme"), THEMES["Villager Green"])
    if "border" not in theme:
        theme = dict(theme)
        theme["border"] = theme.get("button", "#24382a")
    return theme
def mc_dir():
    p = settings.get("minecraft_path", "")
    if p and os.path.isdir(p):
        return p
    a = os.environ.get("APPDATA", "")
    return os.path.join(a, ".minecraft") if a else ""
def owned():
    d = mc_dir()
    return bool(d and os.path.isdir(d) and (os.path.isfile(os.path.join(d, "launcher_accounts.json")) or os.path.isfile(os.path.join(d, "launcher_profiles.json"))))
def gate(feature):
    if owned():
        return True
    messagebox.showwarning("Minecraft Required", f"{feature} requires an original Minecraft installation. Sign in through the official Minecraft Launcher, then choose its Minecraft folder in Settings.")
    return False
def versions():
    d = os.path.join(mc_dir(), "versions")
    try:
        return sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x))], reverse=True)
    except OSError:
        return []
def selected_version():
    v = profiles[selected].get("version", "") if profiles else ""
    return v or (versions()[0] if versions() else "")
def selected_loader():
    return profiles[selected].get("loader", "Vanilla") if profiles else "Vanilla"
def net_json(url, timeout=15):
    r = Request(url + ("&" if "?" in url else "?") + "t=" + str(time.time_ns()), headers={"User-Agent": f"Villager-Launcher/{CURRENT_VERSION}"})
    with urlopen(r, timeout=timeout) as x:
        return json.loads(x.read().decode("utf-8"))
def project_folder(project_type):
    return {"mod": "mods", "shader": "shaderpacks", "resourcepack": "resourcepacks", "datapack": "datapacks"}.get(project_type, "mods")
def effective_kind(project):
    pt = project.get("project_type", "mod")
    cats = project.get("categories") or []
    if pt == "mod" and "datapack" in cats:
        return "datapack"
    return pt
def installed_filenames(project_type):
    out = os.path.join(mc_dir(), project_folder(project_type))
    try:
        return {f.lower() for f in os.listdir(out)}
    except OSError:
        return set()
def is_installed(project):
    typ = effective_kind(project)
    slug = (project.get("slug") or "").lower()
    if not slug:
        return False
    names = installed_filenames(typ)
    return any(slug in n for n in names)
def _fetch_icon_bytes_async(url, callback):
    def worker():
        raw = None
        try:
            req = Request(url, headers={"User-Agent": f"Villager-Launcher/{CURRENT_VERSION}"})
            with urlopen(req, timeout=6) as r:
                raw = r.read()
        except Exception:
            raw = None
        if root and root.winfo_exists():
            root.after(0, lambda: callback(raw))
    threading.Thread(target=worker, daemon=True).start()
def _bytes_to_photo(raw, size):
    if HAS_PIL:
        im = Image.open(io.BytesIO(raw)).convert("RGBA").resize((size, size))
        return ImageTk.PhotoImage(im)
    photo = tk.PhotoImage(data=raw)
    w = photo.width()
    if w > size:
        factor = max(1, w // size)
        photo = photo.subsample(factor, factor)
    return photo
def icon_widget(parent, project, size=ICON_SIZE):
    t = T()
    box = tk.Frame(parent, width=size, height=size, bg=t["button"])
    box.pack_propagate(False)
    initial = (project.get("title") or project.get("slug") or "?").strip()[:1].upper() or "?"
    placeholder = tk.Label(box, text=initial, bg=t["button"], fg=t["accent"], font=(FONT, 15, "bold"))
    placeholder.pack(fill="both", expand=True)
    url = project.get("icon_url")
    if not url:
        return box
    cached = workshop_icon_cache.get(url)
    if cached == "FAILED":
        return box
    if cached is not None:
        placeholder.destroy()
        lbl = tk.Label(box, image=cached, bg=t["card"])
        lbl.image = cached
        lbl.pack(fill="both", expand=True)
        return box
    def done(raw, box=box, placeholder=placeholder, url=url):
        try:
            if not box.winfo_exists():
                return
            if raw is None:
                workshop_icon_cache[url] = "FAILED"
                return
            photo = _bytes_to_photo(raw, size)
            workshop_icon_cache[url] = photo
            placeholder.destroy()
            lbl = tk.Label(box, image=photo, bg=t["card"])
            lbl.image = photo
            lbl.pack(fill="both", expand=True)
        except Exception:
            workshop_icon_cache[url] = "FAILED"
    _fetch_icon_bytes_async(url, done)
    return box
def apply_styles():
    t = T()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(".", font=(FONT, 10), background=t["bg"], foreground=t["fg"])
    style.configure("TFrame", background=t["bg"])
    style.configure("Card.TFrame", background=t["card"])
    style.configure("TLabel", background=t["bg"], foreground=t["fg"], font=(FONT, 10))
    style.configure("Muted.TLabel", background=t["bg"], foreground=t["muted"], font=(FONT, 10))
    style.configure("Title.TLabel", background=t["bg"], foreground=t["fg"], font=(FONT, 24, "bold"))
    style.configure("TEntry", fieldbackground=t["input"], foreground=t["fg"], insertcolor=t["fg"])
    style.configure("TCombobox", fieldbackground=t["input"], background=t["menu"], foreground=t["fg"])
    style.map("TCombobox", fieldbackground=[("readonly", t["input"])], foreground=[("readonly", t["fg"])])
    style.configure("Vertical.TScrollbar", background=t["button"], troughcolor=t["panel"], bordercolor=t["panel"], arrowcolor=t["fg"])
class ScrollArea(tk.Frame):
    def __init__(self, parent, bg):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.bar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._width)
        self.canvas.configure(yscrollcommand=self.bar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.bar.pack(side="right", fill="y")
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._wheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
    def _width(self, event):
        self.canvas.itemconfigure(self.win, width=event.width)
    def _wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")
def hover_btn(parent, text, command, primary=False, padx=18, pady=10, enabled=True):
    t = T()
    bg = (t["accent"] if primary else t["button"]) if enabled else t["panel"]
    fg = t["fg"] if enabled else t["muted"]
    if primary and enabled:
        fg = "#0b120d" if _is_light_accent(t["accent"]) else "#ffffff"
    b = tk.Label(parent, text=text, bg=bg, fg=fg, font=(FONT, 10, "bold"), padx=padx, pady=pady, cursor="hand2" if enabled else "arrow")
    if enabled:
        b.bind("<Enter>", lambda e: b.configure(bg=t["hover"]))
        b.bind("<Leave>", lambda e: b.configure(bg=bg))
        b.bind("<Button-1>", lambda e: command())
    return b
def _is_light_accent(hex_color):
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return False
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) > 160
def chip(parent, text, ok=True):
    t = T()
    bg = "#1f3d28" if ok else "#3d1f24"
    fg = t["accent"] if ok else t["danger"]
    return tk.Label(parent, text=text, bg=bg, fg=fg, font=(FONT, 8, "bold"), padx=10, pady=4)
def page_header(parent, title, subtitle, right_widget_fn=None):
    t = T()
    wrap = tk.Frame(parent, bg=t["bg"])
    wrap.pack(fill="x", padx=28, pady=(22, 8))
    left = tk.Frame(wrap, bg=t["bg"])
    left.pack(side="left", fill="x", expand=True)
    tk.Label(left, text=title, bg=t["bg"], fg=t["fg"], font=(FONT, 26, "bold")).pack(anchor="w")
    tk.Label(left, text=subtitle, bg=t["bg"], fg=t["muted"], font=(FONT, 10)).pack(anchor="w", pady=(4, 0))
    if right_widget_fn:
        right = tk.Frame(wrap, bg=t["bg"])
        right.pack(side="right")
        right_widget_fn(right)
    return wrap
def card(parent, padx=28, pady=8, accent=True):
    t = T()
    shell = tk.Frame(parent, bg=t["border"])
    shell.pack(fill="x", padx=padx, pady=pady)
    inner = tk.Frame(shell, bg=t["card"])
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    row = tk.Frame(inner, bg=t["card"])
    row.pack(fill="both", expand=True)
    if accent:
        tk.Frame(row, bg=t["accent"], width=3).pack(side="left", fill="y")
    content = tk.Frame(row, bg=t["card"])
    content.pack(side="left", fill="both", expand=True, padx=20, pady=16)
    return content
def section_label(parent, text):
    t = T()
    tk.Label(parent, text=text.upper(), bg=t["bg"], fg=t["muted"], font=(FONT, 9, "bold")).pack(anchor="w", padx=28, pady=(14, 0))
def go(p):
    global page
    if p == page:
        return
    page = p
    render()
def shell():
    global body
    t = T()
    root.configure(bg=t["bg"])
    for w in root.winfo_children():
        w.destroy()
    apply_styles()
    outer = tk.Frame(root, bg=t["bg"])
    outer.pack(fill="both", expand=True)
    side = tk.Frame(outer, bg=t["panel"], width=232)
    side.pack(side="left", fill="y")
    side.pack_propagate(False)
    brand = tk.Frame(side, bg=t["panel"])
    brand.pack(fill="x", padx=18, pady=(22, 18))
    mark = tk.Frame(brand, bg=t["accent"], width=12, height=12)
    mark.pack(side="left", padx=(0, 10))
    mark.pack_propagate(False)
    names = tk.Frame(brand, bg=t["panel"])
    names.pack(side="left")
    tk.Label(names, text="VILLAGER", bg=t["panel"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
    tk.Label(names, text="LAUNCHER", bg=t["panel"], fg=t["muted"], font=(FONT, 8)).pack(anchor="w")
    nav = [
        ("⌂", "Home", "Home"),
        ("☰", "Profiles", "Profiles"),
        ("⚒", "Workshop", "Workshop"),
        ("▣", "Installations", "Installations"),
        ("✚", "Repair", "Repair"),
        ("★", "Ideas", "Ideas"),
        ("⚙", "Settings", "Settings"),
        ("✎", "Feedback", "Feedback"),
    ]
    for icon, name, dest in nav:
        active = page == dest
        row = tk.Frame(side, bg=t["panel"])
        row.pack(fill="x", padx=12, pady=3)
        tk.Frame(row, bg=t["accent"] if active else t["panel"], width=4).pack(side="left", fill="y")
        label_bg = t["card"] if active else t["panel"]
        label_fg = t["accent"] if active else t["muted"]
        b = tk.Label(row, text=f"{icon}   {name}", bg=label_bg, fg=label_fg, font=(FONT, 10, "bold"),
                     anchor="w", padx=14, pady=10, cursor="arrow" if active else "hand2")
        b.pack(side="left", fill="x", expand=True)
        if not active:
            b.bind("<Button-1>", lambda e, p=dest: go(p))
            b.bind("<Enter>", lambda e, w=b: w.configure(bg=t["button"]))
            b.bind("<Leave>", lambda e, w=b, bg=label_bg: w.configure(bg=bg))
    foot = f"{CURRENT_VERSION}" + (" beta" if BETA else "")
    tk.Label(side, text=foot, bg=t["panel"], fg=t["muted"], font=(FONT, 8)).pack(side="bottom", pady=16)
    right = tk.Frame(outer, bg=t["bg"])
    right.pack(side="left", fill="both", expand=True)
    header = tk.Frame(right, bg=t["bg"], height=64)
    header.pack(fill="x")
    header.pack_propagate(False)
    left_head = tk.Frame(header, bg=t["bg"])
    left_head.pack(side="left", padx=28, pady=14)
    tk.Label(left_head, text="VILLAGER", bg=t["bg"], fg=t["muted"], font=(FONT, 9, "bold")).pack(side="left")
    tk.Label(left_head, text="fuPs launcher", bg=t["bg"], fg=t["muted"], font=(FONT, 5)).pack(side="left", padx=(8, 10), pady=(8, 0))
    tk.Label(left_head, text="  ›  ", bg=t["bg"], fg=t["muted"], font=(FONT, 9)).pack(side="left")
    tk.Label(left_head, text=PAGE_TITLES.get(page, page), bg=t["bg"], fg=t["fg"], font=(FONT, 13, "bold")).pack(side="left")
    status = "Minecraft found" if owned() else "Set Minecraft folder"
    hover_btn(header, "?", open_credits, True, padx=10, pady=6).pack(side="right", padx=(8, 18))
    chip(header, status, owned()).pack(side="right", padx=0)
    tk.Frame(right, bg=t["border"], height=1).pack(fill="x")
    body_wrap = tk.Frame(right, bg=t["bg"])
    body_wrap.pack(fill="both", expand=True)
    scroll = ScrollArea(body_wrap, t["bg"])
    scroll.pack(fill="both", expand=True, padx=(0, 4))
    body = scroll.inner
def open_credits():
    t = T()
    w = tk.Toplevel(root)
    w.title("Villager Launcher — Credits & Origins")
    w.geometry("720x620")
    w.minsize(620, 520)
    w.configure(bg=t["panel"])
    w.transient(root)
    tk.Label(w, text="Villager Launcher", bg=t["panel"], fg=t["fg"], font=(FONT, 24, "bold")).pack(pady=(24, 2))
    tk.Label(w, text="Credits • Origins • Project History", bg=t["panel"], fg=t["muted"], font=(FONT, 10)).pack(pady=(0, 16))
    content = tk.Frame(w, bg=t["panel"])
    content.pack(fill="both", expand=True, padx=28)
    sections = [
        ("Creator", "Villager Commander"),
        ("Project owner", "Villager Commander"),
        ("Project origin", "Villager Launcher — created and developed by Villager Commander."),
        ("FuPs / MrXAUYT", "Some launcher ideas and inspiration were influenced by MrXAUYT's FuPs launcher. FuPs is credited as an inspiration/reference, not as the creator or owner of Villager Launcher."),
        ("Inspiration", "Minecraft launcher concepts, Modrinth browsing, classic desktop launcher design, and the user's own ideas and experiments."),
        ("Major contributors", "Villager Commander is the creator/owner. Other contributions can be added here as they are confirmed."),
        ("Special thanks", "MrXAUYT / FuPs for inspiration and reference."),
        ("Current release", f"Villager Launcher {CURRENT_VERSION}"),
    ]
    for heading, text in sections:
        box = tk.Frame(content, bg=t["card"])
        box.pack(fill="x", pady=5)
        tk.Label(box, text=heading, bg=t["card"], fg=t["accent"], font=(FONT, 10, "bold")).pack(anchor="w", padx=16, pady=(10, 2))
        tk.Label(box, text=text, bg=t["card"], fg=t["fg"], font=(FONT, 9), wraplength=620, justify="left").pack(anchor="w", padx=16, pady=(0, 10))
    hover_btn(w, "Close", w.destroy, True, padx=18, pady=8).pack(pady=16)
def render():
    shell()
    {
        "Home": home,
        "Profiles": profiles_page,
        "Workshop": workshop_page,
        "Installations": installations_page,
        "Repair": repair_page,
        "Ideas": ideas_page,
        "Settings": settings_page,
        "Feedback": feedback_page,
    }.get(page, home)()
def home():
    t = T()
    page_header(body, "Welcome back", "Play, download mods, and install retexture packs from one place.")
    hero = card(body)
    tk.Label(hero, text="READY TO PLAY", bg=t["card"], fg=t["muted"], font=(FONT, 8, "bold")).pack(anchor="w")
    tk.Label(hero, text=profiles[selected].get("name", "Default"), bg=t["card"], fg=t["fg"], font=(FONT, 22, "bold")).pack(anchor="w", pady=(6, 2))
    loader = selected_loader()
    tk.Label(hero, text=f"{LOADER_ICON.get(loader, '')}  {selected_version() or 'None selected'}  •  {loader}", bg=t["card"], fg=t["muted"], font=(FONT, 10)).pack(anchor="w")
    actions = tk.Frame(hero, bg=t["card"])
    actions.pack(anchor="w", pady=(16, 0))
    hover_btn(actions, "Play", launch_game, True, padx=28, pady=12).pack(side="left")
    hover_btn(actions, "Villager Bot", open_villager_bot).pack(side="left", padx=8)
    hover_btn(actions, "Hmm", hmm_button).pack(side="left", padx=(0, 8))
    hover_btn(actions, "Test everything", test_everything).pack(side="left")
    stats = tk.Frame(body, bg=t["bg"])
    stats.pack(fill="x", padx=28, pady=(4, 8))
    for label, value in [
        ("Profiles", str(len(profiles))),
        ("Installed versions", str(len(versions()))),
        ("Theme", settings.get("theme", "Villager Green")),
        ("Status", "Linked" if owned() else "Not linked"),
    ]:
        cell = tk.Frame(stats, bg=t["border"])
        cell.pack(side="left", fill="both", expand=True, padx=(0, 10))
        inn = tk.Frame(cell, bg=t["card"])
        inn.pack(fill="both", expand=True, padx=1, pady=1)
        box = tk.Frame(inn, bg=t["card"])
        box.pack(fill="both", expand=True, padx=14, pady=12)
        tk.Label(box, text=value, bg=t["card"], fg=t["fg"], font=(FONT, 15, "bold")).pack(anchor="w")
        tk.Label(box, text=label, bg=t["card"], fg=t["muted"], font=(FONT, 8, "bold")).pack(anchor="w")
    tools = tk.Frame(body, bg=t["bg"])
    tools.pack(fill="x", padx=28, pady=8)
    for title, desc, dest in [
        ("Mod Workshop", "Search Modrinth for mods, shaders, and retexture packs.", "Workshop"),
        ("Installations", "Pick the Minecraft version this profile should use.", "Installations"),
        ("Repair Center", "Run safe checks without deleting Minecraft files.", "Repair"),
    ]:
        item = tk.Frame(tools, bg=t["border"])
        item.pack(side="left", fill="both", expand=True, padx=(0, 10))
        inner = tk.Frame(item, bg=t["card"])
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        box = tk.Frame(inner, bg=t["card"])
        box.pack(fill="both", expand=True, padx=16, pady=16)
        tk.Label(box, text=title, bg=t["card"], fg=t["fg"], font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(box, text=desc, bg=t["card"], fg=t["muted"], font=(FONT, 9), wraplength=220, justify="left").pack(anchor="w", pady=(6, 12))
        hover_btn(box, "Open", lambda p=dest: go(p), True, padx=14, pady=7).pack(anchor="w")
def profiles_page():
    t = T()
    page_header(body, "Profiles", "Create, rename, and configure launcher profiles.")
    if not gate("Profiles"):
        return
    for i, p in enumerate(profiles):
        row = card(body)
        top = tk.Frame(row, bg=t["card"])
        top.pack(fill="x")
        info = tk.Frame(top, bg=t["card"])
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=p.get("name", "Profile"), bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
        tk.Label(info, text=f'{p.get("version") or "Auto"}  •  {p.get("loader", "Vanilla")}', bg=t["card"], fg=t["muted"], font=(FONT, 9)).pack(anchor="w", pady=(4, 0))
        controls = tk.Frame(top, bg=t["card"])
        controls.pack(side="right")
        loader_var = tk.StringVar(value=p.get("loader", "Vanilla"))
        loader_box = ttk.Combobox(controls, textvariable=loader_var, values=LOADERS, state="readonly", width=10)
        loader_box.pack(side="left", padx=(0, 8))
        loader_box.bind("<<ComboboxSelected>>", lambda e, i=i, v=loader_var: set_loader(i, v.get()))
        hover_btn(controls, "Rename", lambda i=i: rename_profile(i)).pack(side="left", padx=(0, 8))
        hover_btn(controls, "Selected" if i == selected else "Select", lambda i=i: select_profile(i), i == selected).pack(side="left", padx=(0, 8))
        hover_btn(controls, "Delete", lambda i=i: delete_profile(i), enabled=len(profiles) > 1).pack(side="left")
    add = card(body)
    hover_btn(add, "New profile", new_profile, True).pack(anchor="w")
def select_profile(i):
    global selected
    selected = i
    save_state()
    render()
def rename_profile(i):
    name = simpledialog.askstring("Rename Profile", "Profile name:", initialvalue=profiles[i].get("name", "Profile"), parent=root)
    if name and name.strip():
        profiles[i]["name"] = name.strip()
        save_state()
        render()
def set_loader(i, loader):
    if loader in LOADERS:
        profiles[i]["loader"] = loader
        save_state()
        render()
def delete_profile(i):
    global selected
    if len(profiles) <= 1:
        return
    if not messagebox.askyesno("Delete Profile", f'Delete profile "{profiles[i].get("name", "Profile")}"?'):
        return
    profiles.pop(i)
    selected = min(selected, len(profiles) - 1)
    save_state()
    render()
def new_profile():
    if gate("Profiles"):
        profiles.append({"name": f"Profile {len(profiles) + 1}", "version": "", "loader": "Vanilla"})
        save_state()
        render()
def installations_page():
    t = T()
    page_header(body, "Installations", "Installed Minecraft versions from your Minecraft folder.")
    if not gate("Installations"):
        return
    vs = versions()
    if not vs:
        empty = card(body)
        tk.Label(empty, text="No Minecraft versions found.", bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
        tk.Label(empty, text="Install one with the official Minecraft Launcher first.", bg=t["card"], fg=t["muted"], font=(FONT, 10)).pack(anchor="w", pady=(6, 0))
        return
    current = selected_version()
    for v in vs:
        row = card(body)
        top = tk.Frame(row, bg=t["card"])
        top.pack(fill="x")
        tk.Label(top, text=v, bg=t["card"], fg=t["fg"], font=(FONT, 12, "bold")).pack(side="left")
        hover_btn(top, "Selected" if v == current else "Select", lambda v=v: set_version(v), v == current).pack(side="right")
def set_version(v):
    profiles[selected]["version"] = v
    save_state()
    render()
def java_ok():
    try:
        subprocess.run([settings.get("java_path") or "java", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=5)
        return True
    except Exception:
        return False
def repair_checks():
    d = mc_dir()
    return [
        ("Launcher app folder", os.path.isdir(APP), "app"),
        ("Settings", os.path.isfile(SETTINGS_FILE), "settings"),
        ("Profiles", os.path.isfile(PROFILES_FILE), "profiles"),
        ("Minecraft directory", bool(d and os.path.isdir(d)), "minecraft"),
        ("Official launcher evidence", owned(), "ownership"),
        ("Installed versions", bool(versions()), "versions"),
        ("Java", java_ok(), "java"),
        ("Updater configuration", bool(BASE_URL and VERSION_URL and LAUNCHER_URL), "updater"),
        ("Mod Workshop configuration", bool(MODRINTH), "workshop"),
        ("Theme system", all(k in T() for k in ("bg", "panel", "card", "fg", "muted", "accent", "button", "input", "menu", "hover", "selected")), "theme"),
        ("UI components", bool(root and root.winfo_exists()), "ui"),
        ("Offline bot", len(BOT_QA) >= 100, "bot"),
    ]
def safe_repair(kind):
    if kind == "app":
        os.makedirs(APP, exist_ok=True)
        return "Created launcher data folder."
    if kind == "settings":
        save_state()
        return "Rebuilt settings safely."
    if kind == "profiles":
        save_state()
        return "Rebuilt profiles safely."
    return ""
def test_everything():
    global last_tests
    last_tests = []
    for name, ok, kind in repair_checks():
        if ok:
            last_tests.append((name, "PASSED", ""))
        else:
            try:
                fixed = safe_repair(kind)
            except Exception:
                fixed = ""
            last_tests.append((name, "FIXED" if fixed else "USER ACTION", fixed or "No unsafe automatic fix was attempted."))
    passed = sum(s in ("PASSED", "FIXED") for _, s, _ in last_tests)
    msg = f"Villager Launcher {CURRENT_VERSION} — TEST EVERYTHING\n\nPassed/Fix: {passed}/{len(last_tests)}\n\n"
    msg += "\n".join(("✓" if s in ("PASSED", "FIXED") else "✕") + f" {n}: {s}" + (f" — {d}" if d else "") for n, s, d in last_tests)
    msg += "\n\nNo Minecraft files are deleted by this diagnostic."
    messagebox.showinfo("Test Everything", msg)
    if page == "Repair":
        render()
def repair_page():
    t = T()
    page_header(body, "Repair Center", "Run safe diagnostics without deleting Minecraft files.")
    hero = card(body)
    tk.Label(hero, text="Test everything", bg=t["card"], fg=t["fg"], font=(FONT, 16, "bold")).pack(anchor="w")
    tk.Label(hero, text="Checks launcher files, settings, profiles, Minecraft, Java, updater, Workshop, themes, and UI.", bg=t["card"], fg=t["muted"], font=(FONT, 10), wraplength=720, justify="left").pack(anchor="w", pady=(6, 12))
    hover_btn(hero, "Run test", test_everything, True).pack(anchor="w")
    for name, state, detail in last_tests:
        row = card(body)
        top = tk.Frame(row, bg=t["card"])
        top.pack(fill="x")
        tk.Label(top, text=name, bg=t["card"], fg=t["fg"], font=(FONT, 11, "bold")).pack(side="left")
        chip(top, state, state in ("PASSED", "FIXED")).pack(side="right")
        if detail:
            tk.Label(row, text=detail, bg=t["card"], fg=t["muted"], font=(FONT, 9)).pack(anchor="w", pady=(8, 0))
def launch_game():
    if not gate("Minecraft launching"):
        return
    v = selected_version()
    d = mc_dir()
    if not v:
        messagebox.showerror("Launch Error", "No Minecraft version is selected or installed.")
        return
    vd = os.path.join(d, "versions", v)
    jf = os.path.join(vd, v + ".json")
    jar = os.path.join(vd, v + ".jar")
    if not os.path.isfile(jf) or not os.path.isfile(jar):
        messagebox.showerror("Launch Error", "The selected Minecraft version is missing required files. The launcher did not delete or modify them.")
        return
    if not java_ok():
        messagebox.showerror("Launch Error", "Java could not be started.")
        return
    messagebox.showinfo("Minecraft", "Validation passed. Authenticated Microsoft launch integration is not enabled yet, so no game process was started.")
def workshop_precheck():
    results = []
    for name, ok, kind in repair_checks():
        if ok:
            results.append((name, "PASSED"))
        else:
            try:
                fixed = safe_repair(kind)
            except Exception:
                fixed = ""
            results.append((name, "FIXED" if fixed else "USER ACTION"))
    failures = [(n, s) for n, s in results if s == "USER ACTION"]
    passed = sum(s in ("PASSED", "FIXED") for _, s in results)
    if failures:
        details = "\n".join(f"✕ {n}: {s}" for n, s in failures)
        return messagebox.askyesno(
            "Workshop Pre-Check",
            f"Workshop diagnostic finished: {passed}/{len(results)} checks passed or safely fixed.\n\n"
            f"Issues needing attention:\n{details}\n\n"
            "Open Workshop anyway?",
        )
    messagebox.showinfo(
        "Workshop Pre-Check",
        f"All Workshop checks passed or were safely fixed.\n\n{passed}/{len(results)} checks ready.\n\nOpening Modrinth Workshop.",
    )
    return True
def workshop_page():
    global workshop_checked
    t = T()
    workshop_checked = True
    page_header(body, "Mod Workshop", "Browse Modrinth mods only. View projects without downloading or installing anything.")
    filters = card(body)
    row = tk.Frame(filters, bg=t["card"])
    row.pack(fill="x")
    q = ttk.Entry(row)
    q.insert(0, workshop_query)
    q.pack(side="left", fill="x", expand=True, ipady=6)
    ver = tk.StringVar(value=workshop_filters.get("version") or selected_version())
    sort = tk.StringVar(value=workshop_filters.get("sort", "Relevance"))
    ttk.Entry(row, textvariable=ver, width=12).pack(side="left", padx=6, ipady=6)
    ttk.Combobox(row, textvariable=sort, values=("Relevance", "Downloads", "Updated"), state="readonly", width=11).pack(side="left", padx=6)
    hover_btn(row, "Search Mods", lambda: search_workshop(q.get(), "Mod", ver.get(), sort.get(), "Any"), True, padx=16, pady=8).pack(side="left")
    q.bind("<Return>", lambda e: search_workshop(q.get(), "Mod", ver.get(), sort.get(), "Any"))
    note = card(body, accent=False)
    tk.Label(note, text="VIEW-ONLY WORKSHOP", bg=t["card"], fg=t["accent"], font=(FONT, 10, "bold")).pack(anchor="w")
    tk.Label(note, text="No mod downloads, installations, or .minecraft changes are performed by Workshop.", bg=t["card"], fg=t["muted"], font=(FONT, 9)).pack(anchor="w", pady=(3, 0))
    if workshop_loading:
        loading = card(body)
        tk.Label(loading, text="Searching Modrinth mods…", bg=t["card"], fg=t["muted"], font=(FONT, 11)).pack(anchor="w")
        return
    if workshop_error:
        err = card(body)
        tk.Label(err, text="Search failed", bg=t["card"], fg=t["danger"], font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(err, text=workshop_error, bg=t["card"], fg=t["muted"], font=(FONT, 9), wraplength=760, justify="left").pack(anchor="w", pady=(4, 10))
        hover_btn(err, "Retry", lambda: search_workshop(workshop_query, "Mod", ver.get(), sort.get(), "Any"), True).pack(anchor="w")
        return
    if not workshop_results:
        empty = card(body)
        tk.Label(empty, text="Search for a Minecraft mod.", bg=t["card"], fg=t["muted"], font=(FONT, 11)).pack(anchor="w")
        return
    count_row = tk.Frame(body, bg=t["bg"])
    count_row.pack(fill="x", padx=28)
    tk.Label(count_row, text=f"{len(workshop_results)} mod result(s)", bg=t["bg"], fg=t["muted"], font=(FONT, 9)).pack(anchor="w")
    shell = tk.Frame(body, bg=t["border"])
    shell.pack(fill="x", padx=28, pady=8)
    outer_panel = tk.Frame(shell, bg=t["card"])
    outer_panel.pack(fill="both", expand=True, padx=1, pady=1)
    strip_row = tk.Frame(outer_panel, bg=t["card"])
    strip_row.pack(fill="both", expand=True)
    tk.Frame(strip_row, bg=t["accent"], width=3).pack(side="left", fill="y")
    panel = tk.Frame(strip_row, bg=t["card"])
    panel.pack(side="left", fill="both", expand=True)
    for idx, p in enumerate(workshop_results):
        row = tk.Frame(panel, bg=t["card"])
        row.pack(fill="x", padx=20, pady=14)
        top = tk.Frame(row, bg=t["card"])
        top.pack(fill="x")
        icon_widget(top, p).pack(side="left", padx=(0, 12))
        def view_project(project=p):
            slug = project.get("slug") or project.get("project_id")
            if slug:
                webbrowser.open(f"https://modrinth.com/mod/{quote(str(slug))}")
        hover_btn(top, "View Project", view_project, True).pack(side="right", padx=(12, 0))
        title_area = tk.Frame(top, bg=t["card"])
        title_area.pack(side="left", fill="x", expand=True)
        tk.Label(title_area, text=p.get("title") or p.get("slug", "Unknown"), bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
        meta = tk.Frame(title_area, bg=t["card"])
        meta.pack(anchor="w", pady=(2, 0))
        chip(meta, "Mod", True).pack(side="left", padx=(0, 6))
        author = p.get("author") or "Unknown author"
        versions = p.get("versions") or []
        version_text = ", ".join(str(x) for x in versions[:6]) + ("…" if len(versions) > 6 else "")
        meta_text = f"by {author}  •  {p.get('downloads', 0):,} downloads"
        if version_text:
            meta_text += f"  •  versions: {version_text}"
        tk.Label(meta, text=meta_text, bg=t["card"], fg=t["muted"], font=(FONT, 8)).pack(side="left")
        desc = (p.get("description") or "").replace("\n", " ")
        tk.Label(row, text=desc[:220] + ("..." if len(desc) > 220 else ""), bg=t["card"], fg=t["muted"], font=(FONT, 9),
                 wraplength=760, justify="left").pack(anchor="w", pady=(8, 0), padx=(ICON_SIZE + 12, 0))
        if idx < len(workshop_results) - 1:
            tk.Frame(panel, bg=t["border"], height=1).pack(fill="x", padx=20)
    if workshop_more_available:
        more = card(body)
        hover_btn(more, "Load more", load_more_workshop, True).pack(anchor="w")
def _set_workshop_retry():
    global workshop_checked
    workshop_checked = False
PROJECT_TYPE_SLUG = {"Mod": "mod"}
def _workshop_facets(content_type, version, loader):
    facets = [["project_type:mod"]]
    v = (version or "").strip()
    if v:
        facets.append([f"versions:{v}"])
    return facets
def _workshop_search_url(query, content_type, version, sort, loader, offset, use_facets=True):
    idx = {"Relevance": "relevance", "Downloads": "downloads", "Updated": "updated"}.get(sort, "relevance")
    q = quote((query or "").strip())
    url = f"{MODRINTH}/search?query={q}&limit={WORKSHOP_PAGE_SIZE}&offset={int(offset)}&index={idx}"
    if use_facets:
        facets = _workshop_facets("Mod", version, "Any")
        url += "&facets=" + quote(json.dumps(facets, separators=(",", ":")))
    return url
def search_workshop(query, content_type, version, sort, loader="Any"):
    global workshop_results, workshop_offset, workshop_query, workshop_more_available, workshop_loading, workshop_filters, workshop_error
    workshop_query = query
    workshop_offset = 0
    workshop_filters = {"content_type": content_type, "version": version, "sort": sort, "loader": loader}
    workshop_loading = True
    workshop_error = ""
    render()
    root.update_idletasks()
    try:
        try:
            url = _workshop_search_url(query, "Mod", version, sort, "Any", 0, True)
            data = net_json(url)
        except Exception as first_error:
            if "400" not in str(first_error):
                raise
            url = _workshop_search_url(query, "Mod", "", sort, "Any", 0, False)
            data = net_json(url)
        workshop_results = [h for h in data.get("hits", []) if h.get("project_type") == "mod"]
        workshop_more_available = data.get("total_hits", 0) > len(workshop_results)
    except Exception as e:
        workshop_results = []
        workshop_more_available = False
        workshop_error = str(e)
    finally:
        workshop_loading = False
        render()
def load_more_workshop():
    global workshop_results, workshop_offset, workshop_more_available, workshop_loading
    workshop_offset += WORKSHOP_PAGE_SIZE
    workshop_loading = True
    render()
    root.update_idletasks()
    try:
        f = workshop_filters
        try:
            url = _workshop_search_url(workshop_query, "Mod", f.get("version", ""), f.get("sort", "Relevance"), "Any", workshop_offset, True)
            data = net_json(url)
        except Exception as first_error:
            if "400" not in str(first_error):
                raise
            url = _workshop_search_url(workshop_query, "Mod", "", f.get("sort", "Relevance"), "Any", workshop_offset, False)
            data = net_json(url)
        hits = [h for h in data.get("hits", []) if h.get("project_type") == "mod"]
        seen = {p.get("project_id") for p in workshop_results}
        workshop_results = workshop_results + [h for h in hits if h.get("project_id") not in seen]
        workshop_more_available = data.get("total_hits", 0) > len(workshop_results)
    except Exception as e:
        workshop_more_available = False
        messagebox.showerror("Workshop Error", str(e))
    finally:
        workshop_loading = False
        render()
def install_project(project):
    messagebox.showinfo("Workshop", "Workshop is view-only in Villager Launcher 2.1.1.\n\nNo files were downloaded or installed.")
def load_feature_state():
    global FEATURE_STATE
    raw = read_json(os.path.join(APP, "features.json"), {})
    FEATURE_STATE = raw if isinstance(raw, dict) else {}
def save_feature_state():
    os.makedirs(APP, exist_ok=True)
    with open(os.path.join(APP, "features.json"), "w", encoding="utf-8") as f:
        json.dump(FEATURE_STATE, f, indent=2)
def toggle_feature(name, var):
    FEATURE_STATE[name] = bool(var.get())
    save_feature_state()
def enable_all_features():
    for f in FEATURES:
        FEATURE_STATE[f["name"]] = True
    save_feature_state()
    render()
def disable_all_features():
    for f in FEATURES:
        FEATURE_STATE[f["name"]] = False
    save_feature_state()
    render()
def reset_features():
    FEATURE_STATE.clear()
    save_feature_state()
    render()
def hmm_button():
    global hmm_clicks
    hmm_clicks += 1
    messages = [
        "Hmmm... Villager is thinking.",
        "HMM! 500 features detected.",
        "Villager inspected the launcher. Hmmm.",
        "Hmmm... maybe add more buttons?",
        "EMERALD ACQUIRED. HMMMM.",
    ]
    if hmm_clicks >= 5:
        stop = messagebox.askyesno("STOP", "STOP PRESSING HMM BUTTONS?\n\nThe Villager has had enough Hmmm.")
        if not stop:
            save_state()
            save_feature_state()
            root.destroy()
            return
        hmm_clicks = 0
    messagebox.showinfo("Hmm", messages[(hmm_clicks - 1) % len(messages)])
def ideas_page():
    global ideas_query, ideas_category
    t = T()
    page_header(body, "500+ Features", "All 500 launcher ideas are registered here, with searchable local feature switches.")
    top = card(body)
    tk.Label(top, text=f"FEATURE REGISTRY • {len(FEATURES)} FEATURES", bg=t["card"], fg=t["fg"], font=(FONT, 14, "bold")).pack(anchor="w")
    tk.Label(top, text="These switches are local feature flags. Future releases can connect each flag to a deeper implementation without changing the registry.", bg=t["card"], fg=t["muted"], font=(FONT, 9), wraplength=760, justify="left").pack(anchor="w", pady=(5, 12))
    controls = tk.Frame(top, bg=t["card"])
    controls.pack(fill="x")
    q = ttk.Entry(controls)
    q.insert(0, ideas_query)
    q.pack(side="left", fill="x", expand=True, ipady=7)
    cats = ["All"] + sorted({f["category"] for f in FEATURES})
    cat = tk.StringVar(value=ideas_category if ideas_category in cats else "All")
    ttk.Combobox(controls, textvariable=cat, values=cats, state="readonly", width=24).pack(side="left", padx=8)
    def apply_filter():
        global ideas_query, ideas_category
        ideas_query, ideas_category = q.get().strip(), cat.get()
        render()
    hover_btn(controls, "Search", apply_filter, True, padx=14, pady=8).pack(side="left")
    hover_btn(controls, "Hmm", hmm_button, padx=14, pady=8).pack(side="left", padx=8)
    actions = tk.Frame(top, bg=t["card"])
    actions.pack(anchor="w", pady=(12, 0))
    hover_btn(actions, "Enable all", enable_all_features).pack(side="left", padx=(0, 8))
    hover_btn(actions, "Disable all", disable_all_features).pack(side="left", padx=(0, 8))
    hover_btn(actions, "Reset", reset_features).pack(side="left")
    q.bind("<Return>", lambda e: apply_filter())
    query = ideas_query.lower()
    shown = [f for f in FEATURES if (ideas_category == "All" or f["category"] == ideas_category) and (not query or query in f["name"].lower() or query in f["description"].lower())]
    count = card(body, accent=False)
    enabled_count = sum(bool(FEATURE_STATE.get(f["name"], False)) for f in FEATURES)
    tk.Label(count, text=f"Showing {len(shown)} / {len(FEATURES)} • Enabled locally: {enabled_count}", bg=t["card"], fg=t["muted"], font=(FONT, 9, "bold")).pack(anchor="w")
    for f in shown:
        row = card(body, accent=False)
        top_row = tk.Frame(row, bg=t["card"])
        top_row.pack(fill="x")
        tk.Label(top_row, text=f["name"], bg=t["card"], fg=t["fg"], font=(FONT, 10, "bold")).pack(side="left", fill="x", expand=True)
        var = tk.BooleanVar(value=bool(FEATURE_STATE.get(f["name"], False)))
        cb = tk.Checkbutton(top_row, text="Enabled", variable=var, command=lambda n=f["name"], v=var: toggle_feature(n, v), bg=t["card"], fg=t["accent"], selectcolor=t["input"], activebackground=t["card"], activeforeground=t["hover"], font=(FONT, 9, "bold"))
        cb.pack(side="right")
        tk.Label(row, text=f'{f["category"]}  •  {f["description"]}', bg=t["card"], fg=t["muted"], font=(FONT, 8), wraplength=760, justify="left").pack(anchor="w", pady=(5, 0))
def settings_page():
    t = T()
    page_header(body, "Settings", "Appearance, folders, updates, and launcher feature controls.")
    appearance = card(body)
    tk.Label(appearance, text="Appearance", bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
    tk.Label(appearance, text="Choose a full launcher theme.", bg=t["card"], fg=t["muted"], font=(FONT, 10)).pack(anchor="w", pady=(4, 10))
    row = tk.Frame(appearance, bg=t["card"])
    row.pack(anchor="w")
    var = tk.StringVar(value=settings.get("theme", "Villager Green"))
    ttk.Combobox(row, textvariable=var, values=list(THEMES) + list(custom_themes), state="readonly", width=28).pack(side="left")
    hover_btn(row, "Apply", lambda: apply_theme(var.get()), True).pack(side="left", padx=8)
    hover_btn(row, "Custom accent", create_custom_theme).pack(side="left")
    mc = card(body)
    tk.Label(mc, text="Minecraft folder", bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
    tk.Label(mc, text=settings.get("minecraft_path") or r"(Automatic: %APPDATA%\.minecraft)", bg=t["card"], fg=t["muted"], font=(FONT, 9)).pack(anchor="w", pady=(6, 10))
    hover_btn(mc, "Browse", choose_mc, True).pack(anchor="w")
    java = card(body)
    tk.Label(java, text="Java", bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
    tk.Label(java, text=settings.get("java_path") or "(System Java)", bg=t["card"], fg=t["muted"], font=(FONT, 9)).pack(anchor="w", pady=(6, 10))
    hover_btn(java, "Browse", choose_java, True).pack(anchor="w")
    updates = card(body)
    tk.Label(updates, text="Updates", bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
    tk.Label(updates, text="GitHub updates are checked manually from this page. Downloaded updates are staged before replacement.", bg=t["card"], fg=t["muted"], font=(FONT, 10), wraplength=760, justify="left").pack(anchor="w", pady=(6, 10))
    row = tk.Frame(updates, bg=t["card"])
    row.pack(anchor="w")
    hover_btn(row, "Check", check_updates, True).pack(side="left")
    hover_btn(row, "What's new", release_notes).pack(side="left", padx=8)
    hover_btn(row, "Rollback", rollback_launcher).pack(side="left")
def apply_theme(name):
    if name in THEMES or name in custom_themes:
        settings["theme"] = name
        save_state()
        render()
def create_custom_theme():
    chosen = colorchooser.askcolor(title="Choose theme accent", initialcolor=T()["accent"])
    if not chosen[1]:
        return
    name = f"Custom {len(custom_themes) + 1}"
    custom_themes[name] = dict(T())
    custom_themes[name]["accent"] = chosen[1]
    custom_themes[name]["button"] = chosen[1]
    custom_themes[name]["hover"] = chosen[1]
    custom_themes[name]["selected"] = chosen[1]
    custom_themes[name]["menu"] = chosen[1]
    settings["theme"] = name
    save_state()
    render()
def choose_mc():
    f = filedialog.askdirectory(title="Choose Minecraft folder")
    if f:
        settings["minecraft_path"] = f
        save_state()
        render()
def choose_java():
    f = filedialog.askopenfilename(title="Choose Java executable", filetypes=[("Executable", "*.exe"), ("All files", "*.*")])
    if f:
        settings["java_path"] = f
        save_state()
        render()
def release_notes():
    try:
        info = net_json(VERSION_URL, 8)
    except Exception:
        info = {"version": CURRENT_VERSION, "whats_new": {
            "Added": ["Startup loading screen", "Automatic previous-version backup", "One-click launcher rollback", "Expanded What's New release notes"],
            "Changed": ["Settings now includes Rollback", "Updater saves the version being replaced", "Startup shows loading stages"],
            "Removed": [],
            "Fixed": ["Previous-version recovery", "What's New metadata compatibility", "Empty update detection"]
        }}
    n = info.get("whats_new", info.get("notes", {}))
    lines = []
    if isinstance(n, dict):
        for k in ("Added", "Changed", "Removed", "Fixed"):
            if n.get(k):
                items = n[k] if isinstance(n[k], list) else [n[k]]
                lines.append(k.upper() + "\n" + "\n".join("• " + str(x) for x in items))
    text = f"Villager Launcher {info.get('version', CURRENT_VERSION)}\n\n" + ("\n\n".join(lines) if lines else "No release notes were provided.")
    messagebox.showinfo("What's New", text)
def download_update():
    with urlopen(Request(LAUNCHER_URL, headers={"User-Agent": f"Villager-Launcher/{CURRENT_VERSION}"}), timeout=20) as r:
        data = r.read()
    if not data:
        raise ValueError("The downloaded launcher is empty.")
    p = os.path.join(tempfile.gettempdir(), "villager_launcher_update.py")
    with open(p, "wb") as f:
        f.write(data)
    return p
def update_helper(source, target):
    h = os.path.join(tempfile.gettempdir(), "villager_update_helper.py")
    helper_code = "import sys,time,shutil,subprocess,os\ntime.sleep(1.5)\nsrc,target=sys.argv[1],sys.argv[2]\ntry:\n    shutil.copy2(src,target)\n    subprocess.Popen([sys.executable,target])\nfinally:\n    try: os.remove(src)\n    except OSError: pass\n    try: os.remove(__file__)\n    except OSError: pass"
    with open(h, "w", encoding="utf-8") as f:
        f.write(helper_code)
    subprocess.Popen([sys.executable, h, source, target], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), close_fds=True)
def rollback_launcher():
    if not os.path.isfile(PREVIOUS_LAUNCHER_FILE):
        messagebox.showinfo("Rollback", "No previous launcher version is available yet.\n\nA previous version will be saved automatically the next time you update.")
        return
    previous = str(read_json(PREVIOUS_VERSION_FILE, {}).get("version", "previous version"))
    if not messagebox.askyesno("Rollback Launcher", f"Restore Villager Launcher {previous}?\n\nThe launcher will close and restart with that previous version."):
        return
    try:
        target = os.path.abspath(sys.argv[0])
        rollback_file = os.path.join(tempfile.gettempdir(), "villager_launcher_rollback.py")
        with open(PREVIOUS_LAUNCHER_FILE, "rb") as src:
            data = src.read()
        if not data:
            raise ValueError("The previous launcher backup is empty.")
        with open(rollback_file, "wb") as f:
            f.write(data)
        update_helper(rollback_file, target)
        root.destroy()
    except Exception as e:
        messagebox.showerror("Rollback Error", str(e))
def vt(v):
    return tuple(int(re.sub(r"\D", "", x) or 0) for x in (str(v).split(".") + ["0", "0"])[:3])
def show_update_loading():
    t = T()
    w = tk.Toplevel(root)
    w.title("Villager Launcher Updater")
    w.geometry("520x300")
    w.resizable(False, False)
    w.configure(bg=t["panel"])
    w.transient(root)
    w.grab_set()
    tk.Label(w, text="VILLAGER LAUNCHER", bg=t["panel"], fg=t["accent"], font=(FONT, 12, "bold")).pack(pady=(28, 4))
    tk.Label(w, text="Updating Villager Launcher...", bg=t["panel"], fg=t["fg"], font=(FONT, 20, "bold")).pack()
    status = tk.StringVar(value="Checking for update...")
    tk.Label(w, textvariable=status, bg=t["panel"], fg=t["muted"], font=(FONT, 10)).pack(pady=(10, 16))
    bar = ttk.Progressbar(w, mode="indeterminate", length=390)
    bar.pack(pady=4)
    bar.start(12)
    stage = tk.Label(w, text="1 / 4  •  Checking", bg=t["panel"], fg=t["accent"], font=(FONT, 9, "bold"))
    stage.pack(pady=(12, 0))
    return w, status, stage, bar
def check_updates():
    loading = None
    try:
        info = net_json(VERSION_URL, 8)
        latest = str(info.get("version", CURRENT_VERSION))
        if vt(latest) <= vt(CURRENT_VERSION):
            messagebox.showinfo("Updates", f"Villager Launcher is up to date.\n\nVersion: {CURRENT_VERSION}")
            return
        if not messagebox.askyesno("Update Available", f"Version {latest} is available.\n\nInstalled: {CURRENT_VERSION}\nAvailable: {latest}\n\nUpdate now?"):
            return
        loading, status, stage, bar = show_update_loading()
        root.update_idletasks()
        status.set("Downloading the new launcher...")
        stage.config(text="2 / 4  •  Downloading")
        root.update_idletasks()
        src = download_update()
        status.set("Saving the current launcher for rollback...")
        stage.config(text="3 / 4  •  Backing up + installing")
        root.update_idletasks()
        target = os.path.abspath(sys.argv[0])
        os.makedirs(APP, exist_ok=True)
        with open(target, "rb") as current, open(PREVIOUS_LAUNCHER_FILE, "wb") as backup:
            backup.write(current.read())
        with open(PREVIOUS_VERSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"version": CURRENT_VERSION}, f, indent=2)
        update_helper(src, target)
        status.set("Restarting Villager Launcher...")
        stage.config(text="4 / 4  •  Restarting")
        bar.stop()
        root.update_idletasks()
        time.sleep(0.7)
        loading.grab_release()
        loading.destroy()
        root.destroy()
    except Exception as e:
        if loading is not None and loading.winfo_exists():
            try:
                loading.grab_release(); loading.destroy()
            except tk.TclError:
                pass
        messagebox.showerror("Update Error", str(e))
def startup_loading():
    t = T()
    root.configure(bg=t["panel"])
    for w in root.winfo_children():
        w.destroy()
    frame = tk.Frame(root, bg=t["panel"])
    frame.pack(fill="both", expand=True)
    tk.Label(frame, text="VILLAGER", bg=t["panel"], fg=t["accent"], font=(FONT, 28, "bold")).pack(pady=(170, 4))
    tk.Label(frame, text="LAUNCHER", bg=t["panel"], fg=t["muted"], font=(FONT, 11, "bold")).pack()
    status = tk.StringVar(value="Starting Villager Launcher...")
    tk.Label(frame, textvariable=status, bg=t["panel"], fg=t["fg"], font=(FONT, 11)).pack(pady=(30, 12))
    bar = ttk.Progressbar(frame, mode="determinate", maximum=100, length=390)
    bar.pack()
    version = tk.Label(frame, text=f"Version {CURRENT_VERSION}  •  Loading...", bg=t["panel"], fg=t["muted"], font=(FONT, 8))
    version.pack(pady=(12, 0))
    stages = [(18, "Loading launcher settings..."), (42, "Loading profiles and features..."), (68, "Preparing launcher interface..."), (88, "Finishing startup...")]
    def step(i=0):
        if not root.winfo_exists():
            return
        if i < len(stages):
            value, text = stages[i]
            bar["value"] = value
            status.set(text)
            root.after(260, lambda: step(i + 1))
        else:
            bar["value"] = 100
            status.set("Launcher ready!")
            version.config(text=f"Version {CURRENT_VERSION}  •  Ready")
            root.after(350, finish_startup_loading)
    step()
def finish_startup_loading():
    if root and root.winfo_exists():
        render()
def feedback_page():
    t = T()
    page_header(body, "Feedback Center", "Rate the launcher and leave notes locally.")
    box = card(body)
    rating = tk.IntVar(value=5)
    stars = tk.Frame(box, bg=t["card"])
    stars.pack(anchor="w")
    for i in range(1, 6):
        tk.Radiobutton(stars, text="★", variable=rating, value=i, font=(FONT, 18), bg=t["card"], fg=t["accent"],
                       selectcolor=t["card"], activebackground=t["card"], activeforeground=t["hover"]).pack(side="left")
    tk.Label(box, text="Your feedback", bg=t["card"], fg=t["fg"], font=(FONT, 11, "bold")).pack(anchor="w", pady=(12, 6))
    text = tk.Text(box, font=(FONT, 10), bg=t["input"], fg=t["fg"], insertbackground=t["fg"], relief="flat", height=10, wrap="word")
    text.pack(fill="x")
    hover_btn(box, "Save feedback", lambda: save_feedback(rating.get(), text.get("1.0", "end").strip()), True).pack(anchor="w", pady=(12, 0))
def save_feedback(rating, text):
    if not text:
        messagebox.showwarning("Feedback", "Please enter feedback.")
        return
    os.makedirs(os.path.join(APP, "feedback"), exist_ok=True)
    f = os.path.join(APP, "feedback", time.strftime("feedback_%Y%m%d_%H%M%S.json"))
    with open(f, "w", encoding="utf-8") as z:
        json.dump({"version": CURRENT_VERSION, "rating": rating, "feedback": text, "timestamp": time.time()}, z, indent=2)
    messagebox.showinfo("Feedback Saved", "Saved locally. Nothing was uploaded automatically.")
BOT_QA = {
    "Minecraft": "a sandbox game about building, exploration, crafting, and survival.",
    "Minecraft Java Edition": "the PC edition of Minecraft known for mods, servers, snapshots, and customization.",
    "Minecraft Bedrock Edition": "the cross-platform Minecraft edition available on supported Windows, consoles, mobile, and other devices.",
    "a Minecraft mod": "a modification that adds, removes, or changes game features.",
    "Modrinth": "a platform for Minecraft mods, resource packs, shaders, and related projects.",
    "Minecraft Forge": "a mod loader and modding platform for Minecraft Java Edition.",
    "Fabric": "a lightweight Minecraft mod loader and modding toolchain.",
    "Sodium": "a Minecraft performance mod focused on improving rendering performance.",
    "Iris": "a Minecraft shader mod that adds shader support and commonly works alongside Sodium.",
    "OptiFine": "a Minecraft optimization and graphics-customization mod.",
    "a resource pack": "a pack that changes textures, sounds, models, fonts, and other Minecraft assets.",
    "a shader": "a graphics effect system that changes Minecraft lighting, shadows, water, skies, and more.",
    "a data pack": "a system for changing or adding supported Minecraft gameplay data and functions.",
    "redstone": "Minecraft's system for building logic circuits and automated mechanisms.",
    "a Creeper": "a hostile Minecraft mob famous for silently approaching players and exploding.",
    "a Villager": "a passive Minecraft NPC that can trade and use different professions.",
    "an Enderman": "a tall neutral mob that can teleport and pick up certain blocks.",
    "the Nether": "a dangerous Minecraft dimension with unique terrain, mobs, structures, and resources.",
    "the End": "a Minecraft dimension containing Endermen, End Cities, and the Ender Dragon.",
    "the Ender Dragon": "the major boss associated with Minecraft's End dimension.",
    "a Minecraft seed": "a value used by world generation to determine the generated world.",
    "a Minecraft snapshot": "a development build used to test upcoming Java Edition features.",
    "a Minecraft version": "a specific Minecraft release, such as 1.20.1.",
    "a game launcher": "a program that manages game versions, profiles, settings, and launching.",
    "a Minecraft profile": "a saved set of launcher choices such as a selected game version.",
    "the Minecraft folder": "the main Java Edition data directory, commonly %APPDATA%\\.minecraft on Windows.",
    "the mods folder": "the folder commonly used for compatible Java Edition mod files.",
    "the versions folder": "the folder containing Minecraft version directories and their files.",
    "a JAR file": "a Java archive file used by Java applications and Minecraft components.",
    "Java": "the programming language and runtime used by Minecraft Java Edition.",
    "Python": "a general-purpose programming language with readable syntax and a large ecosystem.",
    "Tkinter": "Python's standard interface to the Tk GUI toolkit.",
    "GitHub": "a platform for hosting Git repositories and collaborating on software.",
    "Git": "a distributed version-control system for tracking changes.",
    "an API": "an interface that lets software communicate with another program or service.",
    "JSON": "a lightweight text format for structured data exchange.",
    "an EXE": "a Windows executable file used to run a program.",
    "RAM": "short-term working memory used while programs are running.",
    "a CPU": "the processor that executes instructions and performs general-purpose computation.",
    "a GPU": "a processor specialized for highly parallel graphics and computation.",
    "an SSD": "solid-state storage using flash memory instead of spinning disks.",
    "an HDD": "magnetic storage using spinning disks and mechanical read/write heads.",
    "FPS": "frames per second, describing how many frames are rendered each second.",
    "ping": "a measurement of network round-trip latency, usually in milliseconds.",
    "a device driver": "software that lets an operating system communicate with hardware.",
    "Windows": "Microsoft's family of operating systems.",
    "Windows 7": "Microsoft's desktop operating system released in 2009.",
    "Windows 10": "Microsoft's desktop operating system introduced in 2015.",
    "Windows 11": "Microsoft's current-generation desktop operating system family.",
    "Android": "a mobile operating system and software platform developed by Google and the open-source Android project.",
    "Samsung": "an electronics company known for phones, displays, appliances, and semiconductors.",
    "the Galaxy Note9": "a Samsung smartphone from 2018 with an S Pen.",
    "the Galaxy S24 Ultra": "a Samsung flagship smartphone with an S Pen.",
    "the S Pen": "Samsung's stylus for writing, drawing, and controls on supported Galaxy devices.",
    "USB": "a standard interface for connecting devices and carrying data or power.",
    "USB-C": "a reversible USB connector format used for data, power, displays, and accessories.",
    "Micro-USB": "an older small USB connector used by many phones and accessories.",
    "HDMI": "a digital interface commonly used to carry video and audio.",
    "Wi-Fi": "a family of wireless networking standards for local wireless connections.",
    "Bluetooth": "a short-range wireless technology for connecting devices and peripherals.",
    "an operating system": "software that manages hardware and provides services to applications.",
    "a file system": "the system that organizes how files and directories are stored and accessed.",
    "a folder": "a container used to organize files and other folders.",
    "a backup": "a separate copy of data kept so it can be restored later.",
    "troubleshooting": "the process of identifying a problem, testing causes, and applying safe fixes.",
    "Windows Safe Mode": "a minimal Windows startup mode useful for diagnosing software and driver problems.",
    "Task Manager": "a Windows utility for viewing processes, performance, startup items, and related information.",
    "Device Manager": "a Windows utility for viewing hardware devices and their drivers.",
    "Command Prompt": "a Windows command-line environment.",
    "PowerShell": "Microsoft's command shell and scripting environment.",
    "a batch file": "a text file containing Windows command-line instructions, commonly ending in .bat.",
    "a Python script": "a text file containing Python code executed by a Python interpreter.",
    "an environment variable": "a named value supplied by the operating system to programs.",
    "APPDATA": "a Windows environment variable pointing to the user's application-data directory.",
    "a cache": "temporary stored data used to speed up repeated operations.",
    "a browser": "software used to access websites and web applications.",
    "Chromium": "an open-source browser project used as the base of several browsers.",
    "Steam": "a digital game distribution and gaming platform operated by Valve.",
    "Roblox": "an online platform where users can play and create interactive experiences.",
    "Roblox Studio": "the development environment used to create Roblox experiences.",
    "Lua": "a lightweight scripting language used by many applications and games.",
    "Luau": "Roblox's scripting language derived from Lua.",
    "a Minecraft command": "an instruction entered through Minecraft's command system.",
    "Creative mode": "a Minecraft mode with extensive building resources and special movement abilities.",
    "Survival mode": "a Minecraft mode focused on gathering resources, crafting, health, hunger, and survival.",
    "Hardcore mode": "a difficult Survival variant with a single-life rule.",
    "a crafting table": "a Minecraft block providing the larger 3-by-3 crafting grid.",
    "a furnace": "a Minecraft block that smelts or cooks items using fuel.",
    "an enchantment": "a magical effect applied to supported Minecraft equipment and items.",
    "an anvil": "a Minecraft block used to combine, repair, and rename certain items.",
    "a beacon": "a Minecraft block that can provide status effects when activated.",
    "a Nether portal": "a gateway that transports players between the Overworld and Nether.",
    "an End portal": "the gateway used to reach the End dimension.",
    "a stronghold": "an underground structure containing the End portal room.",
    "an Ancient City": "a Deep Dark structure containing valuable loot and the Warden.",
    "the Warden": "a powerful hostile mob associated with the Deep Dark.",
    "a biome": "a region of a Minecraft world with characteristic terrain, climate, vegetation, and mobs.",
    "a chunk": "a 16-by-16-column section of a Minecraft world used for world storage and processing.",
    "a block": "the basic cube-shaped unit making up much of Minecraft's world.",
    "a Minecraft tick": "a unit of game simulation time; Minecraft normally targets 20 ticks per second.",
}
def bot_answer(q):
    q = re.sub(r"[^a-z0-9 ]+", " ", q.lower()).strip()
    if not q:
        return "Ask me a question."
    if q in BOT_QA:
        return BOT_QA[q]
    words = set(q.split())
    best = max(BOT_QA, key=lambda k: len(words & set(k.split())), default="")
    return BOT_QA[best] if best and len(words & set(best.split())) >= 2 else "I'm offline. I can answer from my built-in 112-question knowledge pack about Minecraft, Modrinth, Windows, Python, Java, Samsung, Roblox, and PC hardware."
def open_villager_bot():
    t = T()
    w = tk.Toplevel(root)
    w.title("Villager Bot — Offline")
    w.geometry("720x620")
    w.configure(bg=t["panel"])
    tk.Label(w, text="Villager Bot", font=(FONT, 22, "bold"), bg=t["panel"], fg=t["fg"]).pack(pady=(18, 2))
    tk.Label(w, text="Offline  •  112 built-in questions  •  no network required", font=(FONT, 9), bg=t["panel"], fg=t["muted"]).pack(pady=(0, 12))
    out = tk.Text(w, font=(FONT, 11), bg=t["input"], fg=t["fg"], insertbackground=t["fg"], relief="flat", wrap="word")
    out.pack(fill="both", expand=True, padx=20, pady=8)
    out.insert("end", "Villager Bot: Hey! I work completely offline. Ask me something!\n\n")
    out.configure(state="disabled")
    ent = ttk.Entry(w)
    ent.pack(fill="x", padx=20, pady=8, ipady=9)
    def send():
        q = ent.get().strip()
        if not q:
            return
        out.configure(state="normal")
        out.insert("end", f"You: {q}\nVillager Bot: {bot_answer(q)}\n\n")
        out.see("end")
        out.configure(state="disabled")
        ent.delete(0, "end")
    hover_btn(w, "Send", send, True).pack(pady=(0, 16))
    ent.bind("<Return>", lambda e: send())
    ent.focus_set()
load_state()
load_feature_state()
root = tk.Tk()
root.title(f"Villager Launcher {CURRENT_VERSION}")
root.geometry(f"{int(settings.get('window_width', 1260))}x{int(settings.get('window_height', 800))}")
root.minsize(1000, 650)
root.protocol("WM_DELETE_WINDOW", lambda: (save_state(), root.destroy()))
startup_loading()
root.mainloop()
