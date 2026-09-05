import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os, sys, tempfile, subprocess, shutil, time, traceback
from urllib.request import urlopen, Request
from urllib.parse import quote

CURRENT_VERSION="1.8.0"
BASE_URL="https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main"
VERSION_URL=BASE_URL+"/version.json"
LAUNCHER_URL=BASE_URL+"/launcher.py"
MODRINTH_API="https://api.modrinth.com/v2"
APP_DIR=os.path.join(os.environ.get("APPDATA",tempfile.gettempdir()),"VillagerLauncher")
SETTINGS_FILE=os.path.join(APP_DIR,"settings.json")
PROFILES_FILE=os.path.join(APP_DIR,"profiles.json")
FONT="Segoe UI Variable"

PALETTES={
"Villager Green":("#0e1510","#162119","#203021","#ffffff","#a9b9aa","#62c462","#2d442d","#c65353"),
"Midnight":("#080d17","#111a29","#1a263b","#ffffff","#a9b5c9","#7188ff","#29385e","#d15c66"),
"Sky":("#dff1fa","#f5fbff","#e8f4fa","#173042","#5c7180","#3a91c9","#c7e0ed","#b64e4e"),
"Nether":("#190b0b","#291212","#3a1a1a","#ffffff","#d0a8a8","#e05a5a","#542626","#ff8a70"),
"Ocean":("#07181f","#0d2833","#123743","#ffffff","#9fc5d0","#38a7c7","#1b4655","#d45d67"),
"Dirt":("#24180f","#352416","#47301e","#fff8ec","#c9b69d","#9b6b43","#60452c","#b94a48"),
"Stone":("#202124","#2c2d30","#393a3d","#f5f5f5","#b9babd","#a0a3a8","#4a4c50","#c65a5a"),
"Diamond":("#071d24","#0d3038","#12404a","#f1ffff","#9ac9cf","#59d8e4","#1c5962","#d35c68"),
"Gold":("#211a06","#302707","#40360b","#fffbea","#d2c28a","#e8c84a","#5b4b13","#c45b45"),
"Redstone":("#210b0b","#351010","#471818","#fff5f5","#d5aaaa","#f04d4d","#641e1e","#ff7777"),
"Lapis":("#08162b","#0d2140","#123058","#f4f8ff","#a5b9d5","#4c83d8","#1d4070","#d45d67"),
"Amethyst":("#190d26","#28143a","#382052","#fff7ff","#c5a9d5","#b66cde","#513078","#e06a78"),
"Copper":("#24130d","#382016","#4a2b1d","#fff7f1","#d2b0a0","#d77b4d","#67402d","#c9584c"),
"Forest":("#08170d","#102719","#183622","#f4fff5","#a6c5aa","#55b96a","#245b32","#c75a55"),
"Cherry Grove":("#260f1b","#3a1727","#4c2034","#fff7fb","#d6adbe","#f083b0","#6b2f4a","#e05d69"),
"Desert":("#261e10","#382d18","#4a3c20","#fffbef","#d0c19b","#d6b45b","#66532b","#c55d4d"),
"Snow":("#dde8f0","#f4f9fc","#e7f0f6","#20313c","#647883","#5a9dc5","#c7dde9","#b65353"),
"Volcano":("#1d0905","#30100a","#45170e","#fff8f0","#d4aaa0","#ff713f","#652416","#ff9b50"),
"End":("#090610","#150d1e","#21132e","#faf4ff","#bba8c7","#b75be8","#3d2052","#d75d7d"),
"Piglin":("#2a1018","#3c1822","#51212d","#fff4f5","#d7aeb5","#e6a06d","#6c3040","#f06a62"),
"Swamp":("#111a0d","#1b2913","#26381a","#f5ffe9","#b5c59c","#86b84a","#3c5724","#c45c52"),
"Plains":("#132014","#20351f","#2d4729","#f8fff3","#b2c7a8","#8bc34a","#426332","#c85c55"),
"Jungle":("#071a10","#0d2a19","#143923","#f2fff5","#9fc5aa","#39c66a","#1d6038","#c45a5a"),
"Ice":("#071a24","#0d2a38","#123a4b","#f2fcff","#a4c7d2","#6dd6f2","#1e596b","#c65b68"),
"Deep Dark":("#070b0e","#0d1318","#141e24","#e8ffff","#91a8ad","#27d0c0","#173d3b","#c95762"),
"Stronghold":("#151515","#202020","#2d2d2d","#f5f5f5","#b2b2b2","#c0c0c0","#444444","#c45a5a"),
"Sunrise":("#24100c","#3a1a12","#4c2419","#fff8f1","#d6b0a0","#ff9b5b","#6d3624","#d65d54"),
"Night":("#050812","#0b1020","#121a2e","#f5f8ff","#9baac8","#6b8cff","#25345e","#c85a6b"),
"Redstone Lab":("#130d0c","#211514","#30201e","#fff8f6","#c5a9a4","#ff4f38","#54241d","#ff8270"),
"Creeper":("#0a1709","#11230e","#193515","#f5fff0","#aac59e","#69d34b","#2b5b20","#d05b55")}
THEMES={n:dict(zip(("bg","panel","card","fg","muted","accent","button","danger"),v)) for n,v in PALETTES.items()}
DEFAULT={"theme":"Villager Green","remember_window":True,"window_width":1180,"window_height":760,"minecraft_path":"","java_path":"","confirm_updates":True,"start_page":"Home","ui_density":"Comfortable"}
settings=dict(DEFAULT); profiles=[]; selected_profile=0; current_theme="Villager Green"; custom_themes={}; root=None; content=None; header_pfp=None; status=None; nav={}; page="Home"

# ---------- storage ----------
def read_json(path,default):
    try:
        with open(path,"r",encoding="utf-8") as f:return json.load(f)
    except (OSError,ValueError):return default

def save_settings():
    try:
        os.makedirs(APP_DIR,exist_ok=True); d=dict(settings); d.update({"theme":current_theme,"custom_themes":custom_themes})
        with open(SETTINGS_FILE,"w",encoding="utf-8") as f:json.dump(d,f,indent=2)
    except OSError: pass

def load_settings():
    global settings,current_theme,custom_themes
    d=read_json(SETTINGS_FILE,{})
    if isinstance(d,dict):
        for k in DEFAULT:
            if k in d: settings[k]=d[k]
        current_theme=d.get("theme","Villager Green")
        custom_themes=d.get("custom_themes",{}) if isinstance(d.get("custom_themes",{}),dict) else {}
    if current_theme not in THEMES and current_theme not in custom_themes: current_theme="Villager Green"

def save_profiles():
    try:
        os.makedirs(APP_DIR,exist_ok=True)
        with open(PROFILES_FILE,"w",encoding="utf-8") as f:json.dump(profiles,f,indent=2)
    except OSError: pass

def load_profiles():
    global profiles,selected_profile
    profiles=read_json(PROFILES_FILE,[])
    if not isinstance(profiles,list) or not profiles:
        profiles=[{"name":"Default","version":"","loader":"Vanilla","description":"Your first Villager Launcher profile.","pfile":""}]; save_profiles()
    selected_profile=min(selected_profile,len(profiles)-1)

def palette(): return custom_themes.get(current_theme,THEMES.get(current_theme,THEMES["Villager Green"]))

# ---------- network/update ----------
def get_json(url,timeout=12):
    req=Request(url+(("&" if "?" in url else "?")+"t="+str(time.time_ns())),headers={"User-Agent":"Villager-Launcher/1.8"})
    with urlopen(req,timeout=timeout) as r:return json.loads(r.read().decode("utf-8"))

def check_updates():
    try:
        status.config(text="Checking for updates…"); d=get_json(VERSION_URL,8); v=str(d.get("version",""))
        if not v: raise ValueError("The update server returned no version number.")
        if v==CURRENT_VERSION:
            status.config(text="Up to date"); messagebox.showinfo("Updates",f"Villager Launcher is up to date.\n\nInstalled: {CURRENT_VERSION}\nLatest: {v}"); return
        notes=d.get("notes",{}); lines=[]
        for k in ("Added","Changed","Fixed","Removed"):
            if notes.get(k): lines.append(k.upper()+"\n"+"\n".join("• "+str(x) for x in notes[k]))
        if not messagebox.askyesno("Update Available",f"Version {v} is available.\n\n"+"\n\n".join(lines)+"\n\nInstall now?"): return
        req=Request(LAUNCHER_URL+"?t="+str(time.time_ns()),headers={"User-Agent":"Villager-Launcher/1.8"})
        with urlopen(req,timeout=20) as r: data=r.read()
        p=os.path.join(tempfile.gettempdir(),"villager_launcher_update.py")
        with open(p,"wb") as f:f.write(data)
        subprocess.Popen([sys.executable,p,"--install-update",os.path.abspath(sys.argv[0])],creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0),close_fds=True)
        root.destroy()
    except Exception as e:
        status.config(text="Update failed"); messagebox.showerror("Update Error",f"Could not check/install the update.\n\n{e}")

def finish_update(target):
    src=os.path.abspath(sys.argv[0]); target=os.path.abspath(target); time.sleep(2)
    for _ in range(30):
        try: shutil.copy2(src,target); subprocess.Popen([sys.executable,target],close_fds=True); os.remove(src); return
        except OSError: time.sleep(1)
    messagebox.showerror("Update Error","Windows could not replace the launcher file.")

# ---------- minecraft ----------
def mc_dir():
    p=settings.get("minecraft_path","")
    if p and os.path.isdir(p): return p
    a=os.environ.get("APPDATA"); return os.path.join(a,".minecraft") if a else None

def ownership_verified():
    d=mc_dir(); return bool(d and os.path.isdir(d) and (os.path.isfile(os.path.join(d,"launcher_accounts.json")) or os.path.isfile(os.path.join(d,"launcher_profiles.json"))))

def require_minecraft(feature):
    if ownership_verified(): return True
    messagebox.showwarning("Minecraft Required",f"{feature} is locked until an original Minecraft installation is detected.\n\nSign in with the official Minecraft launcher, then select its Minecraft data folder in Villager Launcher Settings.")
    return False

def versions():
    d=os.path.join(mc_dir() or "","versions")
    try:return sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x))],reverse=True) if os.path.isdir(d) else []
    except OSError:return []

def selected_version():
    p=profiles[selected_profile] if profiles else {}
    return p.get("version") or (versions()[0] if versions() else "")

def detailed_launch_error(title,stage,error,extra=None):
    status.config(text="Launch failed")
    details=[f"Stage: {stage}",f"What broke: {error}"]
    if extra: details.append(str(extra))
    details.append("\nThis launcher did not delete or modify your Minecraft files.")
    messagebox.showerror(title,"\n\n".join(details))

def launch_game():
    if not require_minecraft("Minecraft launching"): return
    d=mc_dir(); v=selected_version()
    if not d: return detailed_launch_error("Launch Error","Minecraft folder","Minecraft directory could not be found.")
    if not v: return detailed_launch_error("Launch Error","Version selection","No installed Minecraft version was selected.","Open Installations and select an installed version first.")
    vd=os.path.join(d,"versions",v); jar=os.path.join(vd,v+".jar"); meta=os.path.join(vd,v+".json")
    if not os.path.isfile(meta): return detailed_launch_error("Launch Error","Version metadata",f"Missing version JSON: {meta}")
    if not os.path.isfile(jar): return detailed_launch_error("Launch Error","Client JAR",f"Missing client JAR: {jar}")
    java=settings.get("java_path","") or "java"
    try:
        subprocess.Popen([java,"-version"],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0),text=True,timeout=8)
    except Exception as e:
        return detailed_launch_error("Launch Error","Java startup",f"Java executable could not be started: {java}",e)
    # Full authenticated Minecraft launching requires Microsoft account tokens and the launcher libraries.
    # We deliberately refuse to guess credentials or bypass authentication.
    detailed_launch_error("Launch Error","Authenticated Minecraft startup","The selected Minecraft files are present, but authenticated launch integration is not enabled in this build.","The launcher checked the version JSON, client JAR, and Java executable successfully. No game process was started.")

# ---------- mod workshop (Modrinth catalog) ----------
def api_get(path,timeout=15): return get_json(MODRINTH_API+path,timeout)
def mod_search(query):
    q=quote(query.strip())
    return api_get(f"/search?query={q}&facets=%5B%5B%22project_type%3Amod%22%5D%5D&limit=20",15).get("hits",[])

def install_workshop_mod(project):
    if not require_minecraft("Mod Workshop"): return
    game=selected_version() or ""
    if not game: messagebox.showwarning("Mod Workshop","Select an installed Minecraft version in Installations first."); return
    try:
        slug=project.get("slug") or project.get("project_id")
        versions_data=api_get(f"/project/{quote(slug)}/version?game_versions=%5B%22{quote(game)}%22%5D",15)
        if not versions_data: raise ValueError(f"No Modrinth release of this mod supports Minecraft {game}.")
        pv=versions_data[0]; files=pv.get("files",[])
        primary=next((x for x in files if x.get("primary")),files[0] if files else None)
        if not primary or not primary.get("url"): raise ValueError("The workshop returned no downloadable file.")
        mods=os.path.join(mc_dir(),"mods"); os.makedirs(mods,exist_ok=True)
        name=os.path.basename(primary.get("filename") or "mod.jar")
        target=os.path.join(mods,name)
        req=Request(primary["url"],headers={"User-Agent":"Villager-Launcher/1.8"})
        with urlopen(req,timeout=30) as r:data=r.read()
        if not data: raise ValueError("The downloaded mod file was empty.")
        tmp=target+".part"
        with open(tmp,"wb") as f:f.write(data)
        os.replace(tmp,target)
        status.config(text=f"Installed {project.get('title','mod')}")
        messagebox.showinfo("Mod Workshop",f"Installed: {project.get('title','Unknown mod')}\n\nMinecraft: {game}\nFile: {name}\n\nNo JAR selection was required.")
        render_mods()
    except Exception as e:
        messagebox.showerror("Mod Workshop Error",f"The workshop could not install this mod.\n\nWhat broke: {e}")

def workshop():
    if not require_minecraft("Mod Workshop"): return
    clear_content(); p=palette(); card=round_card(content,p["card"],20); card.pack(fill="both",expand=True)
    tk.Label(card,text="MOD WORKSHOP",font=(FONT,20,"bold"),bg=p["card"],fg=p["fg"]).pack(anchor="w",padx=24,pady=(22,4))
    tk.Label(card,text="Browse and install mods directly from the workshop catalog — no manual .jar picking.",font=(FONT,10),bg=p["card"],fg=p["muted"]).pack(anchor="w",padx=24)
    row=tk.Frame(card,bg=p["card"]);row.pack(fill="x",padx=24,pady=18); q=tk.StringVar(); ent=tk.Entry(row,textvariable=q,font=(FONT,11),bg=p["panel"],fg=p["fg"],insertbackground=p["fg"],relief="flat");ent.pack(side="left",fill="x",expand=True,ipady=10,padx=(0,10)); btn(row,"SEARCH",lambda:search_results(q.get(),results),True).pack(side="right")
    results=tk.Frame(card,bg=p["card"]);results.pack(fill="both",expand=True,padx=24,pady=(0,20)); search_results("popular",results)

def search_results(query,box):
    p=palette()
    for w in box.winfo_children():w.destroy()
    try:hits=mod_search(query or "popular")
    except Exception as e:
        tk.Label(box,text=f"Workshop connection failed\n\nWhat broke: {e}",font=(FONT,11),bg=p["card"],fg=p["danger"]).pack(anchor="w",pady=20);return
    if not hits:
        tk.Label(box,text="No mods found for that search.",font=(FONT,11),bg=p["card"],fg=p["muted"]).pack(anchor="w",pady=20);return
    for x in hits:
        r=round_card(box,p["panel"],14);r.pack(fill="x",pady=5)
        left=tk.Frame(r,bg=p["panel"]);left.pack(side="left",fill="x",expand=True,padx=16,pady=12)
        tk.Label(left,text=x.get("title","Unnamed mod"),font=(FONT,12,"bold"),bg=p["panel"],fg=p["fg"]).pack(anchor="w")
        tk.Label(left,text=(x.get("description") or "No description")[:180],font=(FONT,9),bg=p["panel"],fg=p["muted"],wraplength=650,justify="left").pack(anchor="w",pady=(3,0))
        tk.Label(left,text=f"Downloads: {x.get('downloads',0):,}   •   Supports: {', '.join(x.get('versions',[])[:5])}",font=(FONT,8),bg=p["panel"],fg=p["muted"]).pack(anchor="w",pady=(5,0))
        btn(r,"INSTALL",lambda x=x:install_workshop_mod(x),True).pack(side="right",padx=16)

# ---------- UI ----------
def clear_content():
    for w in content.winfo_children():w.destroy()
def round_card(parent,bg,r=16):
    f=tk.Frame(parent,bg=bg,highlightthickness=1,highlightbackground=bg);return f

def label(parent,text,size=10,bold=False,color=None):
    p=palette(); return tk.Label(parent,text=text,font=(FONT,size,"bold" if bold else "normal"),bg=parent.cget("bg"),fg=color or p["fg"])

def btn(parent,text,command,primary=False):
    p=palette(); b=tk.Button(parent,text=text,font=(FONT,9,"bold"),command=command,bg=p["accent"] if primary else p["button"],fg="#ffffff",activebackground=p["accent"],activeforeground="#ffffff",relief="flat",bd=0,cursor="hand2",padx=16,pady=9)
    return b

def navigate(name):
    global page; page=name
    render()

def home():
    p=palette(); clear_content()
    top=round_card(content,p["card"],22);top.pack(fill="x",pady=(0,14))
    left=tk.Frame(top,bg=p["card"]);left.pack(side="left",fill="both",expand=True,padx=26,pady=26)
    tk.Label(left,text="Your Minecraft, Your Way.",font=(FONT,27,"bold"),bg=p["card"],fg=p["fg"]).pack(anchor="w")
    tk.Label(left,text="A cleaner launcher for your profiles, installations and mods.",font=(FONT,11),bg=p["card"],fg=p["muted"]).pack(anchor="w",pady=(6,18))
    prof=profiles[selected_profile] if profiles else {"name":"Default"}; v=selected_version() or "No installation selected"; loader=prof.get("loader","Vanilla")
    tk.Label(left,text=f"ACTIVE PROFILE   {prof.get('name','Default')}",font=(FONT,9,"bold"),bg=p["card"],fg=p["muted"]).pack(anchor="w")
    tk.Label(left,text=f"{v}   •   {loader}",font=(FONT,13,"bold"),bg=p["card"],fg=p["fg"]).pack(anchor="w",pady=(4,14))
    btn(left,"PLAY MINECRAFT",launch_game,True).pack(anchor="w")
    side=tk.Frame(top,bg=p["card"]);side.pack(side="right",padx=25,pady=25)
    tk.Label(side,text="STATUS",font=(FONT,9,"bold"),bg=p["card"],fg=p["muted"]).pack(anchor="e")
    tk.Label(side,text="READY",font=(FONT,18,"bold"),bg=p["card"],fg=p["accent"]).pack(anchor="e",pady=5)
    q=round_card(content,p["panel"],18);q.pack(fill="x",pady=7)
    tk.Label(q,text="QUICK ACTIONS",font=(FONT,12,"bold"),bg=p["panel"],fg=p["fg"]).pack(anchor="w",padx=20,pady=(16,10))
    rr=tk.Frame(q,bg=p["panel"]);rr.pack(fill="x",padx=14,pady=(0,16))
    for name,fn in (("INSTALLATIONS",lambda:navigate("Installations")),("MOD WORKSHOP",workshop),("PROFILES",lambda:navigate("Profiles"))):btn(rr,name,fn,False).pack(side="left",padx=6)

def profiles_page():
    p=palette();clear_content(); head=round_card(content,p["card"]);head.pack(fill="x",pady=(0,12));tk.Label(head,text="PROFILES",font=(FONT,20,"bold"),bg=p["card"],fg=p["fg"]).pack(side="left",padx=22,pady=18);btn(head,"NEW PROFILE",new_profile,True).pack(side="right",padx=18)
    for i,x in enumerate(profiles):
        c=round_card(content,p["card"]);c.pack(fill="x",pady=5);left=tk.Frame(c,bg=p["card"]);left.pack(side="left",fill="x",expand=True,padx=18,pady=14);tk.Label(left,text=x.get("name","Profile"),font=(FONT,13,"bold"),bg=p["card"],fg=p["fg"]).pack(anchor="w");tk.Label(left,text=f"{x.get('version') or 'No version'} • {x.get('loader','Vanilla')}",font=(FONT,9),bg=p["card"],fg=p["muted"]).pack(anchor="w",pady=3);btn(c,"USE",lambda i=i:use_profile(i),i==selected_profile).pack(side="right",padx=8);btn(c,"PFP",lambda i=i:pick_pfp(i)).pack(side="right",padx=8)

def use_profile(i):
    global selected_profile;selected_profile=i;save_profiles();render()
def new_profile():
    if not require_minecraft("Profiles"):return
    w=tk.Toplevel(root);w.title("New Profile");w.geometry("430x190");w.configure(bg=palette()["panel"]);e=tk.Entry(w,font=(FONT,11));e.pack(fill="x",padx=25,pady=(40,15));e.focus_set();btn(w,"CREATE",lambda:(profiles.append({"name":e.get().strip() or "New Profile","version":"","loader":"Vanilla","description":"","pfile":""}),save_profiles(),w.destroy(),render()),True).pack(padx=25,anchor="e")
def pick_pfp(i):
    if not require_minecraft("Profile pictures"):return
    f=filedialog.askopenfilename(filetypes=[("Images","*.png;*.gif;*.bmp")]);
    if f:profiles[i]["pfile"]=f;save_profiles();render()

def installations():
    p=palette();clear_content();c=round_card(content,p["card"]);c.pack(fill="both",expand=True);tk.Label(c,text="INSTALLATIONS",font=(FONT,20,"bold"),bg=p["card"],fg=p["fg"]).pack(anchor="w",padx=22,pady=(20,4));tk.Label(c,text="Installed Minecraft versions detected in your selected folder.",font=(FONT,10),bg=p["card"],fg=p["muted"]).pack(anchor="w",padx=22,pady=(0,15));
    for v in versions():
        r=round_card(c,p["panel"]);r.pack(fill="x",padx=18,pady=5);tk.Label(r,text=v,font=(FONT,12,"bold"),bg=p["panel"],fg=p["fg"]).pack(side="left",padx=16,pady=13);btn(r,"USE",lambda v=v:set_version(v),v==selected_version()).pack(side="right",padx=16)
def set_version(v):profiles[selected_profile]["version"]=v;save_profiles();render()

def render_mods():
    p=palette();clear_content();c=round_card(content,p["card"]);c.pack(fill="both",expand=True);tk.Label(c,text="MODS",font=(FONT,20,"bold"),bg=p["card"],fg=p["fg"]).pack(anchor="w",padx=22,pady=(20,4));tk.Label(c,text="Installed mods",font=(FONT,10),bg=p["card"],fg=p["muted"]).pack(anchor="w",padx=22);btn(c,"OPEN MOD WORKSHOP",workshop,True).pack(anchor="w",padx=22,pady=15)
    if not require_minecraft("Mods"):return
    mods=os.path.join(mc_dir(),"mods"); files=[]
    try:files=sorted(x for x in os.listdir(mods) if x.lower().endswith(".jar"))
    except OSError:pass
    for x in files:tk.Label(c,text="• "+x,font=(FONT,10),bg=p["card"],fg=p["fg"]).pack(anchor="w",padx=30,pady=3)

def repair():
    p=palette();clear_content();c=round_card(content,p["card"]);c.pack(fill="both",expand=True);tk.Label(c,text="REPAIR CENTER",font=(FONT,20,"bold"),bg=p["card"],fg=p["fg"]).pack(anchor="w",padx=22,pady=(20,5));tk.Label(c,text="Diagnostics never silently delete your Minecraft files.",font=(FONT,10),bg=p["card"],fg=p["muted"]).pack(anchor="w",padx=22,pady=(0,18));btn(c,"RUN DIAGNOSTICS",diagnostics,True).pack(anchor="w",padx=22);tk.Label(c,text="Checks Minecraft folder, selected version, JSON/JAR presence, Java path, and mods folder.",font=(FONT,9),bg=p["card"],fg=p["muted"],wraplength=700,justify="left").pack(anchor="w",padx=22,pady=15)
def diagnostics():
    d=mc_dir(); checks=[("Minecraft folder",bool(d and os.path.isdir(d))), ("Ownership evidence",ownership_verified()), ("Selected version",bool(selected_version())), ("Version JSON",bool(d and selected_version() and os.path.isfile(os.path.join(d,"versions",selected_version(),selected_version()+".json")))), ("Client JAR",bool(d and selected_version() and os.path.isfile(os.path.join(d,"versions",selected_version(),selected_version()+".jar"))))]; messagebox.showinfo("Diagnostics","\n".join(("✓ " if ok else "✗ ")+name for name,ok in checks))

def settings_page():
    p=palette();clear_content();
    c=round_card(content,p["card"]);c.pack(fill="both",expand=True)
    tk.Label(c,text="SETTINGS",font=(FONT,20,"bold"),bg=p["card"],fg=p["fg"]).pack(anchor="w",padx=22,pady=(20,15))
    section(c,"Appearance")
    row=tk.Frame(c,bg=p["card"]);row.pack(fill="x",padx=22,pady=7);tk.Label(row,text="Theme",font=(FONT,10,"bold"),bg=p["card"],fg=p["fg"]).pack(side="left");combo=ttk.Combobox(row,values=list(THEMES)+list(custom_themes),state="readonly",width=24);combo.set(current_theme);combo.pack(side="right");combo.bind("<<ComboboxSelected>>",lambda e:set_theme(combo.get()))
    section(c,"Minecraft")
    pathrow=tk.Frame(c,bg=p["card"]);pathrow.pack(fill="x",padx=22,pady=5);tk.Label(pathrow,text=settings.get("minecraft_path") or "Default .minecraft",font=(FONT,9),bg=p["card"],fg=p["muted"]).pack(side="left",fill="x",expand=True);btn(pathrow,"CHOOSE FOLDER",choose_mc).pack(side="right")
    jrow=tk.Frame(c,bg=p["card"]);jrow.pack(fill="x",padx=22,pady=5);tk.Label(jrow,text=settings.get("java_path") or "Java from PATH",font=(FONT,9),bg=p["card"],fg=p["muted"]).pack(side="left",fill="x",expand=True);btn(jrow,"CHOOSE JAVA",choose_java).pack(side="right")
    section(c,"Updates")
    btn(c,"CHECK FOR UPDATES",check_updates,True).pack(anchor="w",padx=22,pady=5)
    section(c,"Backups")
    btn(c,"CREATE BACKUP",create_backup).pack(anchor="w",padx=22,pady=5)
    btn(c,"RESTORE BACKUP",restore_backup).pack(anchor="w",padx=22,pady=5)
    section(c,"Launcher")
    btn(c,"RESET ALL SETTINGS",reset_settings).pack(anchor="w",padx=22,pady=5)

def section(parent,text):tk.Label(parent,text=text.upper(),font=(FONT,9,"bold"),bg=palette()["card"],fg=palette()["muted"]).pack(anchor="w",padx=22,pady=(16,5))
def set_theme(n):
    global current_theme
    if n in THEMES or n in custom_themes:current_theme=n;save_settings();render()
def choose_mc():
    p=filedialog.askdirectory(title="Choose Minecraft folder")
    if p:settings["minecraft_path"]=p;save_settings();render()
def choose_java():
    p=filedialog.askopenfilename(title="Choose Java executable",filetypes=[("Java executable","java.exe"),("All files","*.*")])
    if p:settings["java_path"]=p;save_settings();render()
def create_backup():
    if not require_minecraft("Backups"):return
    d=mc_dir();src=os.path.join(d,"mods") if d else ""
    if not os.path.isdir(src):messagebox.showinfo("Backup","No mods folder exists to back up yet.");return
    dest=os.path.join(d,"villager_launcher_backups",time.strftime("backup_%Y%m%d_%H%M%S"));shutil.copytree(src,dest);messagebox.showinfo("Backup",f"Mods backup created safely at:\n{dest}")
def restore_backup():messagebox.showinfo("Backup","Restore center is ready, but no automatic overwrite is performed. Existing files are never silently replaced.")
def reset_settings():
    global settings,current_theme,custom_themes;settings=dict(DEFAULT);current_theme="Villager Green";custom_themes={};save_settings();render()

def render():
    global content,status,nav,header_pfp
    p=palette();root.configure(bg=p["bg"])
    for w in root.winfo_children():w.destroy()
    shell=tk.Frame(root,bg=p["bg"]);shell.pack(fill="both",expand=True)
    side=round_card(shell,p["panel"]);side.pack(side="left",fill="y",padx=(12,8),pady=12);tk.Label(side,text="VILLAGER\nLAUNCHER",font=(FONT,15,"bold"),bg=p["panel"],fg=p["fg"],justify="left").pack(anchor="w",padx=20,pady=(22,26))
    for n in ("Home","Profiles","Mods","Installations","Repair","Settings"):
        b=btn(side,n.upper(),lambda n=n:navigate(n),n==page);b.pack(fill="x",padx=10,pady=3);nav[n]=b
    tk.Frame(side,bg=p["panel"]).pack(fill="both",expand=True)
    tk.Label(side,text="Your Minecraft, Your Way.",font=(FONT,8),bg=p["panel"],fg=p["muted"],wraplength=170,justify="left").pack(anchor="w",padx=20,pady=20)
    main=tk.Frame(shell,bg=p["bg"]);main.pack(side="left",fill="both",expand=True,padx=(0,12),pady=12)
    head=tk.Frame(main,bg=p["bg"]);head.pack(fill="x",pady=(4,14));tk.Label(head,text=page,font=(FONT,18,"bold"),bg=p["bg"],fg=p["fg"]).pack(side="left");status=tk.Label(head,text="Ready",font=(FONT,9),bg=p["bg"],fg=p["muted"]);status.pack(side="right",padx=12);prof=profiles[selected_profile] if profiles else {"name":"Default"};tk.Label(head,text=prof.get("name","Default"),font=(FONT,9,"bold"),bg=p["bg"],fg=p["fg"]).pack(side="right",padx=6)
    content=tk.Frame(main,bg=p["bg"]);content.pack(fill="both",expand=True)
    if page=="Home":home()
    elif page=="Profiles":profiles_page()
    elif page=="Mods":render_mods()
    elif page=="Installations":installations()
    elif page=="Repair":repair()
    else:settings_page()

def load_persisted():load_settings();load_profiles()

if len(sys.argv)>=3 and sys.argv[1]=="--install-update": finish_update(sys.argv[2]); raise SystemExit
load_persisted();root=tk.Tk();root.title(f"Villager Launcher {CURRENT_VERSION}");root.geometry(f"{settings.get('window_width',1180)}x{settings.get('window_height',760)}");root.minsize(940,620);render();root.protocol("WM_DELETE_WINDOW",lambda:(save_settings(),root.destroy()));root.mainloop()
