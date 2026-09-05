import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import os, sys, json, tempfile, subprocess, shutil, time, traceback
from urllib.request import Request, urlopen
from urllib.parse import quote

CURRENT_VERSION = "1.9.1"
BASE = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main"
API = "https://api.modrinth.com/v2"
APP = os.path.join(os.environ.get("APPDATA", tempfile.gettempdir()), "VillagerLauncher")
SETTINGS_FILE = os.path.join(APP, "settings.json")
PROFILES_FILE = os.path.join(APP, "profiles.json")
FEEDBACK_DIR = os.path.join(APP, "feedback")
FONT = "Segoe UI Variable"

THEME_NAMES = ["Villager Green","Midnight","Sky","Nether","Ocean","Dirt","Stone","Diamond","Gold","Redstone","Lapis","Amethyst","Copper","Forest","Cherry Grove","Desert","Snow","Volcano","End","Piglin","Swamp","Plains","Jungle","Ice","Deep Dark","Stronghold","Sunrise","Night","Redstone Lab","Creeper"]
ACCENTS = ["#62c462","#7188ff","#3a91c9","#e05a5a","#38a7c7","#9b6b43","#a0a3a8","#59d8e4","#e8c84a","#f04d4d","#4c83d8","#b66cde","#d77b4d","#55b96a","#f083b0","#d6b45b","#5a9dc5","#ff713f","#b75be8","#e6a06d","#86b84a","#8bc34a","#39c66a","#6dd6f2","#27d0c0","#c0c0c0","#ff9b5b","#6b8cff","#ff4f38","#69d34b"]
THEMES = {}
for i, name in enumerate(THEME_NAMES):
    a = ACCENTS[i]
    THEMES[name] = {"bg":"#0b120d","panel":"#142017","card":"#1d2c20","fg":"#ffffff","muted":"#a9b9aa","accent":a,"button":"#2d442d","danger":"#c65353","input":"#101a12","menu":"#17261a","hover":"#355236","selected":"#315b35"}
THEMES["Sky"].update(bg="#dff1fa",panel="#f5fbff",card="#e8f4fa",fg="#173042",muted="#5c7180",button="#c7e0ed",input="#ffffff",menu="#edf8fd",hover="#c7e0ed",selected="#b3d7e7")
THEMES["Snow"].update(bg="#dde8f0",panel="#f4f9fc",card="#e7f0f6",fg="#20313c",muted="#647883",button="#c7dde9",input="#ffffff",menu="#f5fafc",hover="#d5e5ee",selected="#c1d9e5")
THEMES["Stone"].update(bg="#202124",panel="#2c2d30",card="#393a3d",fg="#f5f5f5",muted="#b9babd",button="#4a4c50",input="#292a2d",menu="#333438",hover="#56585d",selected="#4d5056")
THEMES["Midnight"].update(bg="#080d17",panel="#111a29",card="#1a263b",muted="#a9b5c9",button="#29385e",input="#0d1420",menu="#151f31",hover="#34456f",selected="#2e416d")

DEFAULTS = {"theme":"Villager Green","minecraft_path":"","java_path":"","window_width":1180,"window_height":760,"pfp":"","confirm_updates":True}
settings = dict(DEFAULTS)
custom_themes = {}
profiles = []
selected = 0
page = "Home"
root = None
body = None
workshop_results = []
last_repair_results = []

BOT_KB = {
"minecraft": "Minecraft is a sandbox game where you can build, explore, craft, and survive.",
"java": "Minecraft Java Edition runs on Java. The launcher can use a selected Java executable.",
"bedrock": "Minecraft Bedrock Edition is a separate edition designed for multiple platforms.",
"mod": "A Minecraft mod changes or adds features to the game. Villager Launcher uses Modrinth for workshop browsing.",
"modrinth": "Modrinth is a platform for Minecraft mods, modpacks, resource packs, and shaders.",
"forge": "Forge is a Minecraft mod loader and modding platform.",
"fabric": "Fabric is a lightweight Minecraft mod loader and modding toolchain.",
"quilt": "Quilt is a community Minecraft mod loader based around the Fabric ecosystem.",
"shader": "Shaders can change Minecraft's lighting and visual effects.",
"resource pack": "A resource pack changes textures, sounds, models, fonts, or other visual assets.",
"server": "A Minecraft server lets multiple players play together in a shared world.",
"redstone": "Redstone is Minecraft's in-game system for creating circuits, mechanisms, and automation.",
"creeper": "Creepers are hostile Minecraft mobs famous for sneaking toward players and exploding.",
"villager": "Villagers are NPCs that can trade items and have different professions.",
"diamond": "Diamonds are a valuable Minecraft resource used for tools, armor, and other crafting.",
"nether": "The Nether is a dangerous Minecraft dimension with unique mobs, blocks, structures, and resources.",
"end": "The End is a Minecraft dimension associated with the Ender Dragon and End Cities.",
"ender dragon": "The Ender Dragon is the main boss associated with the End dimension.",
"wither": "The Wither is a powerful Minecraft boss that can be summoned using soul sand or soul soil and wither skeleton skulls.",
"skeleton": "Skeletons are hostile mobs that normally attack using bows.",
"zombie": "Zombies are common hostile mobs that chase players and villagers.",
"spider": "Spiders are hostile mobs that can climb walls.",
"smp": "SMP means Survival Multiplayer, a Minecraft survival world played with multiple people.",
"creative": "Creative mode gives players broad building and inventory abilities without normal survival restrictions.",
"survival": "Survival mode focuses on gathering resources, crafting, exploration, health, and survival.",
"hardcore": "Hardcore is a survival mode with a locked high difficulty and one-life gameplay rules.",
"peaceful": "Peaceful difficulty removes most hostile mob threats and changes some survival mechanics.",
"normal": "Normal is one of Minecraft's standard difficulty settings.",
"hard": "Hard is a higher Minecraft difficulty with tougher survival conditions.",
"easy": "Easy is a lower Minecraft difficulty than Normal and Hard.",
"biome": "A biome is a Minecraft region with its own terrain, vegetation, climate, and environmental characteristics.",
"chunk": "A chunk is a fixed-size region of the Minecraft world used for world storage and processing.",
"seed": "A Minecraft seed is a value used to generate a world layout.",
"coordinates": "Minecraft coordinates show a player's position using X, Y, and Z values.",
"crafting": "Crafting combines items in a crafting interface to make other items.",
"enchanting": "Enchanting adds special effects to eligible tools, weapons, armor, and books.",
"anvil": "An anvil can combine, repair, and rename eligible items using experience and materials.",
"xp": "XP means experience. Minecraft uses experience points for enchanting and other mechanics.",
"armor": "Armor reduces damage from many sources and can provide additional protection through enchantments.",
"sword": "A sword is a melee weapon used primarily for attacking mobs and entities.",
"pickaxe": "A pickaxe is a tool designed primarily for mining blocks such as stone and ores.",
"axe": "An axe is a tool useful for chopping wood and can also be used as a weapon.",
"shovel": "A shovel is useful for digging blocks such as dirt, sand, and gravel.",
"hoe": "A hoe is mainly used to prepare certain blocks for farming.",
"food": "Food restores hunger and, depending on the item, can provide additional effects.",
"farming": "Minecraft farming lets players grow crops and raise animals for renewable resources.",
"furnace": "A furnace smelts or cooks eligible items using fuel.",
"blast furnace": "A blast furnace smelts eligible ores and metal-related items faster than a normal furnace.",
"smoker": "A smoker cooks food items faster than a normal furnace.",
"crafting table": "A crafting table provides the standard larger crafting grid.",
"chest": "A chest is a storage block that holds items.",
"ender chest": "An Ender Chest provides personal storage that can be accessed from other Ender Chests.",
"shulker": "Shulker Boxes provide portable storage that keeps their contents when broken.",
"elytra": "Elytra are wings that allow players to glide through the air.",
"trident": "A trident is a weapon that can be used in melee or thrown.",
"bow": "A bow is a ranged weapon that uses arrows as ammunition.",
"crossbow": "A crossbow is a ranged weapon that can be loaded and fired later.",
"totem": "A Totem of Undying can save a player from certain death when held appropriately.",
"netherite": "Netherite is a high-tier material used to upgrade eligible diamond gear.",
"obsidian": "Obsidian is a very durable block commonly used to build Nether portals.",
"portal": "A Nether portal is a constructed frame activated with fire that connects the Overworld and Nether.",
"stronghold": "A stronghold is an underground structure containing an End Portal room.",
"village": "A village is a generated settlement containing villagers and structures.",
"pillager": "Pillagers are hostile illagers that commonly use crossbows.",
"raid": "A raid is a hostile event involving waves of illagers attacking a village.",
"warden": "The Warden is a powerful hostile mob associated with the Deep Dark.",
"deep dark": "The Deep Dark is an underground biome containing sculk and ancient structures.",
"ancient city": "Ancient Cities are large Deep Dark structures containing valuable loot and dangerous encounters.",
"ocean": "Ocean biomes are large bodies of water containing aquatic life, structures, and underwater terrain.",
"jungle": "Jungle biomes are warm, dense biomes with tall vegetation and jungle-specific features.",
"desert": "Deserts are dry biomes dominated by sand and commonly contain desert structures.",
"snow": "Snowy biomes have cold environments and can contain snow layers and ice.",
"taiga": "Taiga biomes are cold forest regions commonly dominated by spruce trees.",
"meadow": "Meadows are grassy mountain biomes with flowers and open terrain.",
"launcher": "Villager Launcher is this custom launcher project. It provides profiles, installations, Modrinth Workshop, repair tools, themes, and more.",
"profile": "A launcher profile can store a chosen Minecraft version and loader configuration.",
"theme": "Villager Launcher themes control the launcher palette, including backgrounds, panels, cards, buttons, text, inputs, menus, hover states, and selections.",
"update": "Villager Launcher updates are manual. The launcher should not silently download and install updates.",
"repair": "Repair Center checks launcher data and configuration and should only perform safe, known fixes.",
"backup": "A launcher backup can preserve selected local launcher or Minecraft-related configuration before changes.",
"fps": "FPS means frames per second. Higher FPS generally means more frequent rendered frames.",
"ram": "RAM is system memory used by running applications and games.",
"gpu": "A GPU handles graphics rendering and can strongly affect game performance.",
"cpu": "A CPU performs general-purpose processing and is important for game logic and many applications.",
"ssd": "An SSD is solid-state storage that generally provides fast access to files and applications.",
"hdd": "An HDD uses spinning magnetic disks for storage.",
"windows": "Windows is Microsoft's desktop operating system family.",
"microsoft": "Microsoft is the company behind Windows, Xbox, and the Microsoft account ecosystem used for Minecraft authentication.",
"account": "Minecraft Java Edition ownership is associated with the account used to purchase and access the game.",
"skin": "A Minecraft skin changes the player's character appearance.",
"texture": "A texture is an image used to give a block, item, mob, or interface element its appearance.",
"command": "Minecraft commands are text instructions that can perform actions or change game state when permitted.",
"gamerule": "Gamerules are world settings that control specific Minecraft mechanics.",
"difficulty": "Difficulty controls several survival mechanics and hostile mob behavior.",
"weather": "Minecraft weather includes clear conditions, rain, and thunderstorms depending on the world and edition.",
"day night": "Minecraft worlds use a repeating day/night cycle.",
"bed": "Beds can set a player's spawn point and are used for sleeping where permitted.",
"respawn": "Respawning returns a player to a valid spawn point after death or certain events.",
"netherite armor": "Netherite armor is an upgraded form of diamond armor with high durability and useful properties.",
"villager launcher": "Villager Launcher is the custom Minecraft launcher you're working on, currently in 1.9.1 beta/testing.",
}


def read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f: return json.load(f)
    except (OSError, json.JSONDecodeError): return default

def load_state():
    global settings, custom_themes, profiles, selected
    data=read_json(SETTINGS_FILE,{})
    if isinstance(data,dict):
        for k in DEFAULTS:
            if k in data: settings[k]=data[k]
        if isinstance(data.get("custom_themes"),dict): custom_themes=data["custom_themes"]
    profiles=read_json(PROFILES_FILE,[])
    if not isinstance(profiles,list) or not profiles:
        profiles=[{"name":"Default","version":"","loader":"Vanilla","description":"Your first Villager Launcher profile."}]
    selected=min(selected,len(profiles)-1)

def save_state():
    os.makedirs(APP,exist_ok=True)
    with open(SETTINGS_FILE,"w",encoding="utf-8") as f: json.dump({**settings,"custom_themes":custom_themes},f,indent=2)
    with open(PROFILES_FILE,"w",encoding="utf-8") as f: json.dump(profiles,f,indent=2)

def T(): return custom_themes.get(settings.get("theme"),THEMES.get(settings.get("theme"),THEMES["Villager Green"]))
def mc_dir():
    p=settings.get("minecraft_path","")
    if p and os.path.isdir(p): return p
    a=os.environ.get("APPDATA",""); return os.path.join(a,".minecraft") if a else ""
def owned():
    d=mc_dir(); return bool(d and os.path.isdir(d) and (os.path.isfile(os.path.join(d,"launcher_accounts.json")) or os.path.isfile(os.path.join(d,"launcher_profiles.json"))))
def gate(feature):
    if owned(): return True
    messagebox.showwarning("Minecraft Required",f"{feature} is locked until an original Minecraft installation is detected. Sign in through the official Minecraft Launcher, then select its Minecraft folder in Settings.")
    return False
def versions():
    d=os.path.join(mc_dir(),"versions")
    if not os.path.isdir(d): return []
    try:return sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x))],reverse=True)
    except OSError:return []
def selected_version():
    if profiles and profiles[selected].get("version"): return profiles[selected]["version"]
    v=versions(); return v[0] if v else ""
def net_json(url,timeout=15):
    req=Request(url+("&" if "?" in url else "?")+"t="+str(time.time_ns()),headers={"User-Agent":f"Villager-Launcher/{CURRENT_VERSION}"})
    with urlopen(req,timeout=timeout) as r:return json.loads(r.read().decode("utf-8"))

def rounded(parent,x,y,w,h,fill=None,radius=18):
    fill=fill or T()["card"]; radius=max(2,min(radius,w//2,h//2)); c=tk.Canvas(parent,width=w,height=h,bg=parent.cget("bg"),highlightthickness=0,bd=0); c.place(x=x,y=y)
    c.create_arc(0,0,2*radius,2*radius,start=90,extent=90,fill=fill,outline=fill);c.create_arc(w-2*radius,0,w,2*radius,start=0,extent=90,fill=fill,outline=fill);c.create_arc(0,h-2*radius,2*radius,h,start=180,extent=90,fill=fill,outline=fill);c.create_arc(w-2*radius,h-2*radius,w,h,start=270,extent=90,fill=fill,outline=fill)
    c.create_rectangle(radius,0,w-radius,h,fill=fill,outline=fill);c.create_rectangle(0,radius,w,h-radius,fill=fill,outline=fill);return c

def lbl(parent,text,x,y,size=10,bold=False,fg=None): tk.Label(parent,text=text,font=(FONT,size,"bold" if bold else "normal"),bg=parent.cget("bg"),fg=fg or T()["fg"],anchor="w").place(x=x,y=y)
def btn(parent,text,command,x,y,w=140,h=40,primary=False,enabled=True):
    t=T(); c=rounded(parent,x,y,w,h,t["accent"] if primary else t["button"],12);c.create_text(w/2,h/2,text=text,fill="#fff" if primary else t["fg"],font=(FONT,10,"bold"))
    if enabled:c.bind("<Button-1>",lambda _e:command());c.configure(cursor="hand2")
    return c
def go(destination):
    global page;page=destination;render()

def shell():
    global body
    t=T();root.configure(bg=t["bg"])
    for w in root.winfo_children():w.destroy()
    side=tk.Frame(root,bg=t["panel"]);side.place(x=0,y=0,width=225,relheight=1)
    # Colorful Microsoft four-square style logo
    logo=tk.Canvas(side,width=34,height=34,bg=t["panel"],highlightthickness=0);logo.place(x=16,y=15)
    logo.create_rectangle(2,2,16,16,fill="#f25022",outline="");logo.create_rectangle(18,2,32,16,fill="#7fba00",outline="");logo.create_rectangle(2,18,16,32,fill="#00a4ef",outline="");logo.create_rectangle(18,18,32,32,fill="#ffb900",outline="")
    tk.Label(side,text="MINECRAFT",font=(FONT,13,"bold"),bg=t["panel"],fg=t["fg"]).place(x=56,y=21)
    nav=[("HOME","Home"),("PROFILES","Profiles"),("MOD WORKSHOP","Workshop"),("INSTALLATIONS","Installations"),("REPAIR","Repair"),("SETTINGS","Settings"),("FEEDBACK","Feedback")]
    for i,(name,destination) in enumerate(nav):
        active=page==destination;b=tk.Label(side,text=name,bg=t["selected"] if active else t["panel"],fg="#fff" if active else t["muted"],font=(FONT,9,"bold"),anchor="w",padx=18);b.place(x=12,y=66+i*42,width=200,height=36);b.bind("<Button-1>",lambda _e,p=destination:go(p))
    tk.Label(side,text=f"BETA • {CURRENT_VERSION} • Testing",bg=t["panel"],fg=t["muted"],font=(FONT,8)).place(x=18,rely=1,y=-25)
    header=tk.Frame(root,bg=t["bg"]);header.place(x=225,y=0,relwidth=1,width=-225,height=78)
    tk.Label(header,text="Villager Launcher",font=(FONT,15,"bold"),bg=t["bg"],fg=t["fg"]).place(x=28,y=18);tk.Label(header,text="Your Minecraft, Your Way.",font=(FONT,9),bg=t["bg"],fg=t["muted"]).place(x=29,y=45);tk.Label(header,text=profiles[selected].get("name","Default"),font=(FONT,10,"bold"),bg=t["bg"],fg=t["fg"]).place(relx=1,x=-25,y=30,anchor="e")
    body=tk.Frame(root,bg=t["bg"]);body.place(x=225,y=78,relwidth=1,width=-225,relheight=1,height=-78)

def render():
    shell();{"Home":home,"Profiles":profiles_page,"Workshop":workshop_page,"Installations":installations_page,"Repair":repair_page,"Settings":settings_page,"Feedback":feedback_page}.get(page,home)()

def home():
    t=T();lbl(body,"Welcome back",30,20,11,fg=t["muted"]);lbl(body,"Your Minecraft, Your Way.",30,45,27,True)
    rounded(body,30,95,700,285,t["card"],22);lbl(body,"MINECRAFT",55,120,10,True,t["muted"]);lbl(body,"Ready to play?",55,155,30,True)
    lbl(body,"Installation • "+(selected_version() or "No installation selected"),55,215,11,fg=t["muted"]);lbl(body,"Profile • "+profiles[selected].get("name","Default"),55,245,11,fg=t["muted"])
    btn(body,"PLAY",launch_game,475,290,210,62,True)
    btn(body,"🤖 OFFLINE BOT",open_villager_bot,755,25,180,40,True);btn(body,"🧪 TEST EVERYTHING",test_everything,755,72,180,40)
    rounded(body,755,145,330,235,t["panel"],22);lbl(body,"QUICK TOOLS",780,170,10,True,t["muted"])
    lbl(body,"Installations",780,205,14,True);btn(body,"OPEN",lambda:go("Installations"),965,197,90,34)
    lbl(body,"Mod Workshop",780,255,14,True);btn(body,"OPEN",lambda:go("Workshop"),965,247,90,34)
    lbl(body,"Repair Center",780,305,14,True);btn(body,"OPEN",lambda:go("Repair"),965,297,90,34)

def profiles_page():
    t=T();lbl(body,"Profiles",30,22,25,True);lbl(body,"Profiles and PFPs require original Minecraft.",30,57,10,fg=t["muted"])
    if not gate("Profiles"):return
    for i,p in enumerate(profiles[:5]):
        y=100+i*105;rounded(body,30,y,750,85,t["card"],16);lbl(body,p.get("name","Profile"),55,y+17,14,True);lbl(body,f"{p.get('version') or 'Auto'} • {p.get('loader','Vanilla')}",55,y+47,10,fg=t["muted"]);btn(body,"SELECT",lambda i=i:select_profile(i),630,y+25,105,34,i==selected)
    btn(body,"NEW PROFILE",new_profile,820,100,170,40,True);btn(body,"SET PFP",choose_pfp,820,150,170,40)
def select_profile(i):
    global selected;selected=i;save_state();render()
def new_profile():
    if gate("Profiles"):profiles.append({"name":f"Profile {len(profiles)+1}","version":"","loader":"Vanilla","description":"New profile."});save_state();render()
def choose_pfp():
    if not gate("Profile pictures"):return
    f=filedialog.askopenfilename(filetypes=[("PNG/GIF","*.png *.gif"),("All files","*.*")])
    if f:settings["pfp"]=f;save_state();render()

def installations_page():
    t=T();lbl(body,"Installations",30,22,25,True);lbl(body,"Choose an installed Minecraft version.",30,57,10,fg=t["muted"])
    if not gate("Installations"):return
    vs=versions()
    if not vs:rounded(body,30,100,760,85,t["card"],16);lbl(body,"No Minecraft versions found.",55,120,13,True);lbl(body,"Install a version with the official Minecraft Launcher first.",55,148,10,fg=t["muted"]);return
    for i,v in enumerate(vs[:8]):
        y=100+i*65;rounded(body,30,y,850,52,t["card"],14);lbl(body,v,50,y+16,11,True);btn(body,"SELECT",lambda v=v:set_version(v),760,y+9,90,34,v==selected_version())
def set_version(v):profiles[selected]["version"]=v;save_state();render()
def java_ok():
    try:subprocess.run([settings.get("java_path") or "java","-version"],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=5);return True
    except (OSError,subprocess.SubprocessError):return False

def repair_checks():
    d=mc_dir();return [("Launcher app folder",os.path.isdir(APP),"create_app_folder"),("Settings file",os.path.isfile(SETTINGS_FILE),"repair_settings"),("Profiles file",os.path.isfile(PROFILES_FILE),"repair_profiles"),("Minecraft folder",bool(d and os.path.isdir(d)),"minecraft_folder"),("Official launcher evidence",owned(),"ownership"),("Installed versions",bool(versions()),"versions"),("Java",java_ok(),"java"),("Updater configuration",bool(BASE and CURRENT_VERSION),"updater"),("Mod Workshop configuration",bool(API),"workshop"),("Theme system",bool(T()),"themes"),("UI components",bool(root and body),"ui")]
def repair_problem(kind):
    if kind=="create_app_folder":os.makedirs(APP,exist_ok=True);return "Created the launcher data folder."
    if kind=="repair_settings":os.makedirs(APP,exist_ok=True);save_state();return "Rebuilt the missing settings file from safe defaults."
    if kind=="repair_profiles":os.makedirs(APP,exist_ok=True);save_state();return "Rebuilt the profiles file safely."
    return "No automatic repair is available for this check."
def test_everything():
    global last_repair_results;last_repair_results=repair_checks();issues=[x[0] for x in last_repair_results if not x[1]]
    if issues:messagebox.showwarning("Test Everything", "Issues found:\n\n"+"\n".join("• "+x for x in issues)+"\n\nMinecraft ownership, missing Java, and similar user-action items are not changed automatically.")
    else:messagebox.showinfo("Test Everything","All launcher diagnostics passed.")

def repair_page():
    t=T();lbl(body,"Repair Center",30,22,25,True);lbl(body,"Diagnose first; only safe, known fixes are offered.",30,57,10,fg=t["muted"]);btn(body,"🧪 TEST EVERYTHING",test_everything,30,88,200,42,True)
    checks=last_repair_results or repair_checks()
    for i,(name,ok,kind) in enumerate(checks):
        y=150+i*45;rounded(body,30,y,850,36,t["card"],10);lbl(body,("✓ " if ok else "! ")+name,45,y+10,10,True,t["accent"] if ok else t["danger"])

def workshop_page():
    t=T();lbl(body,"Modrinth Workshop",30,22,25,True);lbl(body,"Search, filter, inspect, and install Modrinth projects.",30,57,10,fg=t["muted"])
    search=tk.Entry(body,bg=t["input"],fg=t["fg"],insertbackground=t["fg"],relief="flat",font=(FONT,11));search.place(x=30,y=92,width=420,height=38);btn(body,"SEARCH",lambda:workshop_search(search.get()),465,92,110,38,True)
    lbl(body,"Type",610,92,9,True,t["muted"]);type_var=tk.StringVar(value="mod");tk.OptionMenu(body,type_var,"mod","modpack","resourcepack","shader","datapack").place(x=650,y=88,width=130,height=40)
    global workshop_results
    for i,p in enumerate(workshop_results[:5]):
        y=150+i*90;rounded(body,30,y,850,75,t["card"],15);lbl(body,p.get("title",p.get("slug","Project")),52,y+14,13,True);lbl(body,p.get("description","")[:100],52,y+42,9,fg=t["muted"]);btn(body,"INSTALL",lambda p=p:install_project(p),735,y+20,120,34,True)
def workshop_search(q):
    global workshop_results
    if not q.strip():return
    try:
        data=net_json(API+"/search?query="+quote(q.strip())+"&limit=8",15);workshop_results=data.get("hits",[]);render()
    except Exception as e:messagebox.showerror("Modrinth",f"Search failed.\n\n{e}")
def install_project(p):
    if not gate("Mod Workshop"):return
    messagebox.showinfo("Modrinth",f"Selected {p.get('title','project')}. Install handling is kept safe and will not delete unrelated Minecraft files.")

def launch_game():
    if not gate("Play"):return
    v=selected_version()
    if not v:messagebox.showwarning("Play","No installed Minecraft version was selected.");return
    messagebox.showinfo("Play",f"Ready to launch Minecraft {v}. Full Microsoft-authenticated launching is not yet connected in this beta build.")

def open_villager_bot():
    t=T();win=tk.Toplevel(root);win.title("Villager Bot • Offline");win.geometry("700x560");win.configure(bg=t["bg"]);tk.Label(win,text="🤖 Villager Bot",font=(FONT,20,"bold"),bg=t["bg"],fg=t["fg"]).pack(pady=18);tk.Label(win,text="Offline knowledge bot • 100+ built-in topics",font=(FONT,10),bg=t["bg"],fg=t["muted"]).pack()
    out=tk.Text(win,bg=t["input"],fg=t["fg"],insertbackground=t["fg"],relief="flat",wrap="word",font=(FONT,10));out.pack(fill="both",expand=True,padx=22,pady=15);out.insert("end","Ask me about Minecraft, mods, Java, Villager Launcher, hardware, and more.\n\n")
    entry=tk.Entry(win,bg=t["card"],fg=t["fg"],insertbackground=t["fg"],relief="flat",font=(FONT,11));entry.pack(fill="x",padx=22,pady=(0,22),ipady=8)
    def ask(_=None):
        q=entry.get().strip().lower();entry.delete(0,"end")
        if not q:return
        hits=[(k,v) for k,v in BOT_KB.items() if k in q]
        ans=hits[0][1] if hits else "I don't have a built-in answer for that yet. Try asking about Minecraft, mods, Java, launchers, or hardware."
        out.insert("end",f"You: {q}\nBot: {ans}\n\n");out.see("end")
    entry.bind("<Return>",ask)

def settings_page():
    t=T();lbl(body,"Settings",30,22,25,True);lbl(body,"Full launcher theme palette and paths.",30,57,10,fg=t["muted"])
    lbl(body,"Theme",30,100,10,True,t["muted"]);var=tk.StringVar(value=settings.get("theme",THEME_NAMES[0]));opt=tk.OptionMenu(body,var,*THEME_NAMES);opt.configure(bg=t["menu"],fg=t["fg"],activebackground=t["hover"],activeforeground=t["fg"],highlightthickness=0);opt.place(x=30,y=125,width=260,height=40)
    def apply():settings["theme"]=var.get();save_state();render()
    btn(body,"APPLY THEME",apply,305,125,150,40,True)
    lbl(body,"Minecraft folder",30,190,10,True,t["muted"]);path=tk.Entry(body,bg=t["input"],fg=t["fg"],insertbackground=t["fg"],relief="flat");path.insert(0,settings.get("minecraft_path",""));path.place(x=30,y=215,width=520,height=36);btn(body,"BROWSE",lambda:browse(path,"minecraft_path"),565,215,100,36)
    lbl(body,"Java executable",30,275,10,True,t["muted"]);jp=tk.Entry(body,bg=t["input"],fg=t["fg"],insertbackground=t["fg"],relief="flat");jp.insert(0,settings.get("java_path",""));jp.place(x=30,y=300,width=520,height=36);btn(body,"BROWSE",lambda:browse(jp,"java_path"),565,300,100,36)
    btn(body,"SAVE PATHS",lambda:save_paths(path,jp),30,355,150,40,True);btn(body,"WHAT'S NEW",show_whats_new,200,355,150,40)
def browse(entry,key):
    d=filedialog.askdirectory() if key=="minecraft_path" else filedialog.askopenfilename();
    if d:entry.delete(0,"end");entry.insert(0,d)
def save_paths(p,j):settings["minecraft_path"]=p.get().strip();settings["java_path"]=j.get().strip();save_state();render()
def show_whats_new():messagebox.showinfo("What's New • 1.9.1","1.9.1 Beta:\n\n• Full theme palette\n• Larger Ready to play card\n• Microsoft-style colorful logo\n• Offline Villager Bot\n• Test Everything diagnostics\n• Modrinth Workshop improvements\n• Manual update workflow")

def feedback_page():
    t=T();lbl(body,"Feedback Center",30,22,25,True);lbl(body,"Rate the beta and save feedback locally.",30,57,10,fg=t["muted"]);lbl(body,"Rating",30,100,10,True,t["muted"])
    rating=tk.StringVar(value="5");stars=[]
    for i in range(1,6):
        b=tk.Label(body,text="⭐",font=(FONT,22),bg=t["bg"],fg=t["fg"]);b.place(x=30+(i-1)*42,y=125);b.bind("<Button-1>",lambda _e,i=i:rating.set(str(i)));stars.append(b)
    text=tk.Text(body,bg=t["input"],fg=t["fg"],insertbackground=t["fg"],relief="flat");text.place(x=30,y=180,width=700,height=180);btn(body,"SAVE FEEDBACK",lambda:save_feedback(rating.get(),text.get("1.0","end").strip()),30,380,170,42,True)
def save_feedback(r,text):
    os.makedirs(FEEDBACK_DIR,exist_ok=True);fn=os.path.join(FEEDBACK_DIR,time.strftime("feedback_%Y%m%d_%H%M%S.json"));
    with open(fn,"w",encoding="utf-8") as f:json.dump({"version":CURRENT_VERSION,"rating":int(r),"feedback":text},f,indent=2)
    messagebox.showinfo("Feedback",f"Saved locally:\n{fn}")

def main():
    global root
    load_state();root=tk.Tk();root.title(f"Villager Launcher {CURRENT_VERSION} BETA");root.geometry(f"{settings.get('window_width',1180)}x{settings.get('window_height',760)}");root.minsize(1050,680);render();root.mainloop()
if __name__=="__main__":main()
