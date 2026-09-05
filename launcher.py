import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import json, os, sys, tempfile, subprocess, shutil, time, zipfile
from urllib.request import urlopen, Request

CURRENT_VERSION="1.7.1"
BASE_URL="https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main"
VERSION_URL=BASE_URL+"/version.json"; LAUNCHER_URL=BASE_URL+"/launcher.py"
APP_DIR=os.path.join(os.environ.get("APPDATA",tempfile.gettempdir()),"VillagerLauncher")
SETTINGS_FILE=os.path.join(APP_DIR,"settings.json"); PROFILES_FILE=os.path.join(APP_DIR,"profiles.json")
FONT="Segoe UI Variable"

# 30 built-in themes. Each keeps the same complete color model used by 1.7.0.
THEME_PALETTES={
"Villager Green":("#101810","#182418","#203020","#FFFFFF","#AFC3AF","#62C462","#2D442D","#B94A48"),"Midnight":("#0A0E18","#121827","#1A2338","#FFFFFF","#AAB6D3","#7188FF","#29365B","#D05B5B"),"Sky":("#DCEFF8","#F7FCFF","#EAF5FA","#173042","#5C7180","#3A91C9","#C7E0ED","#B64E4E"),"Nether":("#180C0C","#2A1212","#391919","#FFFFFF","#D0A8A8","#E05A5A","#542626","#FF8A70"),"Ocean":("#071820","#0D2833","#123743","#FFFFFF","#9FC5D0","#38A7C7","#1B4655","#D45D67"),"Dirt":("#24180F","#352416","#47301E","#FFF8EC","#C9B69D","#9B6B43","#60452C","#B94A48"),"Stone":("#202124","#2C2D30","#393A3D","#F5F5F5","#B9BABD","#A0A3A8","#4A4C50","#C65A5A"),"Diamond":("#071D24","#0D3038","#12404A","#F1FFFF","#9AC9CF","#59D8E4","#1C5962","#D35C68"),"Gold":("#211A06","#302707","#40360B","#FFFBEA","#D2C28A","#E8C84A","#5B4B13","#C45B45"),"Redstone":("#210B0B","#351010","#471818","#FFF5F5","#D5AAAA","#F04D4D","#641E1E","#FF7777"),"Lapis":("#08162B","#0D2140","#123058","#F4F8FF","#A5B9D5","#4C83D8","#1D4070","#D45D67"),"Amethyst":("#190D26","#28143A","#382052","#FFF7FF","#C5A9D5","#B66CDE","#513078","#E06A78"),"Copper":("#24130D","#382016","#4A2B1D","#FFF7F1","#D2B0A0","#D77B4D","#67402D","#C9584C"),"Forest":("#08170D","#102719","#183622","#F4FFF5","#A6C5AA","#55B96A","#245B32","#C75A55"),"Cherry Grove":("#260F1B","#3A1727","#4C2034","#FFF7FB","#D6ADBE","#F083B0","#6B2F4A","#E05D69"),"Desert":("#261E10","#382D18","#4A3C20","#FFFBEF","#D0C19B","#D6B45B","#66532B","#C55D4D"),"Snow":("#DDE8F0","#F4F9FC","#E7F0F6","#20313C","#647883","#5A9DC5","#C7DDE9","#B65353"),"Volcano":("#1D0905","#30100A","#45170E","#FFF8F0","#D4AAA0","#FF713F","#652416","#FF9B50"),"End":("#090610","#150D1E","#21132E","#FAF4FF","#BBA8C7","#B75BE8","#3D2052","#D75D7D"),"Piglin":("#2A1018","#3C1822","#51212D","#FFF4F5","#D7AEB5","#E6A06D","#6C3040","#F06A62"),"Swamp":("#111A0D","#1B2913","#26381A","#F5FFE9","#B5C59C","#86B84A","#3C5724","#C45C52"),"Plains":("#132014","#20351F","#2D4729","#F8FFF3","#B2C7A8","#8BC34A","#426332","#C85C55"),"Jungle":("#071A10","#0D2A19","#143923","#F2FFF5","#9FC5AA","#39C66A","#1D6038","#C45A5A"),"Ice":("#071A24","#0D2A38","#123A4B","#F2FCFF","#A4C7D2","#6DD6F2","#1E596B","#C65B68"),"Deep Dark":("#070B0E","#0D1318","#141E24","#E8FFFF","#91A8AD","#27D0C0","#173D3B","#C95762"),"Stronghold":("#151515","#202020","#2D2D2D","#F5F5F5","#B2B2B2","#C0C0C0","#444444","#C45A5A"),"Sunrise":("#24100C","#3A1A12","#4C2419","#FFF8F1","#D6B0A0","#FF9B5B","#6D3624","#D65D54"),"Night":("#050812","#0B1020","#121A2E","#F5F8FF","#9BAAC8","#6B8CFF","#25345E","#C85A6B"),"Redstone Lab":("#130D0C","#211514","#30201E","#FFF8F6","#C5A9A4","#FF4F38","#54241D","#FF8270"),"Creeper":("#0A1709","#11230E","#193515","#F5FFF0","#AAC59E","#69D34B","#2B5B20","#D05B55")}
THEMES={n:dict(zip(("bg","panel","card","fg","muted","accent","button","danger"),v)) for n,v in THEME_PALETTES.items()}
DEFAULT_SETTINGS={"theme":"Villager Green","remember_window":True,"window_width":1120,"window_height":720,"minecraft_path":"","java_path":"","confirm_updates":True,"start_page":"Home","ui_density":"Comfortable"}
settings=dict(DEFAULT_SETTINGS);profiles=[];selected_profile=0;current_theme="Villager Green";custom_themes={};root=None;content=None;status=None;nav_buttons={}

def load_json(path,default):
    try:
        with open(path,"r",encoding="utf-8") as f:return json.load(f)
    except (OSError,json.JSONDecodeError):return default

def save_settings():
    try:
        os.makedirs(APP_DIR,exist_ok=True);d=dict(settings);d["theme"]=current_theme;d["custom_themes"]=custom_themes
        with open(SETTINGS_FILE,"w",encoding="utf-8") as f:json.dump(d,f,indent=2)
    except OSError:pass

def load_settings():
    global settings,current_theme,custom_themes
    d=load_json(SETTINGS_FILE,{})
    if isinstance(d,dict):
        for k in DEFAULT_SETTINGS:
            if k in d:settings[k]=d[k]
        current_theme=d.get("theme",current_theme);custom_themes=d.get("custom_themes",{}) if isinstance(d.get("custom_themes",{}),dict) else {}

def save_profiles():
    try:
        os.makedirs(APP_DIR,exist_ok=True)
        with open(PROFILES_FILE,"w",encoding="utf-8") as f:json.dump(profiles,f,indent=2)
    except OSError:pass

def load_profiles():
    global profiles
    profiles=load_json(PROFILES_FILE,[])
    if not isinstance(profiles,list) or not profiles:
        profiles=[{"name":"Default","version":"","loader":"Vanilla","description":"Your first Villager Launcher profile.","pfile":""}];save_profiles()

def theme():return custom_themes.get(current_theme,THEMES.get(current_theme,THEMES["Villager Green"]))
def github_request(url,timeout=10):
    q="&" if "?" in url else "?";return urlopen(Request(url+q+"t="+str(time.time_ns()),headers={"User-Agent":"Villager-Launcher"}),timeout=timeout)
def latest_info():
    with github_request(VERSION_URL,5) as r:d=json.loads(r.read().decode())
    if not isinstance(d,dict) or not d.get("version"):raise ValueError("Version information is missing.")
    return d
def release_text(d):
    n=d.get("notes",{});return "\n\n".join(k.upper()+"\n"+"\n".join("• "+str(x) for x in n.get(k,[])) for k in ("Added","Changed","Removed","Fixed") if n.get(k)) or "No changes listed."
def download_update():
    with github_request(LAUNCHER_URL,15) as r:b=r.read()
    if not b:raise ValueError("Downloaded launcher is empty.")
    p=os.path.join(tempfile.gettempdir(),"villager_launcher_update.py");open(p,"wb").write(b);return p
def finish_update(target):
    src=os.path.abspath(sys.argv[0]);target=os.path.abspath(target);time.sleep(2)
    for _ in range(30):
        try:shutil.copy2(src,target);subprocess.Popen([sys.executable,target],close_fds=True);os.remove(src);return
        except OSError:time.sleep(1)
    messagebox.showerror("Update Error","Windows could not replace the launcher file.")
def install_update(p):
    subprocess.Popen([sys.executable,p,"--install-update",os.path.abspath(sys.argv[0])],creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0),close_fds=True);root.destroy()
def check_updates():
    try:
        status.config(text="Checking for updates...");d=latest_info();v=str(d["version"])
        if v==CURRENT_VERSION:status.config(text="Up to date");messagebox.showinfo("Updates",f"Villager Launcher is up to date!\n\nInstalled: {CURRENT_VERSION}\nServer: {v}");return
        if settings.get("confirm_updates",True) and not messagebox.askyesno("Update Available",f"Version {v} is available.\n\nWHAT'S NEW\n{release_text(d)}\n\nInstall now?"):return
        status.config(text="Installing update...");install_update(download_update())
    except Exception as e:status.config(text="Update failed");messagebox.showerror("Update Error",str(e))

def mc_dir():
    p=settings.get("minecraft_path","")
    if p and os.path.isdir(p):return p
    a=os.environ.get("APPDATA");return os.path.join(a,".minecraft") if a else None
def ownership_verified():
    f=mc_dir();return bool(f and os.path.isdir(f) and (os.path.isfile(os.path.join(f,"launcher_accounts.json")) or os.path.isfile(os.path.join(f,"launcher_profiles.json"))))
def require_minecraft(feature):
    if ownership_verified():return True
    messagebox.showwarning("Minecraft Required",f"{feature} is locked until an original Minecraft installation is detected.\n\nSign in through the official Minecraft launcher and select its Minecraft data folder in Villager Launcher Settings.");return False
def installed_versions():
    f=os.path.join(mc_dir(),"versions") if mc_dir() else ""
    try:return sorted(os.listdir(f),reverse=True) if os.path.isdir(f) else []
    except OSError:return []
def mod_files():
    f=os.path.join(mc_dir(),"mods") if mc_dir() else ""
    try:return sorted(x for x in os.listdir(f) if x.lower().endswith(".jar")) if os.path.isdir(f) else []
    except OSError:return []
def load_pfp(p,size):
    f=p.get("pfile","")
    if not f or not os.path.isfile(f):return None
    try:
        im=tk.PhotoImage(file=f);q=max(1,int(max(im.width(),im.height())/size));return im.subsample(q,q) if q>1 else im
    except tk.TclError:return None
def pick_pfp(i):
    if not require_minecraft("Profile pictures"):return
    f=filedialog.askopenfilename(title="Choose profile picture",filetypes=[("PNG images","*.png"),("GIF images","*.gif"),("BMP images","*.bmp")])
    if f:profiles[i]["pfile"]=f;save_profiles();rebuild_ui()
def create_profile():
    if not require_minecraft("Profiles"):return
    w=tk.Toplevel(root);w.title("New Profile");w.geometry("430x180");w.configure(bg=theme()["panel"]);w.grab_set();label(w,"Profile name",11,True).pack(anchor="w",padx=25,pady=(25,8));e=tk.Entry(w,font=(FONT,11));e.pack(fill="x",padx=25);e.focus_set()
    def done():
        n=e.get().strip()
        if n:profiles.append({"name":n,"version":"","loader":"Vanilla","description":"","pfile":""});save_profiles();w.destroy();rebuild_ui()
    btn(w,"CREATE",done,True).pack(anchor="e",padx=25,pady=18)
def choose_mc():
    p=filedialog.askdirectory(title="Choose Minecraft folder")
    if p:settings["minecraft_path"]=p;save_settings();render_settings()
def choose_java():
    p=filedialog.askopenfilename(title="Choose Java executable",filetypes=[("Java executable","java.exe"),("All files","*.*")])
    if p:settings["java_path"]=p;save_settings();render_settings()
def set_theme(n):
    global current_theme
    if n in THEMES or n in custom_themes:current_theme=n;save_settings();rebuild_ui()
def pick_color(v):
    c=colorchooser.askcolor(title="Choose theme color",initialcolor=v.get())[1]
    if c:v.set(c)
def custom_theme_editor():
    base=theme();w=tk.Toplevel(root);w.title("Custom Theme Editor");w.geometry("570x590");w.configure(bg=base["panel"]);w.grab_set();wrap=tk.Frame(w,bg=base["panel"]);wrap.pack(fill="both",expand=True,padx=24,pady=20);label(wrap,"CUSTOM THEME EDITOR",18,True).pack(anchor="w");label(wrap,"Create a theme without changing the built-in themes.",10,False,base["muted"]).pack(anchor="w",pady=(2,14));name=tk.StringVar(value=current_theme+" Copy");r=tk.Frame(wrap,bg=base["panel"]);r.pack(fill="x");label(r,"Theme name",9,True).pack(side="left");tk.Entry(r,textvariable=name).pack(side="left",fill="x",expand=True,padx=15);fields={};prev=tk.Frame(wrap,bg=base["card"]);prev.pack(fill="x",pady=12)
    keys=["bg","panel","card","fg","muted","accent","button","danger"]
    for k in keys:
        rr=tk.Frame(wrap,bg=base["panel"]);rr.pack(fill="x",pady=2);label(rr,k.upper(),9,True).pack(side="left",fill="x",expand=True);fields[k]=tk.StringVar(value=base[k]);tk.Entry(rr,textvariable=fields[k],width=12).pack(side="left");tk.Button(rr,text="COLOR",command=lambda v=fields[k]:pick_color(v)).pack(side="right")
    def save():
        n=name.get().strip() or "My Theme";d={k:v.get().strip() for k,v in fields.items()}
        if any(len(x)!=7 or not x.startswith("#") for x in d.values()):messagebox.showerror("Theme Error","Use colors like #62C462.",parent=w);return
        custom_themes[n]=d;globals()["current_theme"]=n;save_settings();w.destroy();rebuild_ui()
    tk.Button(wrap,text="SAVE THEME",command=save).pack(anchor="e",pady=12)
def reset_settings():
    global settings,current_theme,custom_themes
    if messagebox.askyesno("Reset Settings","Reset launcher settings? Minecraft files and profiles will not be deleted."):settings=dict(DEFAULT_SETTINGS);current_theme="Villager Green";custom_themes={};save_settings();rebuild_ui()
def play_selected():
    if require_minecraft("Minecraft launching"):messagebox.showinfo("Minecraft","Original Minecraft installation detected.\n\nLaunch integration will be enabled in a future release.")
def import_mod():
    if not require_minecraft("Mods"):return
    fs=filedialog.askopenfilenames(title="Import Minecraft mods",filetypes=[("Minecraft mods","*.jar")]);folder=os.path.join(mc_dir(),"mods")
    if fs:
        try:os.makedirs(folder,exist_ok=True);[shutil.copy2(x,os.path.join(folder,os.path.basename(x))) for x in fs];render_mods()
        except OSError as e:messagebox.showerror("Mod Error",str(e))
def create_backup():
    if not require_minecraft("Backups"):return
    mc=mc_dir();folder=os.path.join(mc,"villager_launcher_backups");os.makedirs(folder,exist_ok=True);target=os.path.join(folder,time.strftime("backup_%Y%m%d_%H%M%S.zip"))
    try:
        with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED) as z:
            for part in ("saves","mods","resourcepacks","config"):
                s=os.path.join(mc,part)
                if os.path.isdir(s):
                    for base,_,files in os.walk(s):
                        for n in files:z.write(os.path.join(base,n),os.path.relpath(os.path.join(base,n),mc))
        messagebox.showinfo("Backup Created","Minecraft backup created safely.\n\n"+target);render_settings()
    except OSError as e:messagebox.showerror("Backup Error",str(e))
def clear():
    for w in content.winfo_children():w.destroy()
def label(p,t,size=10,bold=False,fg=None,bg=None):
    c=theme();return tk.Label(p,text=t,font=(FONT,size,"bold" if bold else "normal"),bg=bg or c["panel"],fg=fg or c["fg"])
def btn(p,t,cmd,accent=False):
    c=theme();return tk.Button(p,text=t,command=cmd,font=(FONT,10,"bold"),relief="flat",bd=0,bg=c["accent"] if accent else c["button"],fg="white" if accent else c["fg"],activebackground=c["accent"],activeforeground="white",padx=16,pady=9,cursor="hand2")
def card(p):return tk.Frame(p,bg=theme()["card"],bd=0,highlightthickness=0)
def locked_page(t,msg):
    clear();c=theme();label(content,t,26,True).pack(anchor="w",pady=(22,0));b=card(content);b.pack(fill="x",pady=18);label(b,"LOCKED",16,True,bg=c["card"]).pack(anchor="w",padx=22,pady=(22,5));label(b,msg,10,False,c["muted"],c["card"]).pack(anchor="w",padx=22,pady=(0,22))
def render_home():
    clear();c=theme();p=profiles[selected_profile];label(content,"Minecraft",28,True).pack(anchor="w",pady=(22,0));label(content,"Your Minecraft, Your Way.",13,False,c["muted"]).pack(anchor="w",pady=(2,18));h=card(content);h.pack(fill="x",pady=5);i=tk.Frame(h,bg=c["card"]);i.pack(fill="x",padx=26,pady=24);label(i,p.get("name","Default"),20,True,bg=c["card"]).pack(anchor="w");label(i,(p.get("version") or "No version selected")+"  •  "+p.get("loader","Vanilla"),10,False,c["muted"],c["card"]).pack(anchor="w",pady=5);btn(i,"PLAY",play_selected,True).pack(side="right",anchor="center") if ownership_verified() else btn(i,"LOCKED — OWN MINECRAFT",lambda:require_minecraft("Minecraft features")).pack(side="right",anchor="center")
    s=tk.Frame(content,bg=c["panel"]);s.pack(fill="x",pady=18)
    for a,v in (("Profiles",len(profiles)),("Versions",len(installed_versions())),("Mods",len(mod_files()))):
        b=card(s);b.pack(side="left",fill="both",expand=True,padx=5);label(b,str(v) if ownership_verified() else "Locked",22,True,bg=c["card"]).pack(pady=(18,0));label(b,a,9,False,c["muted"],c["card"]).pack(pady=(2,18))
def render_profiles():
    if not ownership_verified():return locked_page("Profiles","Original Minecraft must be detected before profiles and PFPs can be used.")
    clear();c=theme();label(content,"Profiles",26,True).pack(anchor="w",pady=(22,0));label(content,"Manage Minecraft profiles and profile pictures.",11,False,c["muted"]).pack(anchor="w",pady=(3,18));btn(content,"+ NEW PROFILE",create_profile,True).pack(anchor="e",pady=(0,12))
    for i,p in enumerate(profiles):
        b=card(content);b.pack(fill="x",pady=5);q=tk.Frame(b,bg=c["card"]);q.pack(fill="x",padx=20,pady=15);im=load_pfp(p,54)
        if im:x=tk.Label(q,image=im,bg=c["card"]);x.image=im;x.pack(side="left",padx=(0,16))
        else:tk.Label(q,text="PFP",width=6,height=3,bg=c["button"],fg=c["muted"]).pack(side="left",padx=(0,16))
        label(q,p.get("name","Profile"),14,True,bg=c["card"]).pack(side="left");btn(q,"CHANGE PFP",lambda x=i:pick_pfp(x)).pack(side="right")
def render_mods():
    if not ownership_verified():return locked_page("Mods","Original Minecraft must be detected before mods can be managed.")
    clear();c=theme();label(content,"Mods",26,True).pack(anchor="w",pady=(22,0));label(content,"Manage installed Minecraft .jar mods.",11,False,c["muted"]).pack(anchor="w",pady=(3,18));btn(content,"+ IMPORT MODS",import_mod,True).pack(anchor="e",pady=(0,12));fs=mod_files()
    if not fs:label(content,"No .jar mods found in the Minecraft mods folder.",10,False,c["muted"]).pack(anchor="w")
    for n in fs:label(content,n,10,True).pack(anchor="w",pady=4)
def render_versions():
    if not ownership_verified():return locked_page("Installations","Original Minecraft must be detected before installations can be managed.")
    clear();c=theme();label(content,"Installations",26,True).pack(anchor="w",pady=(22,0));label(content,"Minecraft versions installed in the selected data folder.",11,False,c["muted"]).pack(anchor="w",pady=(3,18));vs=installed_versions()
    if not vs:label(content,"No installed versions found.",10,False,c["muted"]).pack(anchor="w")
    for n in vs:label(content,n,11,True).pack(anchor="w",pady=4)
def render_repair():
    clear();c=theme();label(content,"Repair",26,True).pack(anchor="w",pady=(22,0));label(content,"Diagnostics that never modify Minecraft files automatically.",11,False,c["muted"]).pack(anchor="w",pady=(3,18));b=card(content);b.pack(fill="x",pady=5);label(b,"Minecraft data folder",13,True,bg=c["card"]).pack(anchor="w",padx=22,pady=(20,4));label(b,mc_dir() or "Not available",10,False,c["muted"],c["card"]).pack(anchor="w",padx=22);label(b,"Official launcher evidence: "+("Detected" if ownership_verified() else "Not detected"),10,False,bg=c["card"]).pack(anchor="w",padx=22,pady=(6,20))
def render_settings():
    clear();c=theme();label(content,"Settings",26,True).pack(anchor="w",pady=(22,0));label(content,"Launcher preferences, updates, backups, Minecraft paths, and appearance.",11,False,c["muted"]).pack(anchor="w",pady=(3,18))
    a=card(content);a.pack(fill="x",pady=5);label(a,"Appearance",16,True,bg=c["card"]).pack(anchor="w",padx=22,pady=(18,10));r=tk.Frame(a,bg=c["card"]);r.pack(fill="x",padx=22,pady=5);label(r,"Theme",10,True,bg=c["card"]).pack(side="left");v=tk.StringVar(value=current_theme);m=tk.OptionMenu(r,v,*list(THEMES)+list(custom_themes),command=set_theme);m.config(bg=c["button"],fg=c["fg"],relief="flat");m.pack(side="right");btn(a,"CREATE CUSTOM THEME",custom_theme_editor,True).pack(anchor="w",padx=22,pady=10);r=tk.Frame(a,bg=c["card"]);r.pack(fill="x",padx=22,pady=6);label(r,"UI density",10,True,bg=c["card"]).pack(side="left");dv=tk.StringVar(value=settings.get("ui_density","Comfortable"));om=tk.OptionMenu(r,dv,"Compact","Comfortable","Spacious",command=lambda x:(settings.__setitem__("ui_density",x),save_settings()));om.config(bg=c["button"],fg=c["fg"],relief="flat");om.pack(side="right")
    mbox=card(content);mbox.pack(fill="x",pady=(14,5));label(mbox,"MINECRAFT",16,True,bg=c["card"]).pack(anchor="w",padx=22,pady=(18,8));r=tk.Frame(mbox,bg=c["card"]);r.pack(fill="x",padx=22,pady=6);label(r,"Minecraft folder",10,True,bg=c["card"]).pack(side="left");label(r,settings.get("minecraft_path") or "Default .minecraft",9,False,c["muted"],c["card"]).pack(side="left",padx=15);btn(r,"CHOOSE",choose_mc).pack(side="right")
    r=tk.Frame(mbox,bg=c["card"]);r.pack(fill="x",padx=22,pady=6);label(r,"Java path",10,True,bg=c["card"]).pack(side="left");label(r,settings.get("java_path") or "Not set",9,False,c["muted"],c["card"]).pack(side="left",padx=15);btn(r,"CHOOSE",choose_java).pack(side="right")
    b=card(content);b.pack(fill="x",pady=(14,5));label(b,"BACKUPS",16,True,bg=c["card"]).pack(anchor="w",padx=22,pady=(18,5));label(b,"Backups are now managed entirely from Settings.",10,False,c["muted"],c["card"]).pack(anchor="w",padx=22,pady=(0,10));btn(b,"CREATE BACKUP",create_backup,True).pack(anchor="w",padx=22,pady=5);folder=os.path.join(mc_dir(),"villager_launcher_backups") if mc_dir() else "";names=sorted([x for x in os.listdir(folder) if x.endswith(".zip")],reverse=True) if os.path.isdir(folder) else [];label(b,("No backups created yet." if not names else "\n".join(names)),9,False,c["muted"],c["card"]).pack(anchor="w",padx=22,pady=(4,16))
    u=card(content);u.pack(fill="x",pady=(14,5));label(u,"UPDATES",16,True,bg=c["card"]).pack(anchor="w",padx=22,pady=(18,5));label(u,"Updates are manual. Nothing installs automatically.",10,False,c["muted"],c["card"]).pack(anchor="w",padx=22,pady=(0,10));btn(u,"CHECK FOR UPDATES",check_updates,True).pack(anchor="w",padx=22,pady=(0,18));btn(content,"RESET ALL SETTINGS",reset_settings).pack(anchor="e",pady=15)
def render_current(page):
    pages={"Home":render_home,"Profiles":render_profiles,"Mods":render_mods,"Installations":render_versions,"Versions":render_versions,"Repair":render_repair,"Settings":render_settings};pages.get(page,render_home)();
    for n,b in nav_buttons.items():b.configure(font=(FONT,10,"bold" if n==page else "normal"))
def build_ui():
    global content,status,nav_buttons
    for w in root.winfo_children():w.destroy()
    c=theme();root.configure(bg=c["bg"]);root.title(f"Villager Launcher {CURRENT_VERSION}");root.geometry(f"{settings.get('window_width',1120)}x{settings.get('window_height',720)}");root.minsize(900,600);shell=tk.Frame(root,bg=c["bg"]);shell.pack(fill="both",expand=True);side=tk.Frame(shell,bg=c["panel"],width=235);side.pack(side="left",fill="y");side.pack_propagate(False);tk.Label(side,text="VILLAGER",font=(FONT,19,"bold"),bg=c["panel"],fg=c["fg"]).pack(anchor="w",padx=25,pady=(30,0));tk.Label(side,text="LAUNCHER",font=(FONT,10,"bold"),bg=c["panel"],fg=c["accent"]).pack(anchor="w",padx=25,pady=(0,25));nav_buttons={};pages=["Home","Profiles","Mods","Installations","Repair","Settings"]
    for p in pages:
        b=tk.Button(side,text=p,command=lambda x=p:render_current(x),font=(FONT,10),relief="flat",bd=0,bg=c["panel"],fg=c["fg"],activebackground=c["button"],activeforeground=c["fg"],anchor="w",padx=25,pady=12,cursor="hand2");b.pack(fill="x");nav_buttons[p]=b
    tk.Label(side,text=f"Version {CURRENT_VERSION}",font=(FONT,8),bg=c["panel"],fg=c["muted"]).pack(side="bottom",anchor="w",padx=25,pady=20);main=tk.Frame(shell,bg=c["bg"]);main.pack(side="left",fill="both",expand=True);top=tk.Frame(main,bg=c["bg"]);top.pack(fill="x",padx=30,pady=(18,0));tk.Label(top,text="Villager Launcher",font=(FONT,10,"bold"),bg=c["bg"],fg=c["muted"]).pack(side="left");im=load_pfp(profiles[selected_profile],44)
    if im:q=tk.Label(top,image=im,bg=c["bg"]);q.image=im;q.pack(side="right",padx=(0,12))
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
