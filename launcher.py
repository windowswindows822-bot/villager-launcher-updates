import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import os, sys, json, tempfile, subprocess, shutil, time
from urllib.request import Request, urlopen
from urllib.parse import quote

CURRENT_VERSION = '1.8.6'
BASE = 'https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main'
API = 'https://api.modrinth.com/v2'
APP = os.path.join(os.environ.get('APPDATA', tempfile.gettempdir()), 'VillagerLauncher')
SETTINGS_FILE = os.path.join(APP, 'settings.json')
PROFILES_FILE = os.path.join(APP, 'profiles.json')
FONT = 'Segoe UI Variable'

THEME_NAMES = ['Villager Green','Midnight','Sky','Nether','Ocean','Dirt','Stone','Diamond','Gold','Redstone','Lapis','Amethyst','Copper','Forest','Cherry Grove','Desert','Snow','Volcano','End','Piglin','Swamp','Plains','Jungle','Ice','Deep Dark','Stronghold','Sunrise','Night','Redstone Lab','Creeper']
ACCENTS = ['#62c462','#7188ff','#3a91c9','#e05a5a','#38a7c7','#9b6b43','#a0a3a8','#59d8e4','#e8c84a','#f04d4d','#4c83d8','#b66cde','#d77b4d','#55b96a','#f083b0','#d6b45b','#5a9dc5','#ff713f','#b75be8','#e6a06d','#86b84a','#8bc34a','#39c66a','#6dd6f2','#27d0c0','#c0c0c0','#ff9b5b','#6b8cff','#ff4f38','#69d34b']
THEMES = {}
for i, name in enumerate(THEME_NAMES):
    a = ACCENTS[i]
    THEMES[name] = {'bg':'#0b120d','panel':'#142017','card':'#1d2c20','fg':'#ffffff','muted':'#a9b9aa','accent':a,'button':'#2d442d','danger':'#c65353'}
THEMES['Sky'].update(bg='#dff1fa',panel='#f5fbff',card='#e8f4fa',fg='#173042',muted='#5c7180',button='#c7e0ed')
THEMES['Snow'].update(bg='#dde8f0',panel='#f4f9fc',card='#e7f0f6',fg='#20313c',muted='#647883',button='#c7dde9')
THEMES['Stone'].update(bg='#202124',panel='#2c2d30',card='#393a3d',fg='#f5f5f5',muted='#b9babd',button='#4a4c50')
THEMES['Midnight'].update(bg='#080d17',panel='#111a29',card='#1a263b',muted='#a9b5c9',button='#29385e')

DEFAULTS = {'theme':'Villager Green','minecraft_path':'','java_path':'','window_width':1180,'window_height':760,'pfp':'','confirm_updates':True}
settings = dict(DEFAULTS)
custom_themes = {}
profiles = []
selected = 0
page = 'Home'
root = None
body = None
workshop_results = []


def read_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def load_state():
    global settings, custom_themes, profiles, selected
    data = read_json(SETTINGS_FILE, {})
    if isinstance(data, dict):
        for key in DEFAULTS:
            if key in data:
                settings[key] = data[key]
        if isinstance(data.get('custom_themes'), dict):
            custom_themes = data['custom_themes']
    profiles = read_json(PROFILES_FILE, [])
    if not isinstance(profiles, list) or not profiles:
        profiles = [{'name':'Default','version':'','loader':'Vanilla','description':'Your first Villager Launcher profile.'}]
    selected = min(selected, len(profiles)-1)


def save_state():
    os.makedirs(APP, exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump({**settings, 'custom_themes':custom_themes}, f, indent=2)
    with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2)


def T():
    return custom_themes.get(settings.get('theme'), THEMES.get(settings.get('theme'), THEMES['Villager Green']))


def mc_dir():
    p = settings.get('minecraft_path','')
    if p and os.path.isdir(p):
        return p
    appdata = os.environ.get('APPDATA','')
    return os.path.join(appdata, '.minecraft') if appdata else ''


def owned():
    d = mc_dir()
    return bool(d and os.path.isdir(d) and (os.path.isfile(os.path.join(d,'launcher_accounts.json')) or os.path.isfile(os.path.join(d,'launcher_profiles.json'))))


def gate(feature):
    if owned():
        return True
    messagebox.showwarning('Minecraft Required', f'{feature} is locked until an original Minecraft installation is detected. Sign in through the official Minecraft Launcher, then select its Minecraft folder in Settings.')
    return False


def versions():
    d = os.path.join(mc_dir(), 'versions')
    if not os.path.isdir(d):
        return []
    try:
        return sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x))], reverse=True)
    except OSError:
        return []


def selected_version():
    if profiles and profiles[selected].get('version'):
        return profiles[selected]['version']
    v = versions()
    return v[0] if v else ''


def net_json(url, timeout=15):
    request = Request(url + ('&' if '?' in url else '?') + 't=' + str(time.time_ns()), headers={'User-Agent':'Villager-Launcher/1.8.6'})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def card(parent, x, y, w, h, fill=None, radius=18):
    fill = fill or T()['card']
    radius = max(2, min(radius, w//2, h//2))
    c = tk.Canvas(parent, width=w, height=h, bg=parent.cget('bg'), highlightthickness=0, bd=0)
    c.place(x=x, y=y)
    # FIX: Tkinter needs exactly four coordinates; start/extent are keywords.
    c.create_arc(0,0,2*radius,2*radius,start=90,extent=90,fill=fill,outline=fill)
    c.create_arc(w-2*radius,0,w,2*radius,start=0,extent=90,fill=fill,outline=fill)
    c.create_arc(0,h-2*radius,2*radius,h,start=180,extent=90,fill=fill,outline=fill)
    c.create_arc(w-2*radius,h-2*radius,w,h,start=270,extent=90,fill=fill,outline=fill)
    c.create_rectangle(radius,0,w-radius,h,fill=fill,outline=fill)
    c.create_rectangle(0,radius,w,h-radius,fill=fill,outline=fill)
    return c


def label(parent, text, x, y, size=10, bold=False, fg=None):
    tk.Label(parent,text=text,font=(FONT,size,'bold' if bold else 'normal'),bg=parent.cget('bg'),fg=fg or T()['fg'],anchor='w').place(x=x,y=y)


def button(parent, text, command, x, y, w=140, h=40, primary=False, enabled=True):
    t = T()
    c = card(parent,x,y,w,h,t['accent'] if primary else t['button'],12)
    c.create_text(w/2,h/2,text=text,fill='#fff' if primary else t['fg'],font=(FONT,10,'bold'))
    if enabled:
        c.bind('<Button-1>', lambda _e: command())
        c.configure(cursor='hand2')
    return c


def go(destination):
    global page
    page = destination
    render()


def shell():
    global body
    t = T()
    root.configure(bg=t['bg'])
    for w in root.winfo_children():
        w.destroy()
    sidebar = tk.Frame(root,bg=t['panel'])
    sidebar.place(x=0,y=0,width=225,relheight=1)
    tk.Label(sidebar,text='⛏  MINECRAFT',font=(FONT,13,'bold'),bg=t['panel'],fg=t['fg']).place(x=18,y=18)
    nav=[('HOME','Home'),('PROFILES','Profiles'),('MOD WORKSHOP','Workshop'),('INSTALLATIONS','Installations'),('REPAIR','Repair'),('SETTINGS','Settings')]
    for i,(name,destination) in enumerate(nav):
        active = page == destination
        b=tk.Label(sidebar,text=name,bg=t['accent'] if active else t['panel'],fg='#fff' if active else t['muted'],font=(FONT,10,'bold'),anchor='w',padx=18)
        b.place(x=12,y=72+i*46,width=200,height=40)
        b.bind('<Button-1>',lambda _e,p=destination:go(p))
    tk.Label(sidebar,text=f'Repair Mode • {CURRENT_VERSION}',bg=t['panel'],fg=t['muted'],font=(FONT,8)).place(x=18,rely=1,y=-25)
    header=tk.Frame(root,bg=t['bg'])
    header.place(x=225,y=0,relwidth=1,width=-225,height=78)
    tk.Label(header,text='Villager Launcher',font=(FONT,15,'bold'),bg=t['bg'],fg=t['fg']).place(x=28,y=18)
    tk.Label(header,text='Your Minecraft, Your Way.',font=(FONT,9),bg=t['bg'],fg=t['muted']).place(x=29,y=45)
    tk.Label(header,text=profiles[selected].get('name','Default'),font=(FONT,10,'bold'),bg=t['bg'],fg=t['fg']).place(relx=1,x=-25,y=30,anchor='e')
    body=tk.Frame(root,bg=t['bg'])
    body.place(x=225,y=78,relwidth=1,width=-225,relheight=1,height=-78)


def render():
    shell()
    {'Home':home,'Profiles':profiles_page,'Workshop':workshop_page,'Installations':installations_page,'Repair':repair_page,'Settings':settings_page}.get(page,home)()


def home():
    t=T()
    label(body,'Welcome back',30,20,11,fg=t['muted'])
    label(body,'Ready to meet your wishes?',30,45,27,True)
    card(body,30,95,700,245,t['card'],22)
    label(body,'MINECRAFT',55,120,10,True,t['muted'])
    label(body,'Your Minecraft, Your Way.',55,150,22,True)
    label(body,'Installation  •  '+(selected_version() or 'No installation selected'),55,198,10,fg=t['muted'])
    label(body,'Profile  •  '+profiles[selected].get('name','Default'),55,223,10,fg=t['muted'])
    button(body,'PLAY',launch_game,500,265,180,54,True)
    for i,(name,dest) in enumerate([('Installations','Installations'),('Mod Workshop','Workshop'),('Settings','Settings')]):
        x=30+i*225
        card(body,x,375,205,100,t['panel'],16)
        label(body,name,x+18,398,11,True)
        button(body,'OPEN',lambda d=dest:go(d),x+18,435,90,28)
    card(body,755,95,330,245,t['panel'],22)
    label(body,'ACTIVE PROFILE',780,120,10,True,t['muted'])
    label(body,profiles[selected].get('name','Default'),780,155,19,True)
    label(body,'Original Minecraft: '+('Detected' if owned() else 'Not detected'),780,210,10,True,t['accent'] if owned() else t['danger'])


def profiles_page():
    t=T(); label(body,'Profiles',30,22,25,True); label(body,'Profiles and PFPs require original Minecraft.',30,57,10,fg=t['muted'])
    if not gate('Profiles'): return
    for i,p in enumerate(profiles[:5]):
        y=100+i*105;card(body,30,y,750,85,t['card'],16)
        label(body,p.get('name','Profile'),55,y+17,14,True)
        label(body,f"{p.get('version') or 'Auto'}  •  {p.get('loader','Vanilla')}",55,y+47,10,fg=t['muted'])
        button(body,'SELECT',lambda i=i:select_profile(i),630,y+25,105,34,i==selected)
    button(body,'NEW PROFILE',new_profile,820,100,170,40,True)
    button(body,'SET PFP',choose_pfp,820,150,170,40)


def select_profile(i):
    global selected
    selected=i;save_state();render()


def new_profile():
    if gate('Profiles'):
        profiles.append({'name':f'Profile {len(profiles)+1}','version':'','loader':'Vanilla','description':'New profile.'})
        save_state();render()


def choose_pfp():
    if not gate('Profile pictures'): return
    f=filedialog.askopenfilename(filetypes=[('PNG/GIF','*.png *.gif'),('All files','*.*')])
    if f:
        settings['pfp']=f;save_state();render()


def installations_page():
    t=T();label(body,'Installations',30,22,25,True);label(body,'Choose an installed Minecraft version.',30,57,10,fg=t['muted'])
    if not gate('Installations'): return
    vs=versions()
    if not vs:
        card(body,30,100,760,85,t['card'],16);label(body,'No Minecraft versions found.',55,120,13,True);label(body,'Install a version with the official Minecraft Launcher first.',55,148,10,fg=t['muted']);return
    for i,v in enumerate(vs[:8]):
        y=100+i*65;card(body,30,y,850,52,t['card'],14);label(body,v,50,y+16,11,True);button(body,'SELECT',lambda v=v:set_version(v),760,y+9,90,34,v==selected_version())


def set_version(v):
    profiles[selected]['version']=v;save_state();render()


def java_ok():
    try:
        subprocess.run([settings.get('java_path') or 'java','-version'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=5)
        return True
    except (OSError,subprocess.SubprocessError): return False


def repair_page():
    t=T();label(body,'Repair Center',30,22,25,True);label(body,'Safe diagnostics. Nothing is deleted automatically.',30,57,10,fg=t['muted'])
    checks=[('Minecraft folder',bool(mc_dir() and os.path.isdir(mc_dir()))),('Official launcher evidence',owned()),('Installed versions',bool(versions())),('Java',java_ok())]
    for i,(name,ok) in enumerate(checks):
        y=105+i*65;card(body,30,y,760,52,t['card'],14);label(body,name,50,y+16,11,True);label(body,'✓ OK' if ok else '✕ Problem',600,y+16,10,True,t['accent'] if ok else t['danger'])
    button(body,'RUN CHECK AGAIN',render,30,390,180,40,True)


def launch_game():
    if not gate('Minecraft launching'): return
    v=selected_version();d=mc_dir()
    if not v:
        messagebox.showerror('Launch Error','Stage: Version selection\n\nWhat broke: No Minecraft version is selected or installed.');return
    vd=os.path.join(d,'versions',v);jf=os.path.join(vd,v+'.json');jar=os.path.join(vd,v+'.jar')
    if not os.path.isfile(jf):
        messagebox.showerror('Launch Error',f'Stage: Version files\n\nWhat broke: Missing version JSON:\n{jf}');return
    if not os.path.isfile(jar):
        messagebox.showerror('Launch Error',f'Stage: Version files\n\nWhat broke: Missing client JAR:\n{jar}');return
    if not java_ok():
        messagebox.showerror('Launch Error',f'Stage: Java startup\n\nWhat broke: Java could not be started.\n\nJava path: {settings.get("java_path") or "System Java"}');return
    messagebox.showinfo('Launch Diagnostics','Stage: Validation complete\n\nMinecraft files and Java were found.\n\nWhat broke: Nothing in the local file checks.\n\nAuthenticated Microsoft launch integration is not enabled in this repair build, so no Minecraft process was started.')


def workshop_page():
    t=T();label(body,'Mod Workshop',30,18,25,True);label(body,'Powered by Modrinth. INSTALL is locked until original Minecraft is detected.',30,52,10,fg=t['muted'])
    q=tk.Entry(body,font=(FONT,10),bg=t['panel'],fg=t['fg'],insertbackground=t['fg'],relief='flat');q.place(x=30,y=88,width=270,height=34)
    typ=tk.StringVar(value='All');menu=tk.OptionMenu(body,typ,'All','Mod','Shader','Resource Pack','Data Pack');menu.configure(bg=t['button'],fg=t['fg'],activebackground=t['accent'],activeforeground='#fff',relief='flat',highlightthickness=0);menu.place(x=315,y=88,width=135,height=34)
    ver=tk.Entry(body,font=(FONT,10),bg=t['panel'],fg=t['fg'],insertbackground=t['fg'],relief='flat');ver.insert(0,selected_version());ver.place(x=465,y=88,width=120,height=34)
    sort=tk.StringVar(value='Relevance');sm=tk.OptionMenu(body,sort,'Relevance','Downloads','Updated');sm.configure(bg=t['button'],fg=t['fg'],activebackground=t['accent'],activeforeground='#fff',relief='flat',highlightthickness=0);sm.place(x=600,y=88,width=120,height=34)
    button(body,'SEARCH',lambda:search_workshop(q.get(),typ.get(),ver.get(),sort.get()),735,88,120,34,True)
    if not workshop_results:
        label(body,'Search Modrinth for mods, shaders, resource packs, or data packs.',30,145,10,fg=t['muted']);return
    for i,p in enumerate(workshop_results[:6]):
        y=145+i*85;card(body,30,y,850,72,t['card'],14);title=p.get('title') or p.get('slug','Unknown');desc=(p.get('description') or '').replace('\n',' ');desc=desc[:78]+'...' if len(desc)>81 else desc
        label(body,title,52,y+10,11,True);label(body,desc,52,y+34,9,fg=t['muted']);label(body,f"Downloads: {p.get('downloads',0):,}",52,y+54,8,fg=t['muted'])
        if owned(): button(body,'INSTALL',lambda p=p:install_project(p),735,y+18,110,34,True)
        else: button(body,'LOCKED',lambda:None,735,y+18,110,34,False,False)


def search_workshop(query,content_type,minecraft_version,sort):
    global workshop_results
    try:
        index={'Relevance':'relevance','Downloads':'downloads','Updated':'updated'}.get(sort,'relevance')
        facets=[]
        if content_type!='All': facets.append([f'project_type:{content_type.lower().replace(" ","_")}'])
        if minecraft_version.strip(): facets.append([f'versions:{minecraft_version.strip()}'])
        url=f"{API}/search?query={quote(query.strip())}&limit=12&index={index}"
        if facets: url += '&facets='+quote(json.dumps(facets,separators=(',',':')))
        workshop_results=net_json(url).get('hits',[]);render()
    except Exception as e:
        messagebox.showerror('Workshop Error',f'Could not search Modrinth.\n\nWhat broke: {e}')


def install_project(project):
    if not gate('Mod Workshop installation'): return
    v=selected_version()
    if not v:
        messagebox.showerror('Install Error','What broke: No Minecraft version is selected.');return
    try:
        slug=project.get('slug','')
        data=net_json(f'{API}/project/{quote(slug)}/version?game_versions={quote(json.dumps([v]))}')
        if not data: raise ValueError(f'No compatible {v} release was found.')
        release=data[0];files=release.get('files',[]);primary=next((f for f in files if f.get('primary')),files[0] if files else None)
        if not primary or not primary.get('url'): raise ValueError('No downloadable file was provided.')
        kind=(project.get('project_type') or 'mod').lower();folders={'mod':'mods','shader':'shaderpacks','resourcepack':'resourcepacks','datapack':'datapacks'};folder=folders.get(kind,'mods')
        target_dir=os.path.join(mc_dir(),folder);os.makedirs(target_dir,exist_ok=True);filename=os.path.basename(primary['url'].split('?')[0]) or (slug+'.jar');target=os.path.join(target_dir,filename)
        req=Request(primary['url'],headers={'User-Agent':'Villager-Launcher/1.8.6'})
        with urlopen(req,timeout=30) as response:data=response.read()
        if not data: raise ValueError('Downloaded file was empty.')
        with open(target,'wb') as f:f.write(data)
        messagebox.showinfo('Workshop','Installed successfully!\n\n'+project.get('title',slug)+f'\n\nFolder: {folder}\nFile: {filename}')
    except Exception as e:
        messagebox.showerror('Install Error',f'The Workshop installation failed.\n\nWhat broke: {e}')


def settings_page():
    t=T();label(body,'Settings',30,20,25,True)
    card(body,30,70,850,125,t['card'],18);label(body,'Appearance',55,92,13,True);label(body,'Theme',55,126,10,fg=t['muted'])
    theme_var=tk.StringVar(value=settings.get('theme','Villager Green'));tm=tk.OptionMenu(body,theme_var,*THEME_NAMES,*custom_themes.keys());tm.configure(bg=t['button'],fg=t['fg'],activebackground=t['accent'],activeforeground='#fff',relief='flat',highlightthickness=0);tm.place(x=250,y=118,width=260,height=34)
    button(body,'APPLY THEME',lambda:apply_theme(theme_var.get()),530,118,140,34,True);button(body,'CUSTOM THEME',custom_theme,685,118,150,34)
    card(body,30,215,850,135,t['card'],18);label(body,'Minecraft',55,237,13,True);label(body,'Minecraft folder',55,272,10,fg=t['muted']);label(body,settings.get('minecraft_path') or '(Automatic: %APPDATA%\\.minecraft)',190,272,9);button(body,'BROWSE',choose_mc,650,258,120,34)
    label(body,'Java executable',55,307,10,fg=t['muted']);label(body,settings.get('java_path') or '(System Java)',190,307,9);button(body,'BROWSE',choose_java,650,293,120,34)
    card(body,30,370,850,115,t['card'],18);label(body,'Updates',55,392,13,True);label(body,'Updates are manual. Nothing downloads automatically.',55,425,10,fg=t['muted']);button(body,'CHECK FOR UPDATES',check_updates,55,445,180,30,True);button(body,"WHAT'S NEW",release_notes,250,445,130,30)
    card(body,30,505,850,120,t['card'],18);label(body,'Backups',55,527,13,True);label(body,'Create a safe backup of your mods folder.',55,560,10,fg=t['muted']);button(body,'CREATE BACKUP',backup,55,580,150,30);button(body,'OPEN BACKUPS',open_backups,220,580,145,30)
    button(body,'RESET SETTINGS',reset_settings,30,650,150,34)


def apply_theme(name):
    if name in THEMES or name in custom_themes:
        settings['theme']=name;save_state();render()


def custom_theme():
    chosen=colorchooser.askcolor(title='Choose custom accent color',initialcolor=T()['accent'])
    if not chosen[1]:return
    name=f'Custom {len(custom_themes)+1}';custom_themes[name]=dict(T());custom_themes[name]['accent']=chosen[1];custom_themes[name]['button']=chosen[1];settings['theme']=name;save_state();render()


def choose_mc():
    f=filedialog.askdirectory(title='Choose Minecraft folder')
    if f:settings['minecraft_path']=f;save_state();render()


def choose_java():
    f=filedialog.askopenfilename(title='Choose Java executable',filetypes=[('Executable','*.exe'),('All files','*.*')])
    if f:settings['java_path']=f;save_state();render()


def backup():
    if not gate('Backups'):return
    source=os.path.join(mc_dir(),'mods')
    if not os.path.isdir(source):messagebox.showinfo('Backup','There is no mods folder to back up yet.');return
    root_dir=os.path.join(mc_dir(),'villager_launcher_backups');os.makedirs(root_dir,exist_ok=True);dest=os.path.join(root_dir,time.strftime('mods_%Y%m%d_%H%M%S'));shutil.copytree(source,dest);messagebox.showinfo('Backup','Backup created:\n\n'+dest)


def open_backups():
    if not gate('Backups'):return
    folder=os.path.join(mc_dir(),'villager_launcher_backups');os.makedirs(folder,exist_ok=True);os.startfile(folder)


def reset_settings():
    if not messagebox.askyesno('Reset Settings','Reset launcher settings?\n\nMinecraft files will not be deleted.'):return
    settings.clear();settings.update(DEFAULTS);custom_themes.clear();save_state();render()


def latest_info():
    with github_request(BASE+'/version.json',8) as response:return json.loads(response.read().decode('utf-8'))


def github_request(url,timeout=10):
    return urlopen(Request(url+('&' if '?' in url else '?')+'t='+str(time.time_ns()),headers={'User-Agent':'Villager-Launcher/1.8.6'}),timeout=timeout)


def vt(v):
    out=[]
    for p in str(v).split('.')[:3]:
        n=''.join(c for c in p if c.isdigit());out.append(int(n or 0))
    return tuple((out+[0,0,0])[:3])


def notes(info):
    n=info.get('notes',{});lines=[]
    if isinstance(n,dict):
        for key in ('Added','Changed','Removed','Fixed'):
            items=n.get(key,[])
            if isinstance(items,str):items=[items]
            if items:lines.append(key.upper());lines.extend('• '+str(x) for x in items);lines.append('')
    return '\n'.join(lines).strip() or 'No changes listed.'


def download_update():
    with github_request(BASE+'/launcher.py',20) as response:data=response.read()
    if not data:raise ValueError('Downloaded launcher was empty.')
    p=os.path.join(tempfile.gettempdir(),'villager_launcher_update.py');open(p,'wb').write(data);return p


def update_helper(source,target):
    helper=os.path.join(tempfile.gettempdir(),'villager_launcher_update_helper.py')
    code='''import sys,time,shutil,subprocess,os\nsource=sys.argv[1];target=sys.argv[2];time.sleep(1.5)\nfor _ in range(30):\n    try:\n        shutil.copy2(source,target)\n        subprocess.Popen([sys.executable,target],close_fds=True)\n        try: os.remove(source)\n        except OSError: pass\n        break\n    except OSError: time.sleep(.5)\n'''
    open(helper,'w',encoding='utf-8').write(code);subprocess.Popen([sys.executable,helper,source,target],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),close_fds=True)


def check_updates(startup=False):
    try:
        info=latest_info();latest=str(info.get('version',CURRENT_VERSION))
        if vt(latest)<=vt(CURRENT_VERSION):
            if not startup:messagebox.showinfo('Updates',f'Villager Launcher is up to date.\n\nVersion: {CURRENT_VERSION}')
            return
        if not messagebox.askyesno('Update Available',f'New version {latest} is available!\n\nInstalled: {CURRENT_VERSION}\nAvailable: {latest}\n\n{notes(info)}\n\nUpdate now?'):return
        source=download_update();target=os.path.abspath(sys.argv[0])
        if not messagebox.askyesno('Ready to Update','The update is downloaded.\n\nThe launcher will close, replace itself, and restart.'):return
        update_helper(source,target);root.destroy()
    except Exception as e:
        if not startup:messagebox.showerror('Update Error',f'Could not update the launcher.\n\nWhat broke: {e}')


def release_notes():
    try:info=latest_info()
    except Exception:info={'version':CURRENT_VERSION,'notes':{}}
    messagebox.showinfo("What's New",f"Villager Launcher {info.get('version',CURRENT_VERSION)}\n\n{notes(info)}")


def main():
    global root
    load_state();root=tk.Tk();root.title(f'Villager Launcher {CURRENT_VERSION} • Repair Mode');root.geometry(f"{int(settings.get('window_width',1180))}x{int(settings.get('window_height',760))}");root.minsize(1000,650);render();root.protocol('WM_DELETE_WINDOW',lambda:(save_state(),root.destroy()));root.after(700,lambda:check_updates(True));root.mainloop()

if __name__=='__main__':main()
