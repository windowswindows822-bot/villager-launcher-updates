import tkinter as tk
from tkinter import messagebox
import os, sys, json, tempfile, subprocess, time
from urllib.request import Request, urlopen

CURRENT_VERSION='1.9.1'
BASE='https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main'
APP=os.path.join(os.environ.get('APPDATA',tempfile.gettempdir()),'VillagerLauncher')
SETTINGS_FILE=os.path.join(APP,'settings.json')

# 1.9.1 beta updater: downloads the new launcher to a temporary file,
# replaces the running launcher after it exits, then starts the new version.
def net_json(url):
    req=Request(url+'?t='+str(time.time_ns()),headers={'User-Agent':f'Villager-Launcher/{CURRENT_VERSION}'})
    with urlopen(req,timeout=15) as r:return json.loads(r.read().decode())

def check_update():
    try:
        info=net_json(BASE+'/version.json')
        latest=str(info.get('version',''))
        if latest and latest != CURRENT_VERSION:
            if messagebox.askyesno('Update available',f'Villager Launcher {latest} is available.\n\nThis is a beta/testing build. Update now?'):
                update_launcher(latest)
        else:
            messagebox.showinfo('Updates','You are already running the latest version.')
    except Exception as e:
        messagebox.showerror('Update failed',f'Could not check for updates.\n\n{e}')

def update_launcher(version):
    try:
        target=os.path.abspath(sys.argv[0])
        if not target.lower().endswith('.py'):
            messagebox.showerror('Update failed','The launcher updater requires the launcher to be running from launcher.py.')
            return
        data=net_json(BASE+'/launcher.py')
        # net_json expects JSON, so fetch the source directly.
        req=Request(BASE+'/launcher.py?t='+str(time.time_ns()),headers={'User-Agent':f'Villager-Launcher/{CURRENT_VERSION}'})
        with urlopen(req,timeout=30) as r: source=r.read().decode('utf-8')
        if f"CURRENT_VERSION='{version}'" not in source and f'CURRENT_VERSION="{version}"' not in source:
            raise RuntimeError('Downloaded launcher version did not match the update metadata.')
        tmp=target+'.update_tmp'
        with open(tmp,'w',encoding='utf-8',newline='') as f:f.write(source)
        # A tiny helper replaces launcher.py only after this process closes.
        helper=target+'.update_helper.py'
        helper_source=f'''import os,time,shutil,subprocess,sys\ntarget={target!r}\ntmp={tmp!r}\nfor _ in range(50):\n    try:\n        if os.path.exists(tmp):\n            os.replace(tmp,target)\n            break\n    except OSError: time.sleep(0.2)\nsubprocess.Popen([sys.executable,target])\ntry: os.remove(__file__)\nexcept OSError: pass\n'''
        with open(helper,'w',encoding='utf-8') as f:f.write(helper_source)
        subprocess.Popen([sys.executable,helper],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        root.destroy()
    except Exception as e:
        messagebox.showerror('Update failed',f'Could not install the update.\n\n{e}')

def load():
    try:
        with open(SETTINGS_FILE,encoding='utf-8') as f:return json.load(f)
    except Exception:return {}

def main():
    global root
    root=tk.Tk(); root.title(f'Villager Launcher {CURRENT_VERSION} BETA'); root.geometry('900x560'); root.configure(bg='#0b120d')
    tk.Label(root,text='⛏ Villager Launcher',font=('Segoe UI',24,'bold'),bg='#0b120d',fg='white').pack(pady=35)
    tk.Label(root,text=f'Version {CURRENT_VERSION} • BETA / TESTING',font=('Segoe UI',13,'bold'),bg='#0b120d',fg='#69d34b').pack()
    tk.Label(root,text='Manual updates only — click below to test the updater.',font=('Segoe UI',11),bg='#0b120d',fg='#a9b9aa').pack(pady=15)
    tk.Button(root,text='CHECK FOR UPDATES',command=check_update,font=('Segoe UI',11,'bold'),padx=20,pady=12).pack(pady=20)
    tk.Button(root,text='EXIT',command=root.destroy,font=('Segoe UI',10),padx=30,pady=8).pack()
    root.mainloop()

if __name__=='__main__':main()
