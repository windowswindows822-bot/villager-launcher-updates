import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import json, os, sys, tempfile, subprocess, shutil, time, zipfile
from urllib.request import urlopen, Request

CURRENT_VERSION = "1.7.0"
BASE_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main"
VERSION_URL = BASE_URL + "/version.json"
LAUNCHER_URL = BASE_URL + "/launcher.py"
APP_DIR = os.path.join(os.environ.get("APPDATA", tempfile.gettempdir()), "VillagerLauncher")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
PROFILES_FILE = os.path.join(APP_DIR, "profiles.json")
FONT = "Segoe UI Variable"

THEMES = {
"Villager Green":{"bg":"#101810","panel":"#182418","card":"#203020","fg":"#FFFFFF","muted":"#AFC3AF","accent":"#62C462","button":"#2D442D","danger":"#B94A48"},
"Midnight":{"bg":"#0A0E18","panel":"#121827","card":"#1A2338","fg":"#FFFFFF","muted":"#AAB6D3","accent":"#7188FF","button":"#29365B","danger":"#D05B5B"},
"Sky":{"bg":"#DCEFF8","panel":"#F7FCFF","card":"#EAF5FA","fg":"#173042","muted":"#5C7180","accent":"#3A91C9","button":"#C7E0ED","danger":"#B64E4E"},
"Nether":{"bg":"#180C0C","panel":"#2A1212","card":"#391919","fg":"#FFFFFF","muted":"#D0A8A8","accent":"#E05A5A","button":"#542626","danger":"#FF8A70"},
"Ocean":{"bg":"#071820","panel":"#0D2833","card":"#123743","fg":"#FFFFFF","muted":"#9FC5D0","accent":"#38A7C7","button":"#1B4655","danger":"#D45D67"},
"Dirt":{"bg":"#24180F","panel":"#352416","card":"#47301E","fg":"#FFF8EC","muted":"#C9B69D","accent":"#9B6B43","button":"#60452C","danger":"#B94A48"},
"Stone":{"bg":"#202124","panel":"#2C2D30","card":"#393A3D","fg":"#F5F5F5","muted":"#B9BABD","accent":"#A0A3A8","button":"#4A4C50","danger":"#C65A5A"},
"Diamond":{"bg":"#071D24","panel":"#0D3038","card":"#12404A","fg":"#F1FFFF","muted":"#9AC9CF","accent":"#59D8E4","button":"#1C5962","danger":"#D35C68"},
"Gold":{"bg":"#211A06","panel":"#302707","card":"#40360B","fg":"#FFFBEA","muted":"#D2C28A","accent":"#E8C84A","button":"#5B4B13","danger":"#C45B45"},
"Redstone":{"bg":"#210B0B","panel":"#351010","card":"#471818","fg":"#FFF5F5","muted":"#D5AAAA","accent":"#F04D4D","button":"#641E1E","danger":"#FF7777"},
"Lapis":{"bg":"#08162B","panel":"#0D2140","card":"#123058","fg":"#F4F8FF","muted":"#A5B9D5","accent":"#4C83D8","button":"#1D4070","danger":"#D45D67"},
"Amethyst":{"bg":"#190D26","panel":"#28143A","card":"#382052","fg":"#FFF7FF","muted":"#C5A9D5","accent":"#B66CDE","button":"#513078","danger":"#E06A78"},
"Copper":{"bg":"#24130D","panel":"#382016","card":"#4A2B1D","fg":"#FFF7F1","muted":"#D2B0A0","accent":"#D77B4D","button":"#67402D","danger":"#C9584C"},
"Forest":{"bg":"#08170D","panel":"#102719","card":"#183622","fg":"#F4FFF5","muted":"#A6C5AA","accent":"#55B96A","button":"#245B32","danger":"#C75A55"},
"Cherry Grove":{"bg":"#260F1B","panel":"#3A1727","card":"#4C2034","fg":"#FFF7FB","muted":"#D6ADBE","accent":"#F083B0","button":"#6B2F4A","danger":"#E05D69"},
"Desert":{"bg":"#261E10","panel":"#382D18","card":"#4A3C20","fg":"#FFFBEF","muted":"#D0C19B","accent":"#D6B45B","button":"#66532B","danger":"#C55D4D"},
"Snow":{"bg":"#DDE8F0","panel":"#F4F9FC","card":"#E7F0F6","fg":"#20313C","muted":"#647883","accent":"#5A9DC5","button":"#C7DDE9","danger":"#B65353"},
"Volcano":{"bg":"#1D0905","panel":"#30100A","card":"#45170E","fg":"#FFF8F0","muted":"#D4AAA0","accent":"#FF713F","button":"#652416","danger":"#FF9B50"},
"End":{"bg":"#090610","panel":"#150D1E","card":"#21132E","fg":"#FAF4FF","muted":"#BBA8C7","accent":"#B75BE8","button":"#3D2052","danger":"#D75D7D"},
"Piglin":{"bg":"#2A1018","panel":"#3C1822","card":"#51212D","fg":"#FFF4F5","muted":"#D7AEB5","accent":"#E6A06D","button":"#6C3040","danger":"#F06A62"},
"Swamp":{"bg":"#111A0D","panel":"#1B2913","card":"#26381A","fg":"#F5FFE9","muted":"#B5C59C","accent":"#86B84A","button":"#3C5724","danger":"#C45C52"},
"Plains":{"bg":"#132014","panel":"#20351F","card":"#2D4729","fg":"#F8FFF3","muted":"#B2C7A8","accent":"#8BC34A","button":"#426332","danger":"#C85C55"},
"Jungle":{"bg":"#071A10","panel":"#0D2A19","card":"#143923","fg":"#F2FFF5","muted":"#9FC5AA","accent":"#39C66A","button":"#1D6038","danger":"#C45A5A"},
"Ice":{"bg":"#071A24","panel":"#0D2A38","card":"#123A4B","fg":"#F2FCFF","muted":"#A4C7D2","accent":"#6DD6F2","button":"#1E596B","danger":"#C65B68"},
"Deep Dark":{"bg":"#070B0E","panel":"#0D1318","card":"#141E24","fg":"#E8FFFF","muted":"#91A8AD","accent":"#27D0C0","button":"#173D3B","danger":"#C95762"},
"Stronghold":{"bg":"#151515","panel":"#202020","card":"#2D2D2D","fg":"#F5F5F5","muted":"#B2B2B2","accent":"#C0C0C0","button":"#444444","danger":"#C45A5A"},
"Sunrise":{"bg":"#24100C","panel":"#3A1A12","card":"#4C2419","fg":"#FFF8F1","muted":"#D6B0A0","accent":"#FF9B5B","button":"#6D3624","danger":"#D65D54"},
"Night":{"bg":"#050812","panel":"#0B1020","card":"#121A2E","fg":"#F5F8FF","muted":"#9BAAC8","accent":"#6B8CFF","button":"#25345E","danger":"#C85A6B"},
"Redstone Lab":{"bg":"#130D0C","panel":"#211514","card":"#30201E","fg":"#FFF8F6","muted":"#C5A9A4","accent":"#FF4F38","button":"#54241D","danger":"#FF8270"},
"Creeper":{"bg":"#0A1709","panel":"#11230E","card":"#193515","fg":"#F5FFF0","muted":"#AAC59E","accent":"#69D34B","button":"#2B5B20","danger":"#D05B55"}
}
DEFAULT_SETTINGS={"theme":"Villager Green","remember_window":True,"window_width":1120,"window_height":720,"minecraft_path":"","java_path":"","confirm_updates":True,"start_page":"Home","ui_density":"Comfortable"}
settings=dict(DEFAULT_SETTINGS); profiles=[]; selected_profile=0; current_theme="Villager Green"; custom_themes={}; root=None; content=None; status=None; nav_buttons={}


def load_json(path,default):
    try:
        with open(path,"r",encoding="utf-8") as f:return json.load(f)
    except (OSError,json.JSONDecodeError):return default


def save_settings():
    try:
        os.makedirs(APP_DIR,exist_ok=True); data=dict(settings); data["theme"]=current_theme; data["custom_themes"]=custom_themes
        with open(SETTINGS_FILE,"w",encoding="utf-8") as f:json.dump(data,f,indent=2)
    except OSError:pass


def load_settings():
    global settings,current_theme,custom_themes
    data=load_json(SETTINGS_FILE,{})
    if isinstance(data,dict):
        for k in DEFAULT_SETTINGS:
            if k in data:settings[k]=data[k]
        if data.get("theme") in THEMES:current_theme=data["theme"]
        custom_themes=data.get("custom_themes",{}) if isinstance(data.get("custom_themes",{}),dict) else {}
        if data.get("theme") in custom_themes:current_theme=data["theme"]


def save_profiles():
    try:
        os.makedirs(APP_DIR,exist_ok=True)
        with open(PROFILES_FILE,"w",encoding="utf-8") as f:json.dump(profiles,f,indent=2)
    except OSError:pass


def load_profiles():
    global profiles,selected_profile
    data=load_json(PROFILES_FILE,[]); profiles=data if isinstance(data,list) else []
    if not profiles:
        profiles=[{"name":"Default","version":"","loader":"Vanilla","description":"Your first Villager Launcher profile.","pfile":""}];save_profiles()
    selected_profile=min(selected_profile,len(profiles)-1)


def theme():
    if current_theme in custom_themes:return custom_themes[current_theme]
    return THEMES.get(current_theme,THEMES["Villager Green"])


def github_request(url,timeout=10):
    q="&" if "?" in url else "?"
    return urlopen(Request(url+q+"t="+str(time.time_ns()),headers={"User-Agent":"Villager-Launcher"}),timeout=timeout)


def latest_info():
    with github_request(VERSION_URL,5) as r:data=json.loads(r.read().decode("utf-8"))
    if not isinstance(data,dict) or not data.get("version"):raise ValueError("Version information is missing.")
    return data


def download_update():
    with github_request(LAUNCHER_URL,15) as r:data=r.read()
    if not data:raise ValueError("Downloaded launcher is empty.")
    path=os.path.join(tempfile.gettempdir(),"villager_launcher_update.py")
    with open(path,"wb") as f:f.write(data)
    return path


def finish_update(target):
    source=os.path.abspath(sys.argv[0]);target=os.path.abspath(target);time.sleep(2)
    for _ in range(30):
        try:
            shutil.copy2(source,target);subprocess.Popen([sys.executable,target],close_fds=True)
            try:os.remove(source)
            except OSError:pass
            return
        except OSError:time.sleep(1)
    try:messagebox.showerror("Update Error","Windows could not replace the launcher file.")
    except tk.TclError:pass


def install_update(path):
    subprocess.Popen([sys.executable,path,"--install-update",os.path.abspath(sys.argv[0])],creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0),close_fds=True);root.destroy()


def release_text(info):
    notes=info.get("notes",{});parts=[]
    if isinstance(notes,dict):
        for k in ("Added","Changed","Removed","Fixed"):
            items=notes.get(k,[]);items=[items] if isinstance(items,str) else items
            if items:parts.append(k.upper()+"\n"+"\n".join("• "+str(x) for x in items))
    return "\n\n".join(parts) or "No changes listed."


def check_updates():
    try:
        status.config(text="Checking for updates...");info=latest_info();newest=str(info["version"])
        if newest==CURRENT_VERSION:
            status.config(text="Up to date");messagebox.showinfo("Updates",f"Villager Launcher is up to date!\n\nInstalled: {CURRENT_VERSION}\nServer: {newest}");return
        notes=release_text(info)
        if settings.get("confirm_updates",True) and not messagebox.askyesno("Update Available",f"Version {newest} is available.\n\nWHAT'S NEW\n{notes}\n\nInstall now?"):
            status.config(text="Update available");return
        status.config(text="Installing update...");install_update(download_update())
    except Exception as exc:status.config(text="Update failed");messagebox.showerror("Update Error",str(exc))


def mc_dir():
    p=settings.get("minecraft_path","")
    if p and os.path.isdir(p):return p
    appdata=os.environ.get("APPDATA");return os.path.join(appdata,".minecraft") if appdata else None


def ownership_verified():
    folder=mc_dir()
    return bool(folder and os.path.isdir(folder) and (os.path.isfile(os.path.join(folder,"launcher_accounts.json")) or os.path.isfile(os.path.join(folder,"launcher_profiles.json"))))


def require_minecraft(feature):
    if ownership_verified():return True
    messagebox.showwarning("Minecraft Required",f"{feature} is locked until an original Minecraft installation is detected.\n\nSign in through the official Minecraft launcher and select its Minecraft data folder in Villager Launcher Settings.");return False


def installed_versions():
    folder=os.path.join(mc_dir(),"versions") if mc_dir() else ""
    try:return sorted([x for x in os.listdir(folder) if os.path.isdir(os.path.join(folder,x))],reverse=True) if os.path.isdir(folder) else []
    except OSError:return []


def mod_files():
    folder=os.path.join(mc_dir(),"mods") if mc_dir() else ""
    try:return sorted([x for x in os.listdir(folder) if x.lower().endswith(".jar")]) if os.path.isdir(folder) else []
    except OSError:return []


def load_pfp(profile,size):
    p=profile.get("pfile","")
    if not p or not os.path.isfile(p):return None
    try:
        image=tk.PhotoImage(file=p);factor=max(1,int(max(image.width(),image.height())/size));return image.subsample(factor,factor) if factor>1 else image
    except tk.TclError:return None


def pick_pfp(index):
    if not require_minecraft("Profile pictures"):return
    p=filedialog.askopenfilename(title="Choose profile picture",filetypes=[("PNG images","*.png"),("GIF images","*.gif"),("BMP images","*.bmp")])
    if p:profiles[index]["pfile"]=p;save_profiles();rebuild_ui()


def create_profile():
    if not require_minecraft("Profiles"):return
    win=tk.Toplevel(root);win.title("New Profile");win.geometry("430x190");win.configure(bg=theme()["panel"]);win.grab_set()
    label(win,"Profile name",11,True).pack(anchor="w",padx=25,pady=(25,8));entry=tk.Entry(win,font=(FONT,11));entry.pack(fill="x",padx=25);entry.focus_set()
    def done():
        n=entry.get().strip()
        if n:profiles.append({"name":n,"version":"","loader":"Vanilla","description":"","pfile":""});save_profiles();win.destroy();rebuild_ui()
    btn(win,"CREATE",done,True).pack(anchor="e",padx=25,pady=18)


def choose_mc():
    p=filedialog.askdirectory(title="Choose Minecraft folder")
    if p:settings["minecraft_path"]=p;save_settings();render_settings()


def choose_java():
    p=filedialog.askopenfilename(title="Choose Java executable",filetypes=[("Java executable","java.exe"),("All files","*.*")])
    if p:settings["java_path"]=p;save_settings();render_settings()


def set_theme(name):
    global current_theme
    if name in THEMES or name in custom_themes:current_theme=name;save_settings();rebuild_ui()


def delete_custom_theme(name):
    global current_theme
    if name not in custom_themes:return
    if messagebox.askyesno("Delete Theme",f"Delete custom theme '{name}'?"):
        del custom_themes[name]
        if current_theme==name:current_theme="Villager Green"
        save_settings();rebuild_ui()


def duplicate_theme():
    base=theme();name_var=tk.StringVar(value=current_theme+" Copy");win=tk.Toplevel(root);win.title("Create Custom Theme");win.geometry("560x560");win.configure(bg=base["panel"]);win.grab_set()
    fields={};wrap=tk.Frame(win,bg=base["panel"]);wrap.pack(fill="both",expand=True,padx=24,pady=20)
    tk.Label(wrap,text="CUSTOM THEME EDITOR",font=(FONT,18,"bold"),bg=base["panel"],fg=base["fg"]).pack(anchor="w")
    tk.Label(wrap,text="Build a complete launcher theme with live preview.",font=(FONT,10),bg=base["panel"],fg=base["muted"]).pack(anchor="w",pady=(3,16))
    row=tk.Frame(wrap,bg=base["panel"]);row.pack(fill="x",pady=5);tk.Label(row,text="Theme name",font=(FONT,10,"bold"),bg=base["panel"],fg=base["fg"]).pack(side="left");tk.Entry(row,textvariable=name_var,font=(FONT,10)).pack(side="right",fill="x",expand=True,padx=(20,0))
    keys=["bg","panel","card","fg","muted","accent","button","danger"]
    preview=tk.Frame(wrap,bg=base["card"]);preview.pack(fill="x",pady=12)
    def refresh_preview():
        for w in preview.winfo_children():w.destroy()
        d={k:fields[k].get().strip() or base[k] for k in keys}
        preview.configure(bg=d["card"]);tk.Label(preview,text="Villager Launcher",font=(FONT,15,"bold"),bg=d["card"],fg=d["fg"]).pack(anchor="w",padx=16,pady=(12,2));tk.Label(preview,text="Your Minecraft, Your Way.",font=(FONT,9),bg=d["card"],fg=d["muted"]).pack(anchor="w",padx=16);tk.Button(preview,text="PLAY",font=(FONT,9,"bold"),bg=d["accent"],fg="white",relief="flat",bd=0).pack(anchor="e",padx=16,pady=12)
    for k in keys:
        r=tk.Frame(wrap,bg=base["panel"]);r.pack(fill="x",pady=2);tk.Label(r,text=k.upper(),width=12,anchor="w",font=(FONT,9,"bold"),bg=base["panel"],fg=base["fg"]).pack(side="left");fields[k]=tk.StringVar(value=base[k]);e=tk.Entry(r,textvariable=fields[k],font=(FONT,9));e.pack(side="left",fill="x",expand=True,padx=6);tk.Button(r,text="COLOR",command=lambda v=fields[k]:pick_color(v),relief="flat",bd=0).pack(side="right")
    refresh_preview()
    for v in fields.values():v.trace_add("write",lambda *_:refresh_preview())
    def save():
        n=name_var.get().strip() or "My Theme";d={k:fields[k].get().strip() for k in keys}
        try:
            for c in d.values():
                if not (len(c)==7 and c.startswith("#")):raise ValueError
        except ValueError:messagebox.showerror("Theme Error","Use valid 6-digit colors such as #62C462.",parent=win);return
        custom_themes[n]=d
        globals()["current_theme"]=n;save_settings();win.destroy();rebuild_ui()
    bottom=tk.Frame(wrap,bg=base["panel"]);bottom.pack(fill="x",pady=14);btn(bottom,"CANCEL",win.destroy).pack(side="right",padx=(8,0));btn(bottom,"SAVE THEME",save,True).pack(side="right")


def pick_color(var):
    c=colorchooser.askcolor(title="Choose theme color",initialcolor=var.get())[1]
    if c:var.set(c)


def reset_settings():
    global settings,current_theme,custom_themes
    if messagebox.askyesno("Reset Settings","Reset Villager Launcher settings? Your Minecraft files and profiles will not be deleted."):
        settings=dict(DEFAULT_SETTINGS);current_theme="Villager Green";custom_themes={};save_settings();rebuild_ui()


def play_selected():
    if require_minecraft("Minecraft launching"):messagebox.showinfo("Minecraft","Original Minecraft installation detected.\n\nLaunch integration will be enabled in a future release.")


def import_mod():
    if not require_minecraft("Mods"):return
    files=filedialog.askopenfilenames(title="Import Minecraft mods",filetypes=[("Minecraft mods","*.jar")])
    if not files:return
    try:
        folder=os.path.join(mc_dir(),"mods");os.makedirs(folder,exist_ok=True)
        for p in files:shutil.copy2(p,os.path.join(folder,os.path.basename(p)))
        render_mods()
    except OSError as e:messagebox.showerror("Mod Error",str(e))


def disable_mod(name):
    if not require_minecraft("Mods"):return
    try:
        d=os.path.join(mc_dir(),"mods_disabled");os.makedirs(d,exist_ok=True);shutil.move(os.path.join(mc_dir(),"mods",name),os.path.join(d,name));render_mods()
    except OSError as e:messagebox.showerror("Mod Error",str(e))


def create_backup():
    if not require_minecraft("Backups"):return
    mc=mc_dir();folder=os.path.join(mc,"villager_launcher_backups");os.makedirs(folder,exist_ok=True);target=os.path.join(folder,time.strftime("backup_%Y%m%d_%H%M%S.zip"))
    try:
        with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED) as a:
            for part in ("saves","mods","resourcepacks","config"):
                source=os.path.join(mc,part)
                if os.path.isdir(source):
                    for base,_,files in os.walk(source):
                        for n in files:a.write(os.path.join(base,n),os.path.relpath(os.path.join(base,n),mc))
        messagebox.showinfo("Backup Created","Minecraft backup created safely.\n\n"+target);render_backups()
    except OSError as e:messagebox.showerror("Backup Error",str(e))


def clear_content():
    for w in content.winfo_children():w.destroy()


def label(parent,text,size=10,bold=False,fg=None,bg=None):
    c=theme();return tk.Label(parent,text=text,font=(FONT,size,"bold" if bold else "normal"),bg=bg or c["panel"],fg=fg or c["fg"])


def btn(parent,text,command,accent=False):
    c=theme();return tk.Button(parent,text=text,command=command,font=(FONT,10,"bold"),relief="flat",bd=0,bg=c["accent"] if accent else c["button"],fg="white" if accent else c["fg"],activebackground=c["accent"],activeforeground="white",padx=16,pady=9,cursor="hand2")


def card(parent):return tk.Frame(parent,bg=theme()["card"],bd=0,highlightthickness=0)


def render_home():
    clear_content();c=theme();p=profiles[selected_profile]
    label(content,"Minecraft",28,True).pack(anchor="w",pady=(22,0));label(content,"Your Minecraft, Your Way.",13,False,c["muted"]).pack(anchor="w",pady=(2,18))
    hero=card(content);hero.pack(fill="x",pady=5);inner=tk.Frame(hero,bg=c["card"]);inner.pack(fill="x",padx=26,pady=24)
    info=tk.Frame(inner,bg=c["card"]);info.pack(side="left",fill="x",expand=True);label(info,p.get("name","Default"),20,True,bg=c["card"]).pack(anchor="w");label(info,(p.get("version") or "No version selected")+"  •  "+p.get("loader","Vanilla"),10,False,c["muted"],c["card"]).pack(anchor="w",pady=5)
    if ownership_verified():btn(inner,"PLAY",play_selected,True).pack(side="right",anchor="center")
    else:btn(inner,"LOCKED — OWN MINECRAFT",lambda:require_minecraft("Minecraft features")).pack(side="right",anchor="center")
    stats=tk.Frame(content,bg=c["panel"]);stats.pack(fill="x",pady=18)
    for title,value in (("Profiles",len(profiles)),("Versions",len(installed_versions())),("Mods",len(mod_files()))):
        box=card(stats);box.pack(side="left",fill="both",expand=True,padx=5);label(box,str(value) if ownership_verified() else "Locked",22,True,bg=c["card"]).pack(pady=(18,0));label(box,title,9,False,c["muted"],c["card"]).pack(pady=(2,18))
    news=card(content);news.pack(fill="x",pady=5);label(news,"VILLAGER LAUNCHER 1.7.0",12,True,bg=c["card"]).pack(anchor="w",padx=20,pady=(16,4));label(news,"Major Minecraft-style interface rebuild with 30+ themes and a full custom theme editor.",10,False,c["muted"],c["card"]).pack(anchor="w",padx=20,pady=(0,16))


def locked_page(title,text):
    clear_content();c=theme();label(content,title,26,True).pack(anchor="w",pady=(22,0));box=card(content);box.pack(fill="x",pady=18);label(box,"LOCKED",16,True,bg=c["card"]).pack(anchor="w",padx=22,pady=(22,5));label(box,text,10,False,c["muted"],c["card"]).pack(anchor="w",padx=22,pady=(0,22))


def render_profiles():
    if not ownership_verified():return locked_page("Profiles","Original Minecraft must be detected before profiles and PFPs can be used.")
    clear_content();c=theme();label(content,"Profiles",26,True).pack(anchor="w",pady=(22,0));label(content,"Manage Minecraft profiles and profile pictures.",11,False,c["muted"]).pack(anchor="w",pady=(3,18));btn(content,"+ NEW PROFILE",create_profile,True).pack(anchor="e",pady=(0,12))
    for i,p in enumerate(profiles):
        box=card(content);box.pack(fill="x",pady=5);inner=tk.Frame(box,bg=c["card"]);inner.pack(fill="x",padx=20,pady=15);image=load_pfp(p,54)
        if image:q=tk.Label(inner,image=image,bg=c["card"]);q.image=image;q.pack(side="left",padx=(0,16))
        else:tk.Label(inner,text="PFP",font=(FONT,9,"bold"),width=6,height=3,bg=c["button"],fg=c["muted"]).pack(side="left",padx=(0,16))
        info=tk.Frame(inner,bg=c["card"]);info.pack(side="left",fill="x",expand=True);label(info,p.get("name","Profile"),14,True,bg=c["card"]).pack(anchor="w");label(info,p.get("description") or "No description",9,False,c["muted"],c["card"]).pack(anchor="w",pady=2);btn(inner,"CHANGE PFP",lambda x=i:pick_pfp(x)).pack(side="right")


def render_mods():
    if not ownership_verified():return locked_page("Mods","Original Minecraft must be detected before mods can be managed.")
    clear_content();c=theme();label(content,"Mods",26,True).pack(anchor="w",pady=(22,0));label(content,"Manage installed Minecraft .jar mods.",11,False,c["muted"]).pack(anchor="w",pady=(3,18));btn(content,"+ IMPORT MODS",import_mod,True).pack(anchor="e",pady=(0,12));files=mod_files()
    if not files:label(content,"No .jar mods found in the Minecraft mods folder.",10,False,c["muted"]).pack(anchor="w")
    for n in files:
        box=card(content);box.pack(fill="x",pady=4);label(box,n,10,True,bg=c["card"]).pack(side="left",padx=18,pady=14);btn(box,"DISABLE",lambda x=n:disable_mod(x)).pack(side="right",padx=12,pady=7)


def render_versions():
    if not ownership_verified():return locked_page("Installations","Original Minecraft must be detected before installations can be managed.")
    clear_content();c=theme();label(content,"Installations",26,True).pack(anchor="w",pady=(22,0));label(content,"Minecraft versions installed in the selected data folder.",11,False,c["muted"]).pack(anchor="w",pady=(3,18));vs=installed_versions()
    if not vs:label(content,"No installed versions found.",10,False,c["muted"]).pack(anchor="w")
    for n in vs:
        box=card(content);box.pack(fill="x",pady=4);label(box,n,11,True,bg=c["card"]).pack(side="left",padx=18,pady=14);label(box,"Installed version",9,False,c["muted"],c["card"]).pack(side="left")


def render_backups():
    if not ownership_verified():return locked_page("Backups","Original Minecraft must be detected before backups can be created.")
    clear_content();c=theme();label(content,"Backups",26,True).pack(anchor="w",pady=(22,0));label(content,"Create safe ZIP backups of important Minecraft folders.",11,False,c["muted"]).pack(anchor="w",pady=(3,18));btn(content,"CREATE BACKUP",create_backup,True).pack(anchor="e",pady=(0,12));folder=os.path.join(mc_dir(),"villager_launcher_backups")
    if os.path.isdir(folder):
        for n in sorted(os.listdir(folder),reverse=True):
            if n.lower().endswith(".zip"):label(content,n,10,True).pack(anchor="w",pady=4)


def render_repair():
    clear_content();c=theme();label(content,"Repair",26,True).pack(anchor="w",pady=(22,0));label(content,"Diagnostics that never modify Minecraft files automatically.",11,False,c["muted"]).pack(anchor="w",pady=(3,18));box=card(content);box.pack(fill="x",pady=5);label(box,"Minecraft data folder",13,True,bg=c["card"]).pack(anchor="w",padx=22,pady=(20,4));label(box,mc_dir() or "Not available",10,False,c["muted"],c["card"]).pack(anchor="w",padx=22);label(box,"Official launcher evidence: "+("Detected" if ownership_verified() else "Not detected"),10,False,c["fg"],c["card"]).pack(anchor="w",padx=22,pady=(6,20))


def render_settings():
    clear_content();c=theme();label(content,"Settings",26,True).pack(anchor="w",pady=(22,0));label(content,"Customize the launcher without changing Minecraft files automatically.",11,False,c["muted"]).pack(anchor="w",pady=(3,18))
    box=card(content);box.pack(fill="x",pady=5);label(box,"Appearance",16,True,bg=c["card"]).pack(anchor="w",padx=22,pady=(20,12))
    r=tk.Frame(box,bg=c["card"]);r.pack(fill="x",padx=22,pady=5);label(r,"Theme",10,True,bg=c["card"]).pack(side="left");var=tk.StringVar(value=current_theme);menu=tk.OptionMenu(r,var,*list(THEMES.keys())+list(custom_themes.keys()),command=set_theme);menu.config(font=(FONT,9),bg=c["button"],fg=c["fg"],relief="flat",highlightthickness=0);menu.pack(side="right")
    actions=tk.Frame(box,bg=c["card"]);actions.pack(fill="x",padx=22,pady=8);btn(actions,"CREATE CUSTOM THEME",duplicate_theme,True).pack(side="left");
    if current_theme in custom_themes:btn(actions,"DELETE CURRENT",lambda:delete_custom_theme(current_theme)).pack(side="right")
    r=tk.Frame(box,bg=c["card"]);r.pack(fill="x",padx=22,pady=8);label(r,"UI density",10,True,bg=c["card"]).pack(side="left");dv=tk.StringVar(value=settings.get("ui_density","Comfortable"));om=tk.OptionMenu(r,dv,"Compact","Comfortable","Spacious",command=lambda v:(settings.__setitem__("ui_density",v),save_settings()));om.config(font=(FONT,9),bg=c["button"],fg=c["fg"],relief="flat",highlightthickness=0);om.pack(side="right")
    r=tk.Frame(box,bg=c["card"]);r.pack(fill="x",padx=22,pady=8);label(r,"Minecraft folder",10,True,bg=c["card"]).pack(side="left");label(r,settings.get("minecraft_path") or "Default .minecraft",9,False,c["muted"],c["card"]).pack(side="left",padx=15);btn(r,"CHOOSE",choose_mc).pack(side="right")
    r=tk.Frame(box,bg=c["card"]);r.pack(fill="x",padx=22,pady=8);label(r,"Java path",10,True,bg=c["card"]).pack(side="left");label(r,settings.get("java_path") or "Not set",9,False,c["muted"],c["card"]).pack(side="left",padx=15);btn(r,"CHOOSE",choose_java).pack(side="right")
    var1=tk.BooleanVar(value=bool(settings.get("confirm_updates",True)));var2=tk.BooleanVar(value=bool(settings.get("remember_window",True)))
    tk.Checkbutton(box,text="Ask before installing launcher updates",variable=var1,bg=c["card"],fg=c["fg"],selectcolor=c["button"],activebackground=c["card"],activeforeground=c["fg"],command=lambda:(settings.__setitem__("confirm_updates",var1.get()),save_settings())).pack(anchor="w",padx=18,pady=6)
    tk.Checkbutton(box,text="Remember launcher window size",variable=var2,bg=c["card"],fg=c["fg"],selectcolor=c["button"],activebackground=c["card"],activeforeground=c["fg"],command=lambda:(settings.__setitem__("remember_window",var2.get()),save_settings())).pack(anchor="w",padx=18,pady=2)
    btn(box,"RESET ALL SETTINGS",reset_settings).pack(anchor="e",padx=22,pady=18)
    u=card(content);u.pack(fill="x",pady=(15,5));label(u,"Updates",16,True,bg=c["card"]).pack(anchor="w",padx=22,pady=(18,8));label(u,"Updates are manual. Villager Launcher never installs an update automatically.",10,False,c["muted"],c["card"]).pack(anchor="w",padx=22,pady=(0,10));btn(u,"CHECK FOR UPDATES",check_updates,True).pack(anchor="e",padx=22,pady=(0,18))


def render_current(page):
    pages={"Home":render_home,"Profiles":render_profiles,"Mods":render_mods,"Installations":render_versions,"Versions":render_versions,"Backups":render_backups,"Repair":render_repair,"Settings":render_settings};pages.get(page,render_home)()
    for n,b in nav_buttons.items():b.configure(font=(FONT,10,"bold" if n==page else "normal"))


def build_ui():
    global content,status
    for w in root.winfo_children():w.destroy()
    c=theme();root.configure(bg=c["bg"]);root.title(f"Villager Launcher {CURRENT_VERSION}");root.geometry(f"{settings.get('window_width',1120)}x{settings.get('window_height',720)}");root.minsize(900,600)
    shell=tk.Frame(root,bg=c["bg"]);shell.pack(fill="both",expand=True);sidebar=tk.Frame(shell,bg=c["panel"],width=235);sidebar.pack(side="left",fill="y");sidebar.pack_propagate(False)
    tk.Label(sidebar,text="VILLAGER",font=(FONT,19,"bold"),bg=c["panel"],fg=c["fg"]).pack(anchor="w",padx=25,pady=(30,0));tk.Label(sidebar,text="LAUNCHER",font=(FONT,10,"bold"),bg=c["panel"],fg=c["accent"]).pack(anchor="w",padx=25,pady=(0,25))
    global nav_buttons;nav_buttons={};pages=["Home","Profiles","Mods","Installations","Backups","Repair","Settings"]
    for p in pages:
        b=tk.Button(sidebar,text=p,command=lambda x=p:render_current(x),font=(FONT,10),relief="flat",bd=0,bg=c["panel"],fg=c["fg"],activebackground=c["button"],activeforeground=c["fg"],anchor="w",padx=25,pady=12,cursor="hand2");b.pack(fill="x");nav_buttons[p]=b
    tk.Label(sidebar,text=f"Version {CURRENT_VERSION}",font=(FONT,8),bg=c["panel"],fg=c["muted"]).pack(side="bottom",anchor="w",padx=25,pady=20)
    main=tk.Frame(shell,bg=c["bg"]);main.pack(side="left",fill="both",expand=True);top=tk.Frame(main,bg=c["bg"]);top.pack(fill="x",padx=30,pady=(18,0));tk.Label(top,text="Villager Launcher",font=(FONT,10,"bold"),bg=c["bg"],fg=c["muted"]).pack(side="left")
    if profiles:
        image=load_pfp(profiles[selected_profile],44)
        if image:q=tk.Label(top,image=image,bg=c["bg"]);q.image=image;q.pack(side="right",padx=(0,12))
        else:tk.Label(top,text="PFP",font=(FONT,8,"bold"),width=5,height=2,bg=c["button"],fg=c["muted"]).pack(side="right",padx=(0,12))
    status=tk.Label(top,text="Ready",font=(FONT,9),bg=c["bg"],fg=c["muted"]);status.pack(side="right",padx=(0,15));content=tk.Frame(main,bg=c["panel"]);content.pack(fill="both",expand=True,padx=30,pady=12);render_current(settings.get("start_page","Home"))


def rebuild_ui():save_settings();build_ui()

def save_window():
    if root and settings.get("remember_window",True):
        try:settings["window_width"]=root.winfo_width();settings["window_height"]=root.winfo_height();save_settings()
        except tk.TclError:pass

load_settings();load_profiles()
if len(sys.argv)>=3 and sys.argv[1]=="--install-update":finish_update(sys.argv[2]);raise SystemExit
root=tk.Tk();build_ui();root.protocol("WM_DELETE_WINDOW",lambda:(save_window(),root.destroy()));root.mainloop()
