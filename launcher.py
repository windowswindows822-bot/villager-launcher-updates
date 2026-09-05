import tkinter as tk
from tkinter import messagebox
import os,sys,tempfile,subprocess,time,json
from urllib.request import Request,urlopen

CURRENT_VERSION='1.9.1'
BASE='https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main'
APP=os.path.join(os.environ.get('APPDATA',tempfile.gettempdir()),'VillagerLauncher')

root=None

def fetch(url,timeout=15):
    req=Request(url+('?t='+str(time.time_ns()) if '?' not in url else '&t='+str(time.time_ns())),headers={'User-Agent':f'Villager-Launcher/{CURRENT_VERSION}'})
    with urlopen(req,timeout=timeout) as r:return r.read().decode('utf-8')

def version_info():
    return json.loads(fetch(BASE+'/version.json'))

def update_launcher(latest):
    try:
        target=os.path.abspath(sys.argv[0])
        if not target.lower().endswith('.py'):
            messagebox.showerror('Update failed','Please run the launcher from launcher.py to update it.')
            return
        source=fetch(BASE+'/launcher.py',30)
        if f"CURRENT_VERSION='{latest}'" not in source and f'CURRENT_VERSION="{latest}"' not in source:
            raise RuntimeError('The downloaded launcher version does not match the update version.')
        tmp=target+'.new'
        with open(tmp,'w',encoding='utf-8') as f:f.write(source)
        helper=target+'.replace.py'
        helper_code=f'''import os,time,subprocess,sys\ntarget={target!r}\ntmp={tmp!r}\nfor _ in range(100):\n    try:\n        os.replace(tmp,target)\n        break\n    except OSError:\n        time.sleep(0.2)\nsubprocess.Popen([sys.executable,target])\ntry: os.remove(__file__)\nexcept OSError: pass\n'''
        with open(helper,'w',encoding='utf-8') as f:f.write(helper_code)
        subprocess.Popen([sys.executable,helper],creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        root.destroy()
    except Exception as e:
        messagebox.showerror('Update failed',str(e))

def show_update_reminder():
    try:
        info=version_info();latest=str(info.get('version',''))
        if latest and latest!=CURRENT_VERSION:
            # Bottom-right reminder only. No popup on startup.
            frame=tk.Frame(root,bg='#1d2c20',highlightthickness=1,highlightbackground='#69d34b')
            frame.place(relx=1,rely=1,x=-18,y=-18,anchor='se',width=330,height=92)
            tk.Label(frame,text=f'⭐ Update available: {latest}',font=('Segoe UI',11,'bold'),bg='#1d2c20',fg='white').place(x=14,y=12)
            tk.Label(frame,text='A beta/testing update is ready.',font=('Segoe UI',9),bg='#1d2c20',fg='#a9b9aa').place(x=14,y=38)
            tk.Button(frame,text='UPDATE',command=lambda:update_launcher(latest)).place(x=230,y=53,width=82,height=28)
            tk.Button(frame,text='×',command=frame.destroy,bd=0,bg='#1d2c20',fg='#a9b9aa').place(x=300,y=4,width=25,height=22)
    except Exception:
        pass

def check_now():
    try:
        info=version_info();latest=str(info.get('version',''))
        if latest and latest!=CURRENT_VERSION:
            if messagebox.askyesno('Update available',f'Villager Launcher {latest} is available.\n\nThis is a beta/testing build. Do you want to update?'):
                update_launcher(latest)
        else: messagebox.showinfo('Updates','You are already running Villager Launcher '+CURRENT_VERSION+'.')
    except Exception as e:messagebox.showerror('Update check failed',str(e))

def main():
    global root
    root=tk.Tk();root.title(f'Villager Launcher {CURRENT_VERSION} BETA');root.geometry('900x560');root.configure(bg='#0b120d')
    tk.Label(root,text='⛏ Villager Launcher',font=('Segoe UI',24,'bold'),bg='#0b120d',fg='white').pack(pady=35)
    tk.Label(root,text=f'Version {CURRENT_VERSION} • BETA / TESTING',font=('Segoe UI',13,'bold'),bg='#0b120d',fg='#69d34b').pack()
    tk.Label(root,text='Updates appear as a bottom-right reminder instead of a startup popup.',font=('Segoe UI',11),bg='#0b120d',fg='#a9b9aa').pack(pady=15)
    tk.Button(root,text='CHECK FOR UPDATES',command=check_now,font=('Segoe UI',11,'bold'),padx=20,pady=12).pack(pady=20)
    tk.Button(root,text='EXIT',command=root.destroy,font=('Segoe UI',10),padx=30,pady=8).pack()
    root.after(1200,show_update_reminder)
    root.mainloop()

if __name__=='__main__':main()
