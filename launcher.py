import tkinter as tk
from tkinter import ttk,messagebox,filedialog,colorchooser
import os,sys,json,tempfile,subprocess,shutil,time,threading
from urllib.request import Request,urlopen
from urllib.parse import quote

CURRENT_VERSION='1.8.5'
BASE='https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main'
API='https://api.modrinth.com/v2'
APP=os.path.join(os.environ.get('APPDATA',tempfile.gettempdir()),'VillagerLauncher')
SET=os.path.join(APP,'settings.json'); PROFILES=os.path.join(APP,'profiles.json')
FONT='Segoe UI Variable'
NAMES=['Villager Green','Midnight','Sky','Nether','Ocean','Dirt','Stone','Diamond','Gold','Redstone','Lapis','Amethyst','Copper','Forest','Cherry Grove','Desert','Snow','Volcano','End','Piglin','Swamp','Plains','Jungle','Ice','Deep Dark','Stronghold','Sunrise','Night','Redstone Lab','Creeper']
COLORS=[('#0e1510','#162119','#203021','#fff','#a9b9aa','#62c462','#2d442d','#c65353'),('#080d17','#111a29','#1a263b','#fff','#a9b5c9','#7188ff','#29385e','#d15c66'),('#dff1fa','#f5fbff','#e8f4fa','#173042','#5c7180','#3a91c9','#c7e0ed','#b64e4e'),('#190b0b','#291212','#3a1a1a','#fff','#d0a8a8','#e05a5a','#542626','#ff8a70'),('#07181f','#0d2833','#123743','#fff','#9fc5d0','#38a7c7','#1b4655','#d45d67'),('#24180f','#352416','#47301e','#fff8ec','#c9b69d','#9b6b43','#60452c','#b94a48'),('#202124','#2c2d30','#393a3d','#f5f5f5','#b9babd','#a0a3a8','#4a4c50','#c65a5a'),('#071d24','#0d3038','#12404a','#f1ffff','#9ac9cf','#59d8e4','#1c5962','#d35c68'),('#211a06','#302707','#40360b','#fffbea','#d2c28a','#e8c84a','#5b4b13','#c45b45'),('#210b0b','#351010','#471818','#fff5f5','#d5aaaa','#f04d4d','#641e1e','#ff7777'),('#08162b','#0d2140','#123058','#f4f8ff','#a5b9d5','#4c83d8','#1d4070','#d45d67'),('#190d26','#28143a','#382052','#fff7ff','#c5a9d5','#b66cde','#513078','#e06a78'),('#24130d','#382016','#4a2b1d','#fff7f1','#d2b0a0','#d77b4d','#67402d','#c9584c'),('#08170d','#102719','#183622','#f4fff5','#a6c5aa','#55b96a','#245b32','#c75a55'),('#260f1b','#3a1727','#4c2034','#fff7fb','#d6adbe','#f083b0','#6b2f4a','#e05d69'),('#261e10','#382d18','#4a3c20','#fffbef','#d0c19b','#d6b45b','#66532b','#c55d4d'),('#dde8f0','#f4f9fc','#e7f0f6','#20313c','#647883','#5a9dc5','#c7dde9','#b65353'),('#1d0905','#30100a','#45170e','#fff8f0','#d4aaa0','#ff713f','#652416','#ff9b50'),('#090610','#150d1e','#21132e','#faf4ff','#bba8c7','#b75be8','#3d2052','#d75d7d'),('#2a1018','#3c1822','#51212d','#fff4f5','#d7aeb5','#e6a06d','#6c3040','#f06a62'),('#111a0d','#1b2913','#26381a','#f5ffe9','#b5c59c','#86b84a','#3c5724','#c45c52'),('#132014','#20351f','#2d4729','#f8fff3','#b2c7a8','#8bc34a','#426332','#c85c55'),('#071a10','#0d2a19','#143923','#f2fff5','#9fc5aa','#39c66a','#1d6038','#c45a5a'),('#071a24','#0d2a38','#123a4b','#f2fcff','#a4c7d2','#6dd6f2','#1e596b','#c65b68'),('#070b0e','#0d1318','#141e24','#e8ffff','#91a8ad','#27d0c0','#173d3b','#c95762'),('#151515','#202020','#2d2d2d','#f5f5f5','#b2b2b2','#c0c0c0','#444','#c45a5a'),('#24100c','#3a1a12','#4c2419','#fff8f1','#d6b0a0','#ff9b5b','#6d3624','#d65d54'),('#050812','#0b1020','#121a2e','#f5f8ff','#9baac8','#6b8cff','#25345e','#c85a6b'),('#130d0c','#211514','#30201e','#fff8f6','#c5a9a4','#ff4f38','#54241d','#ff8270'),('#0a1709','#11230e','#193515','#f5fff0','#aac59e','#69d34b','#2b5b20','#d05b55')]
THEMES={n:dict(zip('bg panel card fg muted accent button danger'.split(),c)) for n,c in zip(NAMES,COLORS)}
DEFAULT={'theme':'Villager Green','minecraft_path':'','java_path':'','window_width':1180,'window_height':760,'pfp':'','confirm_updates':True}
settings=dict(DEFAULT); custom={}; profiles=[]; selected=0; page='Home'; root=None; body=None; status=None; results=[]; images={}

def load():
 global settings,custom,profiles
 d=read(SET,{})
 if isinstance(d,dict):
  settings.update({k:d[k] for k in DEFAULT if k in d}); custom=d.get('custom_themes',{}) if isinstance(d.get('custom_themes',{}),dict) else {}
 profiles=read(PROFILES,[])
 if not isinstance(profiles,list) or not profiles: profiles=[{'name':'Default','version':'','loader':'Vanilla','description':'Your first Villager Launcher profile.'}]
def read(p,d):
 try:
  with open(p,encoding='utf8') as f:return json.load(f)
 except:return d
def save():
 os.makedirs(APP,exist_ok=True)
 with open(SET,'w',encoding='utf8') as f:json.dump({**settings,'theme':settings['theme'],'custom_themes':custom},f,indent=2)
 with open(PROFILES,'w',encoding='utf8') as f:json.dump(profiles,f,indent=2)
def T():return custom.get(settings['theme'],THEMES.get(settings['theme'],THEMES['Villager Green']))
def mc():
 p=settings['minecraft_path'];
 if p and os.path.isdir(p):return p
 a=os.environ.get('APPDATA');return os.path.join(a,'.minecraft') if a else ''
def owned():
 d=mc();return bool(d and os.path.isdir(d) and (os.path.isfile(os.path.join(d,'launcher_accounts.json')) or os.path.isfile(os.path.join(d,'launcher_profiles.json'))))
def gate(feature):
 if owned():return True
 messagebox.showwarning('Minecraft Required',feature+' is locked until an original Minecraft installation is detected. Sign in through the official Minecraft Launcher, then select its Minecraft folder in Settings.')
 return False
def vers():
 d=os.path.join(mc(),'versions')
 try:return sorted([x for x in os.listdir(d) if os.path.isdir(os.path.join(d,x))],reverse=True) if os.path.isdir(d) else []
 except:return []
def version():
 if profiles and profiles[selected].get('version'):return profiles[selected]['version']
 v=vers();return v[0] if v else ''
def api(url,timeout=15):
 r=Request(url+(('&' if '?' in url else '?')+'t='+str(time.time_ns())),headers={'User-Agent':'Villager-Launcher/1.8.5'})
 with urlopen(r,timeout=timeout) as x:return json.loads(x.read().decode())
def card(par,x,y,w,h,fill=None,r=20):
 fill=fill or T()['card']; c=tk.Canvas(par,width=w,height=h,bg=par.cget('bg'),highlightthickness=0);c.place(x=x,y=y)
 c.create_arc(0,0,2*r,2*r,90,90,fill=fill,outline=fill);c.create_arc(w-2*r,0,w,2*r,0,90,fill=fill,outline=fill);c.create_arc(0,h-2*r,2*r,2*r,180,90,fill=fill,outline=fill);c.create_arc(w-2*r,h-2*r,w,h,270,90,fill=fill,outline=fill);c.create_rectangle(r,0,w-r,h,fill=fill,outline=fill);c.create_rectangle(0,r,w,h-r,fill=fill,outline=fill);return c
def lbl(p,text,x,y,size=10,bold=False,fg=None):tk.Label(p,text=text,font=(FONT,size,'bold' if bold else 'normal'),bg=p.cget('bg'),fg=fg or T()['fg'],anchor='w').place(x=x,y=y)
def btn(p,text,cmd,x,y,w=140,h=40,primary=False,enabled=True):
 t=T();c=card(p,x,y,w,h,t['accent'] if primary else t['button'],12);c.create_text(w/2,h/2,text=text,fill='#fff' if primary else t['fg'],font=(FONT,10,'bold'))
 if enabled:c.bind('<Button-1>',lambda e:cmd());c.configure(cursor='hand2')
 return c
def go(p):
 global page;page=p;render()
def shell():
 global body
 t=T();root.configure(bg=t['bg'])
 for w in root.winfo_children():w.destroy()
 s=tk.Frame(root,bg=t['panel']);s.place(x=0,y=0,width=225,relheight=1)
 tk.Label(s,text='⛏  MINECRAFT',font=(FONT,13,'bold'),bg=t['panel'],fg=t['fg']).place(x=18,y=18)
 for i,(n,p) in enumerate([('HOME','Home'),('PROFILES','Profiles'),('MOD WORKSHOP','Workshop'),('INSTALLATIONS','Installations'),('REPAIR','Repair'),('SETTINGS','Settings')]):
  bg=t['accent'] if page==p else t['panel'];fg='#fff' if page==p else t['muted'];b=tk.Label(s,text=n,bg=bg,fg=fg,font=(FONT,10,'bold'),anchor='w',padx=18);b.place(x=12,y=72+i*46,width=200,height=40);b.bind('<Button-1>',lambda e,p=p:go(p))
 tk.Label(s,text=CURRENT_VERSION,bg=t['panel'],fg=t['muted'],font=(FONT,9)).place(x=18,rely=1,y=-25)
 h=tk.Frame(root,bg=t['bg']);h.place(x=225,y=0,relwidth=1,width=-225,height=78)
 tk.Label(h,text='Villager Launcher',font=(FONT,15,'bold'),bg=t['bg'],fg=t['fg']).place(x=28,y=20);tk.Label(h,text='Your Minecraft, Your Way.',font=(FONT,9),bg=t['bg'],fg=t['muted']).place(x=29,y=46)
 tk.Label(h,text=profiles[selected].get('name','Default'),font=(FONT,10,'bold'),bg=t['bg'],fg=t['fg']).place(relx=1,x=-25,y=30,anchor='e')
 body=tk.Frame(root,bg=t['bg']);body.place(x=225,y=78,relwidth=1,width=-225,relheight=1,height=-78)
def render():
 shell();{'Home':home,'Profiles':profiles_page,'Workshop':workshop,'Installations':installations,'Repair':repair,'Settings':settings_page}.get(page,home)()
def home():
 t=T();lbl(body,'Welcome back',11,20,11,False,t['muted']);lbl(body,'Ready to meet your wishes?',30,43,27,True)
 card(body,30,95,700,245);lbl(body,'MINECRAFT',55,120,10,True,t['muted']);lbl(body,'Your Minecraft, Your Way.',55,150,22,True);lbl(body,'Installation  •  '+(version() or 'No installation selected'),55,198,10,False,t['muted']);lbl(body,'Profile  •  '+profiles[selected].get('name','Default'),55,223,10,False,t['muted']);btn(body,'PLAY',launch,500,265,180,54,True)
 for i,(n,p) in enumerate([('Installations','Installations'),('Mod Workshop','Workshop'),('Settings','Settings')]):x=30+i*225;card(body,x,385,205,95,16 and t['panel']);lbl(body,n,x+18,408,11,True);btn(body,'OPEN',lambda p=p:go(p),x+18,440,90,28)
 card(body,755,95,330,245,22,t['panel']);lbl(body,'ACTIVE PROFILE',780,120,10,True,t['muted']);lbl(body,profiles[selected].get('name','Default'),780,155,19,True);lbl(body,'Original Minecraft: '+('Detected' if owned() else 'Not detected'),780,210,10,False,t['accent'] if owned() else t['danger'])
def profiles_page():
 lbl(body,'Profiles',30,22,25,True);lbl(body,'Profiles and PFPs require original Minecraft.',30,57,10,False,T()['muted'])
 if not gate('Profiles'):return
 for i,p in enumerate(profiles):y=100+i*105;card(body,30,y,750,85);lbl(body,p.get('name','Profile'),55,y+18,14,True);lbl(body,(p.get('version') or 'Auto')+'  •  '+p.get('loader','Vanilla'),55,y+47,10,False,T()['muted']);btn(body,'SELECT',lambda i=i:select_profile(i),630,y+25,105,34,i==selected)
 btn(body,'NEW PROFILE',new_profile,820,100,170,40,True);btn(body,'SET PFP',pfp,820,150,170,40)
def select_profile(i):
 global selected;selected=i;save();render()
def new_profile():
 if gate('Profiles'):profiles.append({'name':f'Profile {len(profiles)+1}','version':'','loader':'Vanilla','description':'New profile.'});save();render()
def pfp():
 if gate('Profile pictures'):
  f=filedialog.askopenfilename(filetypes=[('PNG/GIF','*.png *.gif'),('All','*.*')]);
  if f:settings['pfp']=f;save();render()
def installations():
 lbl(body,'Installations',30,22,25,True);lbl(body,'Choose an installed Minecraft version.',30,57,10,False,T()['muted'])
 if not gate('Installations'):return
 for i,v in enumerate(vers()[:8]):y=100+i*65;card(body,30,y,850,52, r=14);lbl(body,v,50,y+16,11,True);btn(body,'USE',lambda v=v:setver(v),760,y+9,90,34,v==version())
def setver(v):profiles[selected]['version']=v;save();render()
def repair():
 lbl(body,'Repair Center',30,22,25,True);lbl(body,'Safe diagnostics. Nothing is deleted automatically.',30,57,10,False,T()['muted'])
 checks=[('Minecraft folder',bool(mc() and os.path.isdir(mc()))),('Launcher evidence',owned()),('Installed versions',bool(vers())),('Java',java_ok())]
 for i,(n,ok) in enumerate(checks):y=105+i*65;card(body,30,y,760,52,r=14);lbl(body,n,50,y+16,11,True);lbl(body,'✓ OK' if ok else '✕ Problem',600,y+16,10,True,T()['accent'] if ok else T()['danger'])
def java_ok():
 try:subprocess.run([settings.get('java_path') or 'java','-version'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=5);return True
 except:return False
def launch():
 if not gate('Minecraft launching'):return
 v=version();d=mc()
 if not v:return error('Version selection','No installed Minecraft version is selected.','Open Installations and select a version.')
 vd=os.path.join(d,'versions',v);meta=os.path.join(vd,v+'.json');jar=os.path.join(vd,v+'.jar')
 if not os.path.isfile(meta):return error('Version metadata','Missing '+v+'.json',meta)
 if not os.path.isfile(jar):return error('Client JAR','Missing '+v+'.jar',jar)
 if not java_ok():return error('Java startup','Java executable could not be started.',settings.get('java_path') or 'java')
 error('Authenticated startup','Authenticated Microsoft launch integration is not enabled in 1.8.5.','Files and Java were checked; no game process was started instead of pretending it launched.')
def error(stage,what,extra=''):messagebox.showerror('Minecraft Launch Error',f'Stage: {stage}\n\nWhat broke: {what}\n\n{extra}\n\nYour Minecraft files were not deleted.')

def workshop():
 lbl(body,'Mod Workshop',30,18,25,True);lbl(body,'Modrinth • browse freely, install only when original Minecraft is detected.',30,53,10,False,T()['muted'])
 q=tk.Entry(body,bg=T()['card'],fg=T()['fg'],insertbackground=T()['fg'],relief='flat',font=(FONT,10));q.place(x=30,y=85,width=310,height=38)
 typ=ttk.Combobox(body,values=['All','Mods','Shaders','Resource Packs','Data Packs'],state='readonly');typ.set('All');typ.place(x=350,y=85,width=140,height=38)
 vv=ttk.Combobox(body,values=['All']+vers(),state='readonly');vv.set('All');vv.place(x=500,y=85,width=130,height=38)
 sort=ttk.Combobox(body,values=['Relevance','Downloads','Updated'],state='readonly');sort.set('Relevance');sort.place(x=640,y=85,width=120,height=38)
 btn(body,'SEARCH',lambda:search_workshop(q.get(),typ.get(),vv.get(),sort.get()),775,85,120,38,True);lbl(body,'INSTALL is locked and intentionally does nothing without original Minecraft.',30,133,9,False,T()['danger'] if not owned() else T()['accent'])
 box=tk.Frame(body,bg=T()['bg']);box.place(x=30,y=160,relwidth=1,width=-60,relheight=1,height=-175);show_results(box)
def show_results(box):
 for w in box.winfo_children():w.destroy()
 for item in results[:10]:
  f=card(box,0,0,1000,92,r=16);f.pack(fill='x',pady=5);name=item.get('title','Project');desc=(item.get('description') or '')[:100];lbl(f,name,22,12,12,True);lbl(f,desc,22,38,9,False,T()['muted']);lbl(f,f"{item.get('project_type','mod')}  •  {item.get('downloads',0):,} downloads",22,65,9,False,T()['muted']);draw_image(f,item.get('icon_url',''));btn(f,'INSTALL' if owned() else 'LOCKED',lambda item=item:install(item),850,27,115,38,owned(),owned())
def draw_image(f,url):
 if not url:return
 lab=tk.Label(f,bg=T()['panel'],text='');lab.place(x=770,y=17,width=55,height=55)
 def work():
  try:
   with urlopen(Request(url,headers={'User-Agent':'Villager-Launcher/1.8.5'}),timeout=8) as r:data=r.read()
   path=os.path.join(tempfile.gettempdir(),'vlimg_'+str(abs(hash(url)))+'.img');open(path,'wb').write(data)
   def ui():
    try:im=tk.PhotoImage(file=path);images[url]=im;lab.configure(image=im)
    except:
     try:
      from PIL import Image,ImageTk;im=Image.open(path);im.thumbnail((52,52));im=ImageTk.PhotoImage(im);images[url]=im;lab.configure(image=im)
     except:lab.configure(text='IMG',fg=T()['muted'])
   root.after(0,ui)
  except:pass
 threading.Thread(target=work,daemon=True).start()
def search_workshop(q,typ,v,sort):
 try:
  facets={'Mods':'mod','Shaders':'shader','Resource Packs':'resourcepack','Data Packs':'datapack'};f=[]
  if typ!='All':f=[[f'project_type:{facets[typ]}']]
  u=f'{API}/search?query={quote(q)}&limit=20&index={sort.lower()}'
  if f:u+='&facets='+quote(json.dumps(f,separators=(',',':')))
  data=api(u).get('hits',[])
  if v!='All':data=[x for x in data if v in x.get('versions',[])]
  global results;results=data;render()
 except Exception as e:messagebox.showerror('Workshop Error',str(e))
def install(item):
 if not gate('Mod Workshop installation'):return
 v=version()
 if not v:return messagebox.showwarning('Workshop','Select an installed Minecraft version first.')
 try:
  data=api(API+'/project/'+quote(item.get('project_id') or item.get('slug'))+'/version');ok=[x for x in data if v in x.get('game_versions',[])]
  if not ok:raise ValueError('No compatible release for Minecraft '+v)
  fs=ok[0].get('files') or [];file=next((x for x in fs if x.get('primary')),fs[0] if fs else None)
  if not file:raise ValueError('No downloadable file was provided.')
  folder={'mod':'mods','shader':'shaderpacks','resourcepack':'resourcepacks','datapack':'datapacks'}.get(item.get('project_type'),'mods');dest=os.path.join(mc(),folder);os.makedirs(dest,exist_ok=True);out=os.path.join(dest,os.path.basename(file['filename']))
  status.set('Downloading…');with_url=urlopen(Request(file['url'],headers={'User-Agent':'Villager-Launcher/1.8.5'}),timeout=60);data=with_url.read();with_url.close();open(out,'wb').write(data)
  if not os.path.isfile(out):raise IOError('Downloaded file was not created.')
  status.set('Installed');messagebox.showinfo('Installed',f"{item.get('title','Project')} installed to {folder}.")
 except Exception as e:status.set('Install failed');messagebox.showerror('Install Failed',f'Stage: Download / install\n\nWhat broke: {e}')

def settings_page():
 lbl(body,'Settings',30,18,25,True);lbl(body,'Updates and Backups stay here, not in the sidebar.',30,53,10,False,T()['muted'])
 card(body,30,85,1040,125);lbl(body,'Appearance',55,108,13,True);lbl(body,'Theme',55,140,10,False,T()['muted']);cb=ttk.Combobox(body,values=NAMES+list(custom),state='readonly');cb.set(settings['theme']);cb.place(x=130,y=136,width=210,height=34);cb.bind('<<ComboboxSelected>>',lambda e:settheme(cb.get()));btn(body,'CUSTOM THEME',theme_editor,360,135,150,36)
 card(body,30,230,500,205);lbl(body,'Minecraft',55,252,13,True);lbl(body,settings['minecraft_path'] or 'Default .minecraft',55,285,9,False,T()['muted']);btn(body,'CHOOSE FOLDER',choose_mc,55,320,140,36);btn(body,'CHOOSE JAVA',choose_java,210,320,130,36)
 card(body,555,230,515,205);lbl(body,'Updates',580,252,13,True);lbl(body,'Installed: '+CURRENT_VERSION,580,285,10,False,T()['muted']);btn(body,'CHECK FOR UPDATES',update_check,580,320,175,38,True)
 card(body,30,455,1040,150);lbl(body,'Backups',55,477,13,True);lbl(body,'Safe launcher-managed mods backups.',55,507,9,False,T()['muted']);btn(body,'CREATE BACKUP',backup,55,540,145,38);btn(body,'OPEN BACKUPS',open_backups,215,540,145,38);btn(body,'RESET SETTINGS',reset,375,540,145,38)
def settheme(v):settings['theme']=v;save();render()
def choose_mc():
 p=filedialog.askdirectory();
 if p:settings['minecraft_path']=p;save();render()
def choose_java():
 p=filedialog.askopenfilename(filetypes=[('Executable','*.exe'),('All','*.*')]);
 if p:settings['java_path']=p;save();render()
def theme_editor():
 w=tk.Toplevel(root);w.title('Custom Theme Editor');w.geometry('520x520');w.configure(bg=T()['bg']);tk.Label(w,text='Custom Theme Editor',font=(FONT,18,'bold'),bg=T()['bg'],fg=T()['fg']).pack(anchor='w',padx=24,pady=20);name=tk.Entry(w,bg=T()['card'],fg=T()['fg'],relief='flat');name.pack(fill='x',padx=24);name.insert(0,'My Theme');vals={k:tk.StringVar(value=T()[k]) for k in 'bg panel card fg muted accent button danger'.split()}
 for k,v in vals.items():
  r=tk.Frame(w,bg=T()['bg']);r.pack(fill='x',padx=24,pady=4);tk.Label(r,text=k.title(),width=12,anchor='w',bg=T()['bg'],fg=T()['fg']).pack(side='left');tk.Entry(r,textvariable=v,bg=T()['card'],fg=T()['fg'],relief='flat',width=14).pack(side='left')
 def save_theme():
  n=name.get().strip() or 'My Theme';custom[n]={k:v.get() for k,v in vals.items()};settings['theme']=n;save();w.destroy();render()
 btn(w,'SAVE THEME',save_theme,0,0,180,40,True).pack(pady=18)
def backup():
 if not gate('Backups'):return
 src=os.path.join(mc(),'mods');
 if not os.path.isdir(src):return messagebox.showinfo('Backup','No mods folder exists yet.')
 d=os.path.join(mc(),'villager_launcher_backups',time.strftime('%Y%m%d_%H%M%S'),'mods');os.makedirs(os.path.dirname(d),exist_ok=True);shutil.copytree(src,d);messagebox.showinfo('Backup Created',d)
def open_backups():
 d=os.path.join(mc() or APP,'villager_launcher_backups');os.makedirs(d,exist_ok=True);os.startfile(d) if hasattr(os,'startfile') else subprocess.Popen(['xdg-open',d])
def reset():
 global settings,custom;settings=dict(DEFAULT);custom={};save();render()
def semver(v):
 try:return tuple(map(int,v.split('.')[:3]))
 except:return (0,0,0)
def update_check():
 try:
  d=api(BASE+'/version.json');v=str(d.get('version',''))
  if semver(v)<=semver(CURRENT_VERSION):return messagebox.showinfo('Updates','You are up to date.')
  if messagebox.askyesno('Update Available',f'Version {v} is available. Update now?'):download_update()
 except Exception as e:messagebox.showerror('Update Error',str(e))
def download_update():
 try:
  data=api_bytes(BASE+'/launcher.py');p=os.path.join(tempfile.gettempdir(),'villager_launcher_update.py');open(p,'wb').write(data);subprocess.Popen([sys.executable,p,'--install-update',os.path.abspath(sys.argv[0])],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),close_fds=True);root.destroy()
 except Exception as e:messagebox.showerror('Update Error',str(e))
def api_bytes(u):
 with urlopen(Request(u+'?t='+str(time.time_ns()),headers={'User-Agent':'Villager-Launcher/1.8.5'}),timeout=30) as r:return r.read()
def startup_notice():
 try:
  d=api(BASE+'/version.json');v=str(d.get('version',''))
  if semver(v)>semver(CURRENT_VERSION):root.after(700,lambda:messagebox.askyesno('Update Available',f'Villager Launcher {v} is available. You have not updated yet. Update now?') and download_update())
 except:pass
def finish_update(target):
 src=os.path.abspath(sys.argv[0]);time.sleep(2)
 for _ in range(30):
  try:shutil.copy2(src,target);subprocess.Popen([sys.executable,target],close_fds=True);os.remove(src);return
  except OSError:time.sleep(1)
 messagebox.showerror('Update Error','Windows could not replace the launcher file.')
def main():
 global root,status
 load()
 if len(sys.argv)>=3 and sys.argv[1]=='--install-update':return finish_update(sys.argv[2])
 root=tk.Tk();root.title('Villager Launcher '+CURRENT_VERSION);root.geometry(f"{settings['window_width']}x{settings['window_height']}");root.minsize(1000,650);status=tk.StringVar(value='Ready');render();startup_notice();root.protocol('WM_DELETE_WINDOW',lambda:(save(),root.destroy()));root.mainloop()
if __name__=='__main__':main()
