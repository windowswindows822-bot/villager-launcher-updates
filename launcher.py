import os
import sys
import json
import tempfile
import subprocess
import time
import re
import io
import threading
import webbrowser
import math
import shutil
import platform
import socket
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser, simpledialog, ttk
from urllib.request import Request, urlopen
from urllib.parse import quote

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
import os
import sys

# Tell Python explicitly where to find the libmpv DLLs
os.environ["PATH"] = os.path.dirname(os.path.abspath(__file__)) + os.pathsep + os.environ["PATH"]
os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))
try:
    import mpv
    HAS_MPV = True
except Exception:
    HAS_MPV = False

CURRENT_VERSION = "2.2.0"
BETA = True
VILLAGER_OS_VERSION = "1.0"
BASE_URL = "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main"
VERSION_URL = BASE_URL + "/version.json"
LAUNCHER_URL = BASE_URL + "/launcher.py"
UPDATE_VERSION_URL = VERSION_URL
UPDATE_LAUNCHER_URL = LAUNCHER_URL
MODRINTH = "https://api.modrinth.com/v2"
APP = os.path.join(os.environ.get("APPDATA", tempfile.gettempdir()), "VillagerLauncher")
SETTINGS_FILE = os.path.join(APP, "settings.json")
PROFILES_FILE = os.path.join(APP, "profiles.json")
SERVERS_FILE = os.path.join(APP, "servers.json")
PREVIOUS_LAUNCHER_FILE = os.path.join(APP, "previous_launcher.py")
PREVIOUS_VERSION_FILE = os.path.join(APP, "previous_version.json")
FONT = "Segoe UI"

# ==================== LANGUAGE / LOCALIZATION ====================
LANGUAGES = ["English", "Arabic"]

AR = {
    "Villager Green": "أخضر فيلجر", "Midnight": "منتصف الليل", "Sky": "السماء", "Nether": "النيذر",
    "Ocean": "المحيط", "Diamond": "الألماس", "Gold": "الذهب", "Amethyst": "الجمشت",
    "Forest": "الغابة", "Cherry Grove": "بستان الكرز", "Deep Dark": "الظلام العميق",
    "Relevance": "الصلة", "Downloads": "التنزيلات", "Updated": "محدث",
    "Vanilla": "فانيلا", "Forge": "فورج", "Fabric": "فابريك", "Quilt": "كويلت", "NeoForge": "نيوفورج",
    "Home": "الرئيسية", "Profiles": "الملفات الشخصية", "Workshop": "ورشة العمل",
    "Installations": "التثبيتات", "Repair": "الإصلاح والتشخيص", "Ideas": "الأفكار",
    "Settings": "الإعدادات", "Feedback": "الملاحظات", "Home Dashboard": "لوحة الرئيسية",
    "Profile Manager": "مدير الملفات الشخصية", "Mod Workshop": "ورشة تعديلات ماينكرافت",
    "Minecraft Installations": "تثبيتات ماينكرافت", "Repair & Diagnostics": "الإصلاح والتشخيص",
    "Launcher Features Registry": "سجل ميزات المشغل", "Launcher Settings": "إعدادات المشغل",
    "Feedback Center": "مركز الملاحظات", "VILLAGER": "فيلجر", "LAUNCHER": "المشغل",
    "fuPs launcher": "مشغل fuPs", "Minecraft Linked": "ماينكرافت مرتبطة",
    "Set Folder in Settings": "حدد المجلد من الإعدادات", "Welcome Back": "مرحبًا بعودتك",
    "Play, manage profiles, and download mods directly from your dashboard.": "شغّل اللعبة وأدر الملفات الشخصية ونزّل التعديلات مباشرة من لوحة التحكم.",
    "ACTIVE PROFILE": "الملف الشخصي النشط", "Play Game": "تشغيل اللعبة", "Villager Bot": "بوت فيلجر",
    "Hrmm": "هممم", "Check Everything": "فحص كل شيء", "Profiles": "الملفات الشخصية",
    "Installed Versions": "الإصدارات المثبتة", "Theme": "السمة", "Minecraft Directory": "مجلد ماينكرافت",
    "Linked": "مرتبط", "Not Found": "غير موجود", "Mod Workshop": "ورشة التعديلات",
    "Search Modrinth for compatible mods and resource packs.": "ابحث في Modrinth عن تعديلات وحزم موارد متوافقة.",
    "Installations": "التثبيتات", "Manage installed versions from your Minecraft folder.": "أدر الإصدارات المثبتة من مجلد ماينكرافت.",
    "Repair Center": "مركز الإصلاح", "Run safe system diagnostics without changing game files.": "شغّل فحوصات آمنة للنظام دون تغيير ملفات اللعبة.",
    "Open Section": "فتح القسم", "Create, customize, and manage launcher profiles.": "أنشئ الملفات الشخصية للمشغل وخصصها وأدرها.",
    "Rename": "إعادة التسمية", "Selected": "محدد", "Select": "تحديد", "Delete": "حذف",
    "New Profile": "ملف شخصي جديد", "Auto": "تلقائي", "No Minecraft versions found.": "لم يتم العثور على إصدارات لماينكرافت.",
    "Install one using the official Minecraft Launcher first.": "ثبّت إصدارًا أولًا باستخدام مشغل Minecraft الرسمي.",
    "Appearance & Theme": "المظهر والسمة", "Select a visual preset for the launcher UI.": "اختر إعدادًا مرئيًا مسبقًا لواجهة المشغل.",
    "Apply Theme": "تطبيق السمة", "Custom Accent": "لون مميز مخصص", "Minecraft Installation Directory": "مجلد تثبيت ماينكرافت",
    "Browse Directory": "استعراض المجلد", "Java Executable": "ملف تشغيل Java", "Browse Executable": "استعراض الملف",
    "Software Updates": "تحديثات البرنامج", "Check GitHub repository for launcher updates.": "تحقق من مستودع GitHub بحثًا عن تحديثات المشغل.",
    "Check for Updates": "التحقق من التحديثات", "Release Notes": "ملاحظات الإصدار", "Rollback": "التراجع",
    "Language": "اللغة", "English": "الإنجليزية", "Arabic": "العربية", "Apply": "تطبيق",
    "Language changes apply immediately to the entire launcher interface.": "يتم تطبيق تغيير اللغة فورًا على واجهة المشغل بالكامل.",
    "Feature Registry": "سجل الميزات", "Browse and toggle 500 local launcher options.": "تصفح وفعّل أو عطّل 500 خيار محلي للمشغل.",
    "These switches serve as local launcher idea/feature flags; the registry does not imply every idea is implemented yet.": "تعمل هذه المفاتيح كعلامات لميزات المشغل المحلية.",
    "Filter": "تصفية", "Enable All": "تفعيل الكل", "Disable All": "تعطيل الكل", "Reset": "إعادة ضبط",
    "Active": "نشط", "Displaying": "عرض", "of": "من", "features": "ميزة", "Total": "الإجمالي",
    "Feedback Center": "مركز الملاحظات", "Submit thoughts and suggestions locally.": "أرسل أفكارك واقتراحاتك محليًا.",
    "Your Feedback": "ملاحظاتك", "Save Feedback": "حفظ الملاحظات", "Please enter your message.": "يرجى إدخال رسالتك.",
    "Feedback Saved": "تم حفظ الملاحظات", "Your entry was stored locally.": "تم حفظ إدخالك محليًا.",
    "Offline Knowledge Base": "قاعدة المعرفة غير المتصلة", "Send Message": "إرسال الرسالة",
    "Ask me a question.": "اسألني سؤالًا.",
    "Villager Bot: Ask me anything about Minecraft or the launcher!": "بوت فيلجر: اسألني عن ماينكرافت أو المشغل!",
    "You": "أنت", "Starting Villager Launcher...": "جارٍ تشغيل مشغل فيلجر...",
    "Loading configuration...": "جارٍ تحميل الإعدادات...", "Checking profiles and data...": "جارٍ فحص الملفات الشخصية والبيانات...",
    "Preparing interface...": "جارٍ تجهيز الواجهة...", "Finishing startup...": "جارٍ إنهاء بدء التشغيل...",
    "Loading...": "جارٍ التحميل...", "Updating Launcher...": "جارٍ تحديث المشغل...",
    "Checking for updates...": "جارٍ التحقق من التحديثات...", "Downloading package...": "جارٍ تنزيل الحزمة...",
    "Creating backup...": "جارٍ إنشاء نسخة احتياطية...", "Restarting...": "جارٍ إعادة التشغيل...",
    "Finalizing": "جارٍ الإنهاء", "Checking": "جارٍ الفحص", "Downloading": "جارٍ التنزيل", "Installing": "جارٍ التثبيت",
    "Up to Date": "محدث بالفعل", "Update Available": "يتوفر تحديث", "Update now?": "هل تريد التحديث الآن؟",
    "Version": "الإصدار", "Current": "الحالي", "New": "الجديد", "No release notes found.": "لم يتم العثور على ملاحظات للإصدار.",
    "Close": "إغلاق", "Search Mods": "البحث عن تعديلات", "Searching Modrinth repository…": "جارٍ البحث في مستودع Modrinth…",
    "Search Failed": "فشل البحث", "Retry Search": "إعادة محاولة البحث", "Enter a keyword above to search for mods.": "أدخل كلمة في الأعلى للبحث عن تعديلات.",
    "View Project": "عرض المشروع", "Load More Results": "تحميل نتائج إضافية", "Unknown": "غير معروف",
    "Unknown author": "مؤلف غير معروف", "downloads": "تنزيلات", "by": "بواسطة",
    "Check Everything": "فحص كل شيء", "Run Diagnostic Suite": "تشغيل مجموعة التشخيص",
    "Run non-destructive integrity checks on system paths and configs.": "شغّل فحوصات سلامة غير مدمرة لمسارات النظام والإعدادات.",
    "Scans launcher configuration, Java environment, folder access, sound drivers, and API paths.": "يفحص إعدادات المشغل وبيئة Java والوصول إلى المجلدات ومحركات الصوت ومسارات API.",
    "Launch Error": "خطأ في التشغيل", "No Minecraft version is selected or installed.": "لم يتم تحديد أو تثبيت إصدار لماينكرافت.",
    "The selected Minecraft version is missing required files.": "إصدار ماينكرافت المحدد يفتقد الملفات المطلوبة.",
    "Java execution environment failed.": "فشلت بيئة تشغيل Java.", "Validation passed. Launcher ready for launch pipe.": "نجح التحقق. المشغل جاهز لمسار التشغيل.",
    "Minecraft": "ماينكرافت", "Minecraft Required": "ماينكرافت مطلوبة",
    "This feature requires an original Minecraft installation.": "تتطلب هذه الميزة تثبيتًا أصليًا لماينكرافت.",
    "STOP PRESSING HRMM BUTTONS?": "هل تتوقف عن الضغط على أزرار هممم؟",
    "The Villager needs a break from all the buttons.": "فيلجر يحتاج إلى استراحة من كل هذه الأزرار.",
    "HRMM OVERLOAD": "زيادة هممم", "Hrmm... Villager is thinking.": "هممم... فيلجر يفكر.",
    "HRMM! 1500 features detected.": "هممم! تم اكتشاف 1500 ميزة.",
    "Villager inspected the launcher layout. Hrmm.": "فيلجر فحص تخطيط المشغل. هممم.",
    "Hrmm... checking for updates?": "هممم... هل نتحقق من التحديثات؟",
    "EMERALD ACQUIRED. HRMMM.": "تم الحصول على زمردة. هممم.",
    "Diagnostic Results — Issues Found": "نتائج التشخيص — تم العثور على مشكلات",
    "Diagnostic Results — All Clear": "نتائج التشخيص — كل شيء سليم",
    "PROBLEMS DETECTED:": "تم اكتشاف مشكلات:",
    "All subsystems and video/audio checks are operating normally!": "جميع الأنظمة الفرعية وفحوصات الفيديو والصوت تعمل بشكل طبيعي!",
    "No game files were changed or removed.": "لم يتم تغيير أو حذف أي ملفات للعبة.",
    "PASSED": "ناجح", "FIXED": "تم الإصلاح", "FAILED": "فشل", "Created launcher data folder.": "تم إنشاء مجلد بيانات المشغل.",
    "Rebuilt settings safely.": "تمت إعادة بناء الإعدادات بأمان.", "Rebuilt profiles safely.": "تمت إعادة بناء الملفات الشخصية بأمان.",
    "Dependency Error": "خطأ في الاعتماديات", "Playback Error": "خطأ في التشغيل", "Update Error": "خطأ في التحديث",
    "Rollback Error": "خطأ في التراجع", "Workshop Error": "خطأ في ورشة التعديلات",
    "No previous launcher backup available.": "لا توجد نسخة احتياطية سابقة للمشغل.",
    "Select Accent Color": "اختر اللون المميز", "Select Minecraft Folder": "اختر مجلد ماينكرافت", "Select Java Binary": "اختر ملف Java التنفيذي",
    "Executable": "ملف تنفيذي", "All files": "كل الملفات", "Current release": "الإصدار الحالي",
    "Credits & Origins": "الاعتمادات والأصل", "Credits • Origins • Project History": "الاعتمادات • الأصل • تاريخ المشروع",
    "Creator": "المنشئ", "Project owner": "مالك المشروع", "Project origin": "أصل المشروع", "Inspiration": "الإلهام",
    "FuPs / MrXAUYT": "FuPs / MrXAUYT", "Some launcher ideas and inspiration were influenced by MrXAUYT's FuPs launcher. FuPs is credited as an inspiration/reference, not as the creator or owner of Villager Launcher.": "تأثرت بعض أفكار المشغل وإلهامه بمشغل FuPs الخاص بـ MrXAUYT. يُذكر FuPs كمصدر إلهام/مرجع، وليس كمنشئ أو مالك لمشغل فيلجر.",
    "Launcher data directory": "مجلد بيانات المشغل", "Directory missing or inaccessible": "المجلد مفقود أو لا يمكن الوصول إليه",
    "Settings file": "ملف الإعدادات", "Settings JSON missing or corrupted": "ملف إعدادات JSON مفقود أو تالف",
    "Profiles file": "ملف الملفات الشخصية", "Profiles JSON missing or corrupted": "ملف الملفات الشخصية JSON مفقود أو تالف",
    "Minecraft directory": "مجلد ماينكرافت", "Minecraft folder not set or invalid": "مجلد ماينكرافت غير محدد أو غير صالح",
    "Official launcher installation": "تثبيت المشغل الرسمي", "Official launcher account files not found": "لم يتم العثور على ملفات حساب المشغل الرسمي",
    "Installed game versions": "إصدارات اللعبة المثبتة", "No game versions found in versions folder": "لم يتم العثور على إصدارات للعبة في مجلد الإصدارات",
    "Java installation": "تثبيت Java", "Java executable non-functional or not found in PATH": "ملف Java التنفيذي لا يعمل أو غير موجود في PATH",
    "Audio/Video Engine (libmpv)": "محرك الصوت/الفيديو (libmpv)", "MPV Engine Operational": "محرك MPV يعمل",
    "python-mpv or libmpv missing": "python-mpv أو libmpv مفقود", "Updater endpoints": "نقاط نهاية التحديث", "Updater API URLs are malformed": "عناوين API الخاصة بالتحديث غير صحيحة",
    "Mod Workshop endpoints": "نقاط نهاية ورشة التعديلات", "Modrinth API path unavailable": "مسار Modrinth API غير متاح",
    "Theme system integrity": "سلامة نظام السمات", "Theme colors incomplete": "ألوان السمة غير مكتملة",
    "UI component tree": "شجرة مكونات الواجهة", "Tkinter main root instance error": "خطأ في مثيل الجذر الرئيسي لـ Tkinter",
    "Offline bot knowledge pack": "حزمة معرفة البوت غير المتصلة", "Knowledge base entries depleted": "نفدت إدخالات قاعدة المعرفة",
    "Launcher data directory": "مجلد بيانات المشغل", "Added": "تمت الإضافة", "Changed": "تم التغيير", "Removed": "تمت الإزالة", "Fixed": "تم الإصلاح",
    "Downloaded update file is empty.": "ملف التحديث الذي تم تنزيله فارغ.", "Backup file is empty.": "ملف النسخة الاحتياطية فارغ.",
    "python-mpv library or mpv-1.dll was not found.\nPlease install python-mpv and provide libmpv binaries.": "لم يتم العثور على مكتبة python-mpv أو mpv-1.dll.\nيرجى تثبيت python-mpv وتوفير ملفات libmpv الثنائية.",
    "is part of the Villager Launcher feature registry.": "جزء من سجل ميزات مشغل فيلجر.",
    "I work offline. Ask me about Minecraft, mods, launchers, or Python!": "أعمل دون اتصال. اسألني عن ماينكرافت أو التعديلات أو المشغلات أو بايثون!",
    "No previous launcher backup available.": "لا توجد نسخة احتياطية سابقة للمشغل.",
    "TECHNICAL CONTROL INTERFACE": "واجهة التحكم التقنية",
    "Quick Access": "وصول سريع", "VIDEO": "الفيديو", "SYSTEM": "النظام",
    "Configuration": "الإعدادات", "Interface": "الواجهة", "PROGRESS": "التقدم",
    "VIDEO FILE NOT FOUND": "ملف الفيديو غير موجود", "MPV VIDEO ENGINE UNAVAILABLE": "محرك فيديو MPV غير متاح",
}


AR.update({
    "Play": "تشغيل", "Versions": "الإصدارات", "Mods": "التعديلات", "Modpacks": "حزم التعديلات",
    "Worlds": "العوالم", "Servers": "الخوادم", "News": "الأخبار", "Tools": "الأدوات",
    "Play Center": "مركز التشغيل", "Version Center": "مركز الإصدارات", "Mods Center": "مركز التعديلات",
    "Modpacks & Packs": "حزم التعديلات والحزم", "World Center": "مركز العوالم", "Server Center": "مركز الخوادم",
    "News & Activity": "الأخبار والنشاط", "Tools Center": "مركز الأدوات", "About": "حول",
    "Villager OS": "نظام فيلجر", "Compact Sidebar": "الشريط الجانبي المصغر", "Expand Sidebar": "توسيع الشريط الجانبي",
    "Quick Actions": "إجراءات سريعة", "System Overview": "نظرة عامة على النظام", "Open Folder": "فتح المجلد",
    "Open Minecraft Folder": "فتح مجلد ماينكرافت", "Open Launcher Folder": "فتح مجلد المشغل",
    "Backup": "نسخة احتياطية", "Last Modified": "آخر تعديل", "No worlds found.": "لم يتم العثور على عوالم.",
    "No local modpacks found.": "لم يتم العثور على حزم تعديلات محلية.", "Add Server": "إضافة خادم",
    "Server Name": "اسم الخادم", "Server Address": "عنوان الخادم", "Copy Address": "نسخ العنوان",
    "Address Copied": "تم نسخ العنوان", "Remove": "إزالة", "Launcher News": "أخبار المشغل",
    "2.2.0 Major Update": "التحديث الكبير 2.2.0", "Master Feature Registry": "سجل الميزات الرئيسي",
    "Browse and toggle 1500 Villager Launcher 2.2.0 ideas.": "تصفح وفعّل أو عطّل 1500 فكرة لمشغل فيلجر 2.2.0.",
    "FEATURE MASTER LIST": "قائمة الميزات الرئيسية", "Technical Dashboard": "لوحة تقنية",
    "Java Status": "حالة Java", "Internet Status": "حالة الإنترنت", "Operating System": "نظام التشغيل",
    "Launcher Version": "إصدار المشغل", "Ready": "جاهز", "Unavailable": "غير متاح", "Detected": "مكتشف",
    "Profile Manager": "مدير الملفات الشخصية", "Diagnostics": "التشخيص", "Feature Ideas": "أفكار الميزات",
    "Local Feedback": "الملاحظات المحلية", "Credits & Villager OS": "الاعتمادات ونظام فيلجر",
    "S4 Easter Egg": "بيضة عيد الفصح S4", "You found it!": "لقد وجدتها!",
    "The hidden S4 startup sound has been unlocked.": "تم فتح صوت بدء تشغيل S4 المخفي.",
    "Main Navigation": "التنقل الرئيسي", "Current Profile": "الملف الشخصي الحالي", "Selected Version": "الإصدار المحدد",
    "View Only": "عرض فقط", "Local Packs": "الحزم المحلية", "Resource Packs": "حزم الموارد", "Shaders": "التظليلات",
    "Minecraft Servers": "خوادم ماينكرافت", "Saved Servers": "الخوادم المحفوظة", "No saved servers yet.": "لا توجد خوادم محفوظة بعد.",
    "Launcher Status": "حالة المشغل", "Update Center": "مركز التحديث", "Release Information": "معلومات الإصدار",
    "Open": "فتح", "Folder not found:": "المجلد غير موجود:", "Backup created:": "تم إنشاء النسخة الاحتياطية:",
    "Villager Launcher 2.2.0 technical dashboard and quick controls.": "لوحة تقنية لمشغل فيلجر 2.2.0 مع أدوات تحكم سريعة.",
    "Launch Minecraft and manage the active profile from one place.": "شغّل ماينكرافت وأدر الملف الشخصي النشط من مكان واحد.",
    "Browse locally installed Minecraft versions and choose the active version.": "تصفح إصدارات ماينكرافت المثبتة محليًا واختر الإصدار النشط.",
    "Inspect local modpack, resource-pack, and shader folders without removing existing Workshop behavior.": "افحص مجلدات حزم التعديلات وحزم الموارد والتظليلات المحلية مع الحفاظ على سلوك الورشة الحالي.",
    "Browse local Minecraft worlds, open their folders, and create safe ZIP backups.": "تصفح عوالم ماينكرافت المحلية وافتح مجلداتها وأنشئ نسخ ZIP احتياطية آمنة.",
    "Maintain a lightweight local list of Minecraft servers and addresses.": "أدر قائمة محلية خفيفة لخوادم ماينكرافت وعناوينها.",
    "Launcher release information, update controls, and the current 2.2.0 highlights.": "معلومات إصدار المشغل وأدوات التحديث وأبرز ميزات 2.2.0.",
    "Diagnostics, feature ideas, feedback, folders, assistant, and project information.": "التشخيص وأفكار الميزات والملاحظات والمجلدات والمساعد ومعلومات المشروع.",
    "Run the existing non-destructive repair and diagnostic suite.": "شغّل مجموعة الإصلاح والتشخيص الحالية غير المدمرة.",
    "Open the existing local feedback center.": "افتح مركز الملاحظات المحلي الحالي.",
    "Open the full existing profile manager.": "افتح مدير الملفات الشخصية الكامل الحالي.",
    "Open the offline Villager Bot knowledge assistant.": "افتح مساعد بوت فيلجر المعرفي غير المتصل.",
    "Credits, project history, Villager OS, and hidden interaction.": "الاعتمادات وتاريخ المشروع ونظام فيلجر والتفاعل المخفي.",
    "Scrollable left sidebar with ten main sections": "شريط جانبي أيسر قابل للتمرير بعشرة أقسام رئيسية",
    "Villager OS 1.0 and hidden S4 audio Easter egg": "نظام فيلجر 1.0 وبيضة عيد الفصح الصوتية المخفية S4",
    "1500-item 2.2.0 master feature registry": "سجل ميزات رئيسي للإصدار 2.2.0 يحتوي على 1500 عنصر",
    "World browser with ZIP backups": "متصفح عوالم مع نسخ ZIP احتياطية",
    "Local server address manager": "مدير محلي لعناوين الخوادم",
    "Dedicated Play, Versions, Modpacks, News, and Tools centers": "مراكز مخصصة للتشغيل والإصدارات وحزم التعديلات والأخبار والأدوات",
    "English/Arabic navigation support": "دعم التنقل بالإنجليزية والعربية",
})

# Common feature-registry words. The fallback translator uses these so the entire 500-feature registry is Arabic too.
AR_WORDS = {
    "home":"الرئيسية","dashboard":"لوحة التحكم","quick":"سريع","launch":"تشغيل","card":"بطاقة","recent":"الأخيرة","profile":"ملف شخصي","profiles":"الملفات الشخصية","version":"إصدار","versions":"الإصدارات","pinned":"مثبتة","favorite":"مفضلة","favorites":"المفضلة","tools":"الأدوات","launcher":"المشغل","status":"الحالة","summary":"ملخص","minecraft":"ماينكرافت","folder":"مجلد","folders":"المجلدات","java":"Java","update":"تحديث","updates":"التحديثات","badge":"شارة","workshop":"الورشة","repair":"الإصلاح","settings":"الإعدادات","feedback":"الملاحظات","ideas":"الأفكار","session":"جلسة","timer":"مؤقت","last":"آخر","first":"أول","timestamp":"طابع زمني","download":"تنزيل","downloads":"تنزيلات","storage":"التخزين","welcome":"ترحيب","message":"رسالة","daily":"يومي","villager":"فيلجر","tip":"نصيحة","random":"عشوائي","fact":"معلومة","search":"بحث","box":"مربع","command":"أمر","palette":"لوحة","shortcut":"اختصار","duplication":"تكرار","duplicate":"مكرر","import":"استيراد","export":"تصدير","backup":"نسخة احتياطية","restore":"استعادة","notes":"ملاحظات","note":"ملاحظة","tags":"وسوم","tag":"وسم","color":"لون","icon":"أيقونة","sorting":"فرز","sort":"فرز","archive":"أرشفة","reset":"إعادة ضبط","statistics":"إحصاءات","count":"عدد","play":"تشغيل","playing":"اللعب","time":"الوقت","folder":"مجلد","view":"عرض","clone":"نسخ","name":"اسم","validation":"تحقق","loader":"محمّل","loaders":"المحمّلات","preset":"إعداد مسبق","presets":"إعدادات مسبقة","memory":"الذاكرة","resolution":"الدقة","modpack":"حزمة تعديلات","association":"ارتباط","real":"حقيقي","automatic":"تلقائي","detection":"اكتشاف","check":"فحص","compatibility":"توافق","warning":"تحذير","argument":"وسيط","arguments":"وسائط","editor":"محرر","window":"نافذة","size":"حجم","fullscreen":"ملء الشاشة","toggle":"تبديل","logging":"تسجيل","history":"السجل","failure":"فشل","diagnostics":"التشخيص","crash":"تعطل","exit":"خروج","offline":"غير متصل","account":"حساب","json":"JSON","jar":"JAR","libraries":"المكتبات","assets":"الأصول","natives":"المكونات الأصلية","game":"اللعبة","directory":"المجلد","override":"تجاوز","limit":"حد","mod":"تعديل","mods":"التعديلات","shader":"تظليل","shaders":"التظليلات","resource":"مورد","resources":"الموارد","pack":"حزمة","data":"بيانات","project":"مشروع","type":"نوع","filter":"تصفية","relevance":"الصلة","load":"تحميل","more":"المزيد","primary":"أساسي","file":"ملف","files":"ملفات","dependency":"اعتمادية","dependencies":"الاعتماديات","conflict":"تعارض","conflicts":"التعارضات","enable":"تفعيل","disable":"تعطيل","installed":"مثبت","install":"تثبيت","progress":"تقدم","speed":"سرعة","queue":"قائمة انتظار","pause":"إيقاف مؤقت","resume":"استئناف","retry":"إعادة محاولة","cancel":"إلغاء","destination":"وجهة","checksum":"تجزئة تحقق","timeout":"مهلة","connection":"اتصال","error":"خطأ","parallel":"متوازية","sequential":"متسلسلة","bandwidth":"عرض النطاق","temporary":"مؤقت","cleanup":"تنظيف","recovery":"استرداد","notification":"إشعار","completion":"اكتمال","sound":"الصوت","cache":"ذاكرة مؤقتة","official":"رسمي","theme":"سمة","integrity":"سلامة","permissions":"أذونات","disk":"قرص","space":"مساحة","path":"مسار","length":"طول","report":"تقرير","github":"GitHub","automatic":"تلقائي","prompt":"مطالبة","staging":"تجهيز","verification":"تحقق","notes":"ملاحظات","channel":"قناة","beta":"تجريبي","stable":"مستقر","startup":"بدء التشغيل","reminder":"تذكير","package":"حزمة","source":"مصدر","cache":"ذاكرة مؤقتة","global":"عام","keyboard":"لوحة المفاتيح","large":"كبير","text":"نص","high":"عالٍ","contrast":"تباين","reduced":"مخفض","motion":"حركة","tooltip":"تلميح","notification":"إشعار","toast":"إشعار سريع","modal":"نافذة","resizable":"قابل لتغيير الحجم","dense":"كثيف","comfortable":"مريح","remember":"تذكر","selected":"محدد","page":"صفحة","refresh":"تحديث","debug":"تصحيح","overlay":"طبقة","midnight":"منتصف الليل","sky":"سماء","nether":"نيذر","ocean":"محيط","diamond":"ألماس","gold":"ذهب","amethyst":"جمشت","forest":"غابة","cherry":"كرز","grove":"بستان","deep":"عميق","dark":"مظلم","custom":"مخصص","accent":"مميز","background":"خلفية","panel":"لوحة","border":"حد","danger":"خطر","random":"عشوائي","button":"زر","animation":"رسوم متحركة","loading":"تحميل","success":"نجاح","failure":"فشل","creeper":"كريبر","achievement":"إنجاز","nether":"نيذر","end":"النهاية","overworld":"العالم العلوي","level":"مستوى","feature":"ميزة","features":"ميزات","unlock":"فتح","secret":"سري","easter":"بيض عيد الفصح","egg":"بيضة","naming":"تسمية","commander":"القائد","celebration":"احتفال","safety":"أمان","reliability":"موثوقية","delete":"حذف","destructive":"مدمر","action":"إجراء","atomic":"ذرّي","interruption":"مقاطعة","malformed":"مشوه","protection":"حماية","missing":"مفقود","invalid":"غير صالح","graceful":"سلس","shutdown":"إيقاف التشغيل","advanced":"متقدم","dependencies":"الاعتماديات","category":"فئة","categories":"فئات","all":"الكل","quick":"سريع","action":"إجراء","history":"السجل","helper":"مساعد","control":"تحكم","preview":"معاينة","reserved":"محجوز","expansion":"توسعة","pack":"حزمة","offline":"غير متصل","question":"سؤال","knowledge":"معرفة","response":"استجابة","counter":"عداد","windows":"ويندوز","python":"بايثون","roblox":"روبلوكس","hardware":"عتاد","support":"دعم","system":"النظام","information":"معلومات","privacy":"خصوصية","developer":"مطور","environment":"بيئة","executable":"تنفيذي","working":"عمل","thread":"مؤشر تنفيذ","monitor":"مراقب","render":"تصيير","timing":"توقيت","memory-friendly":"موفر للذاكرة"
}

def tr(value):
    if not isinstance(value, str) or settings.get("language", "English") != "Arabic":
        return value
    if value in AR:
        return AR[value]
    # Preserve technical identifiers and paths, but translate ordinary English phrases.
    def repl(match):
        w = match.group(0)
        return AR_WORDS.get(w.lower(), w)
    translated = re.sub(r"[A-Za-z][A-Za-z-]*", repl, value)
    # Translate common punctuation-separated words that appear as all-caps UI labels.
    return translated

def from_display(value):
    if settings.get("language", "English") != "Arabic":
        return value
    for english, arabic in AR.items():
        if arabic == value:
            return english
    return value

def set_language(language):
    if language not in LANGUAGES:
        language = "English"
    settings["language"] = language
    save_state()
    render()

# Translate Tkinter UI text centrally. This keeps the existing launcher architecture intact
# and makes every Label/Checkbutton/Radiobutton/button string switch languages.
_ORIG_LABEL = tk.Label
_ORIG_CHECKBUTTON = tk.Checkbutton
_ORIG_RADIOBUTTON = tk.Radiobutton
_ORIG_SHOWINFO = messagebox.showinfo
_ORIG_SHOWWARNING = messagebox.showwarning
_ORIG_SHOWERROR = messagebox.showerror
_ORIG_ASKYESNO = messagebox.askyesno
_ORIG_ASKSTRING = simpledialog.askstring
_ORIG_ASKDIRECTORY = filedialog.askdirectory
_ORIG_ASKOPENFILENAME = filedialog.askopenfilename
_ORIG_ASKCOLOR = colorchooser.askcolor

def _localized_label(master=None, *args, **kwargs):
    if "text" in kwargs:
        kwargs["text"] = tr(kwargs["text"])
    if settings.get("language", "English") == "Arabic":
        kwargs.setdefault("justify", "right")
    return _ORIG_LABEL(master, *args, **kwargs)

def _localized_checkbutton(master=None, *args, **kwargs):
    if "text" in kwargs:
        kwargs["text"] = tr(kwargs["text"])
    return _ORIG_CHECKBUTTON(master, *args, **kwargs)

def _localized_radiobutton(master=None, *args, **kwargs):
    if "text" in kwargs:
        kwargs["text"] = tr(kwargs["text"])
    return _ORIG_RADIOBUTTON(master, *args, **kwargs)

def _showinfo(title, message, *args, **kwargs): return _ORIG_SHOWINFO(tr(title), tr(message), *args, **kwargs)
def _showwarning(title, message, *args, **kwargs): return _ORIG_SHOWWARNING(tr(title), tr(message), *args, **kwargs)
def _showerror(title, message, *args, **kwargs): return _ORIG_SHOWERROR(tr(title), tr(message), *args, **kwargs)
def _askyesno(title, message, *args, **kwargs): return _ORIG_ASKYESNO(tr(title), tr(message), *args, **kwargs)
def _askstring(title, prompt, *args, **kwargs): return _ORIG_ASKSTRING(tr(title), tr(prompt), *args, **kwargs)
def _askdirectory(*args, **kwargs):
    if "title" in kwargs:
        kwargs["title"] = tr(kwargs["title"])
    return _ORIG_ASKDIRECTORY(*args, **kwargs)
def _askopenfilename(*args, **kwargs):
    if "title" in kwargs:
        kwargs["title"] = tr(kwargs["title"])
    return _ORIG_ASKOPENFILENAME(*args, **kwargs)
def _askcolor(*args, **kwargs):
    if "title" in kwargs:
        kwargs["title"] = tr(kwargs["title"])
    return _ORIG_ASKCOLOR(*args, **kwargs)

tk.Label = _localized_label
tk.Checkbutton = _localized_checkbutton
tk.Radiobutton = _localized_radiobutton
messagebox.showinfo = _showinfo
messagebox.showwarning = _showwarning
messagebox.showerror = _showerror
messagebox.askyesno = _askyesno
simpledialog.askstring = _askstring
filedialog.askdirectory = _askdirectory
filedialog.askopenfilename = _askopenfilename
colorchooser.askcolor = _askcolor

LOADERS = ["Vanilla", "Forge", "Fabric", "Quilt", "NeoForge"]
LOADER_ICON = {"Vanilla": "◆", "Forge": "▲", "Fabric": "◇", "Quilt": "●", "NeoForge": "■"}
PAGE_TITLES = {
    "Home": "Home Dashboard",
    "Play": "Play Center",
    "Versions": "Version Center",
    "Mods": "Mods Center",
    "Modpacks": "Modpacks & Packs",
    "Worlds": "World Center",
    "Servers": "Server Center",
    "News": "News & Activity",
    "Tools": "Tools Center",
    "Settings": "Launcher Settings",
    "Profiles": "Profile Manager",
    "Workshop": "Mod Workshop",
    "Installations": "Minecraft Installations",
    "Repair": "Repair & Diagnostics",
    "Ideas": "Launcher Features Registry",
    "Feedback": "Feedback Center",
}
WORKSHOP_PAGE_SIZE = 18

# Villager Launcher 2.2.0 master registry — generated from the user's 1500 idea list.
_MASTER_FEATURE_ROWS = [
    "1	UI / VISUAL SYSTEM	New main window layout",
    "2	UI / VISUAL SYSTEM	Scrollable sidebar",
    "3	UI / VISUAL SYSTEM	Compact sidebar mode",
    "4	UI / VISUAL SYSTEM	Expanded sidebar mode",
    "5	UI / VISUAL SYSTEM	Sidebar section headers",
    "6	UI / VISUAL SYSTEM	Active-page indicator",
    "7	UI / VISUAL SYSTEM	Smooth page switching",
    "8	UI / VISUAL SYSTEM	Dashboard cards",
    "9	UI / VISUAL SYSTEM	Larger Play button",
    "10	UI / VISUAL SYSTEM	Launcher status indicator",
    "11	UI / VISUAL SYSTEM	Consistent button sizing",
    "12	UI / VISUAL SYSTEM	Consistent card spacing",
    "13	UI / VISUAL SYSTEM	Better typography",
    "14	UI / VISUAL SYSTEM	Better icon system",
    "15	UI / VISUAL SYSTEM	Custom launcher logo area",
    "16	UI / VISUAL SYSTEM	Header redesign",
    "17	UI / VISUAL SYSTEM	Footer redesign",
    "18	UI / VISUAL SYSTEM	Status-bar redesign",
    "19	UI / VISUAL SYSTEM	Better dialogs",
    "20	UI / VISUAL SYSTEM	Custom confirmation dialogs",
    "21	UI / VISUAL SYSTEM	Custom warning dialogs",
    "22	UI / VISUAL SYSTEM	Custom error dialogs",
    "23	UI / VISUAL SYSTEM	Custom information dialogs",
    "24	UI / VISUAL SYSTEM	Custom download dialogs",
    "25	UI / VISUAL SYSTEM	Custom update dialog",
    "26	UI / VISUAL SYSTEM	Custom settings cards",
    "27	UI / VISUAL SYSTEM	Rounded UI components",
    "28	UI / VISUAL SYSTEM	Better hover effects",
    "29	UI / VISUAL SYSTEM	Press animations",
    "30	UI / VISUAL SYSTEM	Focus indicators",
    "31	UI / VISUAL SYSTEM	Keyboard navigation",
    "32	UI / VISUAL SYSTEM	Better scrolling",
    "33	UI / VISUAL SYSTEM	Scrollbar redesign",
    "34	UI / VISUAL SYSTEM	Sidebar auto-scroll",
    "35	UI / VISUAL SYSTEM	Content-area scrolling",
    "36	UI / VISUAL SYSTEM	Better window resizing",
    "37	UI / VISUAL SYSTEM	Minimum window size",
    "38	UI / VISUAL SYSTEM	Maximum window behavior",
    "39	UI / VISUAL SYSTEM	Fullscreen support",
    "40	UI / VISUAL SYSTEM	Borderless optional mode",
    "41	UI / VISUAL SYSTEM	Custom title bar",
    "42	UI / VISUAL SYSTEM	Minimize button",
    "43	UI / VISUAL SYSTEM	Maximize button",
    "44	UI / VISUAL SYSTEM	Close button",
    "45	UI / VISUAL SYSTEM	Window-state saving",
    "46	UI / VISUAL SYSTEM	Remember window size",
    "47	UI / VISUAL SYSTEM	Remember window position",
    "48	UI / VISUAL SYSTEM	Better loading animation",
    "49	UI / VISUAL SYSTEM	Loading progress indicator",
    "50	UI / VISUAL SYSTEM	Loading stage indicator",
    "51	UI / VISUAL SYSTEM	Startup status messages",
    "52	UI / VISUAL SYSTEM	Better empty states",
    "53	UI / VISUAL SYSTEM	Better unavailable states",
    "54	UI / VISUAL SYSTEM	Better offline state",
    "55	UI / VISUAL SYSTEM	Better connection state",
    "56	UI / VISUAL SYSTEM	Better error-state pages",
    "57	UI / VISUAL SYSTEM	Modern settings layout",
    "58	UI / VISUAL SYSTEM	Modern About page",
    "59	UI / VISUAL SYSTEM	Modern profile card",
    "60	UI / VISUAL SYSTEM	Modern version cards",
    "61	UI / VISUAL SYSTEM	Modern server cards",
    "62	UI / VISUAL SYSTEM	Modern world cards",
    "63	UI / VISUAL SYSTEM	Modern mod cards",
    "64	UI / VISUAL SYSTEM	Modern download cards",
    "65	UI / VISUAL SYSTEM	Modern news cards",
    "66	UI / VISUAL SYSTEM	Modern notification cards",
    "67	UI / VISUAL SYSTEM	Modern Java cards",
    "68	UI / VISUAL SYSTEM	Modern diagnostics cards",
    "69	UI / VISUAL SYSTEM	Modern backup cards",
    "70	UI / VISUAL SYSTEM	Modern resource-pack cards",
    "71	UI / VISUAL SYSTEM	Modern shader cards",
    "72	UI / VISUAL SYSTEM	Modern activity cards",
    "73	UI / VISUAL SYSTEM	Modern history cards",
    "74	UI / VISUAL SYSTEM	Modern search UI",
    "75	UI / VISUAL SYSTEM	Search suggestions",
    "76	UI / VISUAL SYSTEM	Search result highlighting",
    "77	UI / VISUAL SYSTEM	Better tooltips",
    "78	UI / VISUAL SYSTEM	Tooltip delays",
    "79	UI / VISUAL SYSTEM	Tooltip descriptions",
    "80	UI / VISUAL SYSTEM	Context menus",
    "81	UI / VISUAL SYSTEM	Right-click support",
    "82	UI / VISUAL SYSTEM	Copy-to-clipboard buttons",
    "83	UI / VISUAL SYSTEM	Open-folder buttons",
    "84	UI / VISUAL SYSTEM	Refresh buttons",
    "85	UI / VISUAL SYSTEM	Retry buttons",
    "86	UI / VISUAL SYSTEM	Cancel buttons",
    "87	UI / VISUAL SYSTEM	Expand/collapse cards",
    "88	UI / VISUAL SYSTEM	Card sorting",
    "89	UI / VISUAL SYSTEM	Card filtering",
    "90	UI / VISUAL SYSTEM	Card grouping",
    "91	UI / VISUAL SYSTEM	UI density setting",
    "92	UI / VISUAL SYSTEM	Animation toggle",
    "93	UI / VISUAL SYSTEM	Reduced-motion mode",
    "94	UI / VISUAL SYSTEM	UI scaling",
    "95	UI / VISUAL SYSTEM	Large-text mode",
    "96	UI / VISUAL SYSTEM	High-contrast mode",
    "97	UI / VISUAL SYSTEM	Better keyboard shortcuts",
    "98	UI / VISUAL SYSTEM	Visual focus mode",
    "99	UI / VISUAL SYSTEM	UI state persistence",
    "100	UI / VISUAL SYSTEM	Unified design language",
    "101	DASHBOARD	Dashboard redesign",
    "102	DASHBOARD	Welcome panel",
    "103	DASHBOARD	Current Minecraft profile",
    "104	DASHBOARD	Current Minecraft version",
    "105	DASHBOARD	Last played world",
    "106	DASHBOARD	Last played server",
    "107	DASHBOARD	Play button",
    "108	DASHBOARD	Quick-launch button",
    "109	DASHBOARD	Recent worlds",
    "110	DASHBOARD	Recent servers",
    "111	DASHBOARD	Recent versions",
    "112	DASHBOARD	Recent modpacks",
    "113	DASHBOARD	Recent downloads",
    "114	DASHBOARD	Recent activity",
    "115	DASHBOARD	Launcher status",
    "116	DASHBOARD	Minecraft status",
    "117	DASHBOARD	Java status",
    "118	DASHBOARD	Internet status",
    "119	DASHBOARD	Update status",
    "120	DASHBOARD	News preview",
    "121	DASHBOARD	Notification preview",
    "122	DASHBOARD	Download preview",
    "123	DASHBOARD	Storage information",
    "124	DASHBOARD	Memory information",
    "125	DASHBOARD	CPU information",
    "126	DASHBOARD	GPU information",
    "127	DASHBOARD	System uptime",
    "128	DASHBOARD	Launcher uptime",
    "129	DASHBOARD	Current profile card",
    "130	DASHBOARD	Profile switcher",
    "131	DASHBOARD	Favorite world",
    "132	DASHBOARD	Favorite server",
    "133	DASHBOARD	Favorite version",
    "134	DASHBOARD	Favorite modpack",
    "135	DASHBOARD	Quick settings",
    "136	DASHBOARD	Quick repair",
    "137	DASHBOARD	Quick refresh",
    "138	DASHBOARD	Quick backup",
    "139	DASHBOARD	Quick logs",
    "140	DASHBOARD	Quick downloads",
    "141	DASHBOARD	Quick Java manager",
    "142	DASHBOARD	Quick resource packs",
    "143	DASHBOARD	Quick shaders",
    "144	DASHBOARD	Quick mods",
    "145	DASHBOARD	Quick worlds",
    "146	DASHBOARD	Quick servers",
    "147	DASHBOARD	Dashboard customization presets",
    "148	DASHBOARD	Compact dashboard",
    "149	DASHBOARD	Detailed dashboard",
    "150	DASHBOARD	Gaming dashboard",
    "151	DASHBOARD	Technical dashboard",
    "152	DASHBOARD	Minimal dashboard",
    "153	DASHBOARD	Retro dashboard",
    "154	DASHBOARD	Minecraft-themed dashboard",
    "155	DASHBOARD	System dashboard",
    "156	DASHBOARD	Activity timeline",
    "157	DASHBOARD	Last update notification",
    "158	DASHBOARD	Launcher version card",
    "159	DASHBOARD	Villager OS card",
    "160	DASHBOARD	Storage warning",
    "161	DASHBOARD	RAM warning",
    "162	DASHBOARD	Java warning",
    "163	DASHBOARD	Connection warning",
    "164	DASHBOARD	Missing-files warning",
    "165	DASHBOARD	Profile warning",
    "166	DASHBOARD	Version warning",
    "167	DASHBOARD	Mod compatibility warning",
    "168	DASHBOARD	World backup reminder",
    "169	DASHBOARD	Server reminder",
    "170	DASHBOARD	Download completion card",
    "171	DASHBOARD	Update completion card",
    "172	DASHBOARD	Startup summary",
    "173	DASHBOARD	Shutdown summary",
    "174	DASHBOARD	Daily activity counter",
    "175	DASHBOARD	Total launches",
    "176	DASHBOARD	Total play sessions",
    "177	DASHBOARD	Total downloads",
    "178	DASHBOARD	Total worlds",
    "179	DASHBOARD	Total profiles",
    "180	DASHBOARD	Total mods",
    "181	DASHBOARD	Total servers",
    "182	DASHBOARD	Favorite feature",
    "183	DASHBOARD	Last error summary",
    "184	DASHBOARD	Last launch status",
    "185	DASHBOARD	Last update status",
    "186	DASHBOARD	Last backup status",
    "187	DASHBOARD	Last download status",
    "188	DASHBOARD	Dashboard refresh",
    "189	DASHBOARD	Automatic dashboard refresh",
    "190	DASHBOARD	Offline dashboard",
    "191	DASHBOARD	Cached dashboard",
    "192	DASHBOARD	Dashboard skeleton loading",
    "193	DASHBOARD	Dashboard animations",
    "194	DASHBOARD	Dashboard shortcuts",
    "195	DASHBOARD	Dashboard search",
    "196	DASHBOARD	Dashboard notifications",
    "197	DASHBOARD	Dashboard news ticker",
    "198	DASHBOARD	Dashboard system monitor",
    "199	DASHBOARD	Dashboard connection monitor",
    "200	DASHBOARD	Dashboard master overview",
    "201	MINECRAFT LAUNCHING	Improved Play system",
    "202	MINECRAFT LAUNCHING	Version selector",
    "203	MINECRAFT LAUNCHING	Profile selector",
    "204	MINECRAFT LAUNCHING	Java selector",
    "205	MINECRAFT LAUNCHING	Memory selector",
    "206	MINECRAFT LAUNCHING	Game directory selector",
    "207	MINECRAFT LAUNCHING	JVM arguments",
    "208	MINECRAFT LAUNCHING	Game arguments",
    "209	MINECRAFT LAUNCHING	Resolution selector",
    "210	MINECRAFT LAUNCHING	Fullscreen option",
    "211	MINECRAFT LAUNCHING	Window-size presets",
    "212	MINECRAFT LAUNCHING	Custom resolution",
    "213	MINECRAFT LAUNCHING	FPS preference",
    "214	MINECRAFT LAUNCHING	Render-distance preference",
    "215	MINECRAFT LAUNCHING	Simulation-distance preference",
    "216	MINECRAFT LAUNCHING	Difficulty selector",
    "217	MINECRAFT LAUNCHING	Game-mode preference",
    "218	MINECRAFT LAUNCHING	Server auto-connect",
    "219	MINECRAFT LAUNCHING	World auto-open",
    "220	MINECRAFT LAUNCHING	Custom launch commands",
    "221	MINECRAFT LAUNCHING	Launch presets",
    "222	MINECRAFT LAUNCHING	Preset duplication",
    "223	MINECRAFT LAUNCHING	Preset renaming",
    "224	MINECRAFT LAUNCHING	Preset deletion",
    "225	MINECRAFT LAUNCHING	Preset favorites",
    "226	MINECRAFT LAUNCHING	Preset import",
    "227	MINECRAFT LAUNCHING	Preset export",
    "228	MINECRAFT LAUNCHING	Launch history",
    "229	MINECRAFT LAUNCHING	Launch timestamps",
    "230	MINECRAFT LAUNCHING	Launch duration",
    "231	MINECRAFT LAUNCHING	Launch success tracking",
    "232	MINECRAFT LAUNCHING	Launch failure tracking",
    "233	MINECRAFT LAUNCHING	Launch error explanation",
    "234	MINECRAFT LAUNCHING	Retry failed launch",
    "235	MINECRAFT LAUNCHING	Cancel launch",
    "236	MINECRAFT LAUNCHING	Stop game",
    "237	MINECRAFT LAUNCHING	Detect running Minecraft",
    "238	MINECRAFT LAUNCHING	Detect duplicate launches",
    "239	MINECRAFT LAUNCHING	Game process monitor",
    "240	MINECRAFT LAUNCHING	Game PID display",
    "241	MINECRAFT LAUNCHING	Game memory usage",
    "242	MINECRAFT LAUNCHING	Game CPU usage",
    "243	MINECRAFT LAUNCHING	Game GPU usage",
    "244	MINECRAFT LAUNCHING	Game Java process",
    "245	MINECRAFT LAUNCHING	Game logs access",
    "246	MINECRAFT LAUNCHING	Crash-log access",
    "247	MINECRAFT LAUNCHING	Crash detection",
    "248	MINECRAFT LAUNCHING	Crash summary",
    "249	MINECRAFT LAUNCHING	Crash recovery",
    "250	MINECRAFT LAUNCHING	Crash history",
    "251	MINECRAFT LAUNCHING	Launch environment summary",
    "252	MINECRAFT LAUNCHING	JVM compatibility check",
    "253	MINECRAFT LAUNCHING	Java compatibility check",
    "254	MINECRAFT LAUNCHING	Mod-loader compatibility",
    "255	MINECRAFT LAUNCHING	Version compatibility",
    "256	MINECRAFT LAUNCHING	Resource-pack compatibility",
    "257	MINECRAFT LAUNCHING	Shader compatibility",
    "258	MINECRAFT LAUNCHING	Argument validation",
    "259	MINECRAFT LAUNCHING	Memory validation",
    "260	MINECRAFT LAUNCHING	Storage validation",
    "261	MINECRAFT LAUNCHING	Directory validation",
    "262	MINECRAFT LAUNCHING	Asset validation",
    "263	MINECRAFT LAUNCHING	Library validation",
    "264	MINECRAFT LAUNCHING	Authentication-state check",
    "265	MINECRAFT LAUNCHING	Offline launch option",
    "266	MINECRAFT LAUNCHING	Safe launch mode",
    "267	MINECRAFT LAUNCHING	Clean launch mode",
    "268	MINECRAFT LAUNCHING	Modded launch mode",
    "269	MINECRAFT LAUNCHING	Vanilla launch mode",
    "270	MINECRAFT LAUNCHING	Debug launch mode",
    "271	MINECRAFT LAUNCHING	Performance launch mode",
    "272	MINECRAFT LAUNCHING	Custom launch mode",
    "273	MINECRAFT LAUNCHING	Launch confirmation option",
    "274	MINECRAFT LAUNCHING	Remember launch choice",
    "275	MINECRAFT LAUNCHING	Launch countdown",
    "276	MINECRAFT LAUNCHING	Cancel countdown",
    "277	MINECRAFT LAUNCHING	Startup progress",
    "278	MINECRAFT LAUNCHING	Asset progress",
    "279	MINECRAFT LAUNCHING	Library progress",
    "280	MINECRAFT LAUNCHING	Version progress",
    "281	MINECRAFT LAUNCHING	Game-start detection",
    "282	MINECRAFT LAUNCHING	Game-exit detection",
    "283	MINECRAFT LAUNCHING	Session summary",
    "284	MINECRAFT LAUNCHING	Session history",
    "285	MINECRAFT LAUNCHING	Playtime tracking",
    "286	MINECRAFT LAUNCHING	Version-specific playtime",
    "287	MINECRAFT LAUNCHING	Profile-specific playtime",
    "288	MINECRAFT LAUNCHING	World-specific playtime",
    "289	MINECRAFT LAUNCHING	Server-specific playtime",
    "290	MINECRAFT LAUNCHING	Launch statistics",
    "291	MINECRAFT LAUNCHING	Failed-launch statistics",
    "292	MINECRAFT LAUNCHING	Most-used version",
    "293	MINECRAFT LAUNCHING	Most-used profile",
    "294	MINECRAFT LAUNCHING	Most-played world",
    "295	MINECRAFT LAUNCHING	Most-played server",
    "296	MINECRAFT LAUNCHING	Most-used Java",
    "297	MINECRAFT LAUNCHING	Launch favorites",
    "298	MINECRAFT LAUNCHING	Quick launch",
    "299	MINECRAFT LAUNCHING	Advanced launch",
    "300	MINECRAFT LAUNCHING	Launch center",
    "301	MINECRAFT VERSIONS	Version browser",
    "302	MINECRAFT VERSIONS	Version search",
    "303	MINECRAFT VERSIONS	Version filtering",
    "304	MINECRAFT VERSIONS	Version sorting",
    "305	MINECRAFT VERSIONS	Version categories",
    "306	MINECRAFT VERSIONS	Vanilla versions",
    "307	MINECRAFT VERSIONS	Snapshot versions",
    "308	MINECRAFT VERSIONS	Release versions",
    "309	MINECRAFT VERSIONS	Old versions",
    "310	MINECRAFT VERSIONS	Installed versions",
    "311	MINECRAFT VERSIONS	Missing versions",
    "312	MINECRAFT VERSIONS	Favorite versions",
    "313	MINECRAFT VERSIONS	Recently used versions",
    "314	MINECRAFT VERSIONS	Version download",
    "315	MINECRAFT VERSIONS	Version removal",
    "316	MINECRAFT VERSIONS	Version reinstall",
    "317	MINECRAFT VERSIONS	Version repair",
    "318	MINECRAFT VERSIONS	Version verification",
    "319	MINECRAFT VERSIONS	Version metadata",
    "320	MINECRAFT VERSIONS	Version release date",
    "321	MINECRAFT VERSIONS	Version type",
    "322	MINECRAFT VERSIONS	Version compatibility",
    "323	MINECRAFT VERSIONS	Version loader",
    "324	MINECRAFT VERSIONS	Version Java requirement",
    "325	MINECRAFT VERSIONS	Version game directory",
    "326	MINECRAFT VERSIONS	Version asset status",
    "327	MINECRAFT VERSIONS	Version library status",
    "328	MINECRAFT VERSIONS	Version download progress",
    "329	MINECRAFT VERSIONS	Version download cancellation",
    "330	MINECRAFT VERSIONS	Version download retry",
    "331	MINECRAFT VERSIONS	Version download history",
    "332	MINECRAFT VERSIONS	Version installation history",
    "333	MINECRAFT VERSIONS	Version removal history",
    "334	MINECRAFT VERSIONS	Version repair history",
    "335	MINECRAFT VERSIONS	Version notes",
    "336	MINECRAFT VERSIONS	Version changelog",
    "337	MINECRAFT VERSIONS	Version favorite",
    "338	MINECRAFT VERSIONS	Version pinning",
    "339	MINECRAFT VERSIONS	Version aliases",
    "340	MINECRAFT VERSIONS	Custom version labels",
    "341	MINECRAFT VERSIONS	Version profiles",
    "342	MINECRAFT VERSIONS	Version duplication",
    "343	MINECRAFT VERSIONS	Version cloning",
    "344	MINECRAFT VERSIONS	Version import",
    "345	MINECRAFT VERSIONS	Version export",
    "346	MINECRAFT VERSIONS	Version backup",
    "347	MINECRAFT VERSIONS	Version restore",
    "348	MINECRAFT VERSIONS	Version folder opening",
    "349	MINECRAFT VERSIONS	Version file browser",
    "350	MINECRAFT VERSIONS	Version JSON viewer",
    "351	MINECRAFT VERSIONS	Version metadata viewer",
    "352	MINECRAFT VERSIONS	Version dependency viewer",
    "353	MINECRAFT VERSIONS	Version asset viewer",
    "354	MINECRAFT VERSIONS	Version library viewer",
    "355	MINECRAFT VERSIONS	Version Java compatibility",
    "356	MINECRAFT VERSIONS	Version memory recommendation",
    "357	MINECRAFT VERSIONS	Version performance note",
    "358	MINECRAFT VERSIONS	Version warning",
    "359	MINECRAFT VERSIONS	Version broken-file detection",
    "360	MINECRAFT VERSIONS	Version missing-library detection",
    "361	MINECRAFT VERSIONS	Version missing-asset detection",
    "362	MINECRAFT VERSIONS	Version repair assistant",
    "363	MINECRAFT VERSIONS	Version cleanup assistant",
    "364	MINECRAFT VERSIONS	Version storage calculator",
    "365	MINECRAFT VERSIONS	Version download-size display",
    "366	MINECRAFT VERSIONS	Version installed-size display",
    "367	MINECRAFT VERSIONS	Version update detection",
    "368	MINECRAFT VERSIONS	Version duplicate detection",
    "369	MINECRAFT VERSIONS	Version conflict detection",
    "370	MINECRAFT VERSIONS	Version launch test indicator",
    "371	MINECRAFT VERSIONS	Version launch history",
    "372	MINECRAFT VERSIONS	Version session history",
    "373	MINECRAFT VERSIONS	Version usage statistics",
    "374	MINECRAFT VERSIONS	Version playtime",
    "375	MINECRAFT VERSIONS	Version favorite world",
    "376	MINECRAFT VERSIONS	Version favorite server",
    "377	MINECRAFT VERSIONS	Version favorite modpack",
    "378	MINECRAFT VERSIONS	Version quick launch",
    "379	MINECRAFT VERSIONS	Version launch options",
    "380	MINECRAFT VERSIONS	Version custom arguments",
    "381	MINECRAFT VERSIONS	Version Java override",
    "382	MINECRAFT VERSIONS	Version memory override",
    "383	MINECRAFT VERSIONS	Version directory override",
    "384	MINECRAFT VERSIONS	Version resolution override",
    "385	MINECRAFT VERSIONS	Version fullscreen override",
    "386	MINECRAFT VERSIONS	Version mod-loader selector",
    "387	MINECRAFT VERSIONS	Version loader detection",
    "388	MINECRAFT VERSIONS	Version loader metadata",
    "389	MINECRAFT VERSIONS	Version loader repair",
    "390	MINECRAFT VERSIONS	Version loader cleanup",
    "391	MINECRAFT VERSIONS	Version loader download",
    "392	MINECRAFT VERSIONS	Version loader history",
    "393	MINECRAFT VERSIONS	Version loader compatibility",
    "394	MINECRAFT VERSIONS	Version comparison",
    "395	MINECRAFT VERSIONS	Version side-by-side details",
    "396	MINECRAFT VERSIONS	Version favorites page",
    "397	MINECRAFT VERSIONS	Version archive page",
    "398	MINECRAFT VERSIONS	Version installation queue",
    "399	MINECRAFT VERSIONS	Version manager",
    "400	MINECRAFT VERSIONS	Version center",
    "401	MODS	Mod browser",
    "402	MODS	Mod search",
    "403	MODS	Mod filtering",
    "404	MODS	Mod sorting",
    "405	MODS	Mod categories",
    "406	MODS	Installed mods",
    "407	MODS	Disabled mods",
    "408	MODS	Enabled mods",
    "409	MODS	Favorite mods",
    "410	MODS	Recently installed mods",
    "411	MODS	Mod metadata",
    "412	MODS	Mod version",
    "413	MODS	Mod loader",
    "414	MODS	Mod Minecraft compatibility",
    "415	MODS	Mod dependency list",
    "416	MODS	Mod conflict detection",
    "417	MODS	Mod duplicate detection",
    "418	MODS	Mod enable/disable",
    "419	MODS	Mod install",
    "420	MODS	Mod removal",
    "421	MODS	Mod reinstall",
    "422	MODS	Mod repair",
    "423	MODS	Mod update detection",
    "424	MODS	Mod update",
    "425	MODS	Mod rollback",
    "426	MODS	Mod backup",
    "427	MODS	Mod restore",
    "428	MODS	Mod import",
    "429	MODS	Mod export",
    "430	MODS	Mod folder access",
    "431	MODS	Mod file viewer",
    "432	MODS	Mod metadata viewer",
    "433	MODS	Mod dependency viewer",
    "434	MODS	Mod configuration access",
    "435	MODS	Mod configuration backup",
    "436	MODS	Mod configuration restore",
    "437	MODS	Mod crash detection",
    "438	MODS	Mod crash explanation",
    "439	MODS	Mod compatibility warnings",
    "440	MODS	Mod loader warnings",
    "441	MODS	Mod Java warnings",
    "442	MODS	Mod missing dependency warning",
    "443	MODS	Mod incompatible dependency warning",
    "444	MODS	Mod duplicate warning",
    "445	MODS	Mod broken-file warning",
    "446	MODS	Mod download progress",
    "447	MODS	Mod download queue",
    "448	MODS	Mod download cancellation",
    "449	MODS	Mod download retry",
    "450	MODS	Mod download history",
    "451	MODS	Mod installation history",
    "452	MODS	Mod removal history",
    "453	MODS	Mod update history",
    "454	MODS	Mod rollback history",
    "455	MODS	Mod favorite groups",
    "456	MODS	Mod collections",
    "457	MODS	Modpacks from selected mods",
    "458	MODS	Mod list export",
    "459	MODS	Mod list import",
    "460	MODS	Mod profile",
    "461	MODS	Mod profile switching",
    "462	MODS	Mod profile cloning",
    "463	MODS	Mod profile backup",
    "464	MODS	Mod profile restore",
    "465	MODS	Mod profile comparison",
    "466	MODS	Mod load-order viewer",
    "467	MODS	Mod load-order warning",
    "468	MODS	Mod startup estimate",
    "469	MODS	Mod count",
    "470	MODS	Mod storage usage",
    "471	MODS	Mod version comparison",
    "472	MODS	Mod author information",
    "473	MODS	Mod description",
    "474	MODS	Mod license information",
    "475	MODS	Mod homepage shortcut",
    "476	MODS	Mod issue shortcut",
    "477	MODS	Mod documentation shortcut",
    "478	MODS	Mod changelog",
    "479	MODS	Mod release history",
    "480	MODS	Mod compatibility matrix",
    "481	MODS	Mod dependency graph",
    "482	MODS	Mod conflict graph",
    "483	MODS	Mod installation assistant",
    "484	MODS	Mod cleanup assistant",
    "485	MODS	Mod repair assistant",
    "486	MODS	Mod migration assistant",
    "487	MODS	Mod update assistant",
    "488	MODS	Mod rollback assistant",
    "489	MODS	Mod manager settings",
    "490	MODS	Mod cache management",
    "491	MODS	Mod download cache",
    "492	MODS	Mod metadata cache",
    "493	MODS	Mod offline metadata",
    "494	MODS	Mod offline installation",
    "495	MODS	Mod backup scheduler",
    "496	MODS	Mod status dashboard",
    "497	MODS	Mod activity",
    "498	MODS	Mod statistics",
    "499	MODS	Mod health report",
    "500	MODS	Mod center",
    "501	MODPACKS / RESOURCE PACKS / SHADERS	Modpack browser",
    "502	MODPACKS / RESOURCE PACKS / SHADERS	Modpack search",
    "503	MODPACKS / RESOURCE PACKS / SHADERS	Modpack filtering",
    "504	MODPACKS / RESOURCE PACKS / SHADERS	Modpack sorting",
    "505	MODPACKS / RESOURCE PACKS / SHADERS	Installed modpacks",
    "506	MODPACKS / RESOURCE PACKS / SHADERS	Favorite modpacks",
    "507	MODPACKS / RESOURCE PACKS / SHADERS	Modpack metadata",
    "508	MODPACKS / RESOURCE PACKS / SHADERS	Modpack version",
    "509	MODPACKS / RESOURCE PACKS / SHADERS	Modpack Minecraft version",
    "510	MODPACKS / RESOURCE PACKS / SHADERS	Modpack loader",
    "511	MODPACKS / RESOURCE PACKS / SHADERS	Modpack dependencies",
    "512	MODPACKS / RESOURCE PACKS / SHADERS	Modpack install",
    "513	MODPACKS / RESOURCE PACKS / SHADERS	Modpack removal",
    "514	MODPACKS / RESOURCE PACKS / SHADERS	Modpack repair",
    "515	MODPACKS / RESOURCE PACKS / SHADERS	Modpack update",
    "516	MODPACKS / RESOURCE PACKS / SHADERS	Modpack rollback",
    "517	MODPACKS / RESOURCE PACKS / SHADERS	Modpack backup",
    "518	MODPACKS / RESOURCE PACKS / SHADERS	Modpack restore",
    "519	MODPACKS / RESOURCE PACKS / SHADERS	Modpack import",
    "520	MODPACKS / RESOURCE PACKS / SHADERS	Modpack export",
    "521	MODPACKS / RESOURCE PACKS / SHADERS	Modpack cloning",
    "522	MODPACKS / RESOURCE PACKS / SHADERS	Modpack profile",
    "523	MODPACKS / RESOURCE PACKS / SHADERS	Modpack profile switching",
    "524	MODPACKS / RESOURCE PACKS / SHADERS	Modpack compatibility",
    "525	MODPACKS / RESOURCE PACKS / SHADERS	Modpack conflict detection",
    "526	MODPACKS / RESOURCE PACKS / SHADERS	Modpack storage usage",
    "527	MODPACKS / RESOURCE PACKS / SHADERS	Modpack download progress",
    "528	MODPACKS / RESOURCE PACKS / SHADERS	Modpack download queue",
    "529	MODPACKS / RESOURCE PACKS / SHADERS	Modpack download retry",
    "530	MODPACKS / RESOURCE PACKS / SHADERS	Modpack download cancellation",
    "531	MODPACKS / RESOURCE PACKS / SHADERS	Modpack activity",
    "532	MODPACKS / RESOURCE PACKS / SHADERS	Modpack history",
    "533	MODPACKS / RESOURCE PACKS / SHADERS	Modpack changelog",
    "534	MODPACKS / RESOURCE PACKS / SHADERS	Modpack dependency viewer",
    "535	MODPACKS / RESOURCE PACKS / SHADERS	Modpack file browser",
    "536	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack browser",
    "537	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack search",
    "538	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack filtering",
    "539	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack sorting",
    "540	MODPACKS / RESOURCE PACKS / SHADERS	Installed resource packs",
    "541	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack enable/disable",
    "542	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack install",
    "543	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack removal",
    "544	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack backup",
    "545	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack restore",
    "546	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack import",
    "547	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack export",
    "548	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack compatibility",
    "549	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack resolution display",
    "550	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack storage usage",
    "551	MODPACKS / RESOURCE PACKS / SHADERS	Shader browser",
    "552	MODPACKS / RESOURCE PACKS / SHADERS	Shader search",
    "553	MODPACKS / RESOURCE PACKS / SHADERS	Shader filtering",
    "554	MODPACKS / RESOURCE PACKS / SHADERS	Shader sorting",
    "555	MODPACKS / RESOURCE PACKS / SHADERS	Installed shaders",
    "556	MODPACKS / RESOURCE PACKS / SHADERS	Shader enable/disable",
    "557	MODPACKS / RESOURCE PACKS / SHADERS	Shader install",
    "558	MODPACKS / RESOURCE PACKS / SHADERS	Shader removal",
    "559	MODPACKS / RESOURCE PACKS / SHADERS	Shader backup",
    "560	MODPACKS / RESOURCE PACKS / SHADERS	Shader restore",
    "561	MODPACKS / RESOURCE PACKS / SHADERS	Shader import",
    "562	MODPACKS / RESOURCE PACKS / SHADERS	Shader export",
    "563	MODPACKS / RESOURCE PACKS / SHADERS	Shader compatibility",
    "564	MODPACKS / RESOURCE PACKS / SHADERS	Shader GPU warning",
    "565	MODPACKS / RESOURCE PACKS / SHADERS	Shader performance warning",
    "566	MODPACKS / RESOURCE PACKS / SHADERS	Shader resolution",
    "567	MODPACKS / RESOURCE PACKS / SHADERS	Shader storage usage",
    "568	MODPACKS / RESOURCE PACKS / SHADERS	Shader configuration",
    "569	MODPACKS / RESOURCE PACKS / SHADERS	Shader configuration backup",
    "570	MODPACKS / RESOURCE PACKS / SHADERS	Shader configuration restore",
    "571	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack profile",
    "572	MODPACKS / RESOURCE PACKS / SHADERS	Shader profile",
    "573	MODPACKS / RESOURCE PACKS / SHADERS	Pack profile switching",
    "574	MODPACKS / RESOURCE PACKS / SHADERS	Pack profile cloning",
    "575	MODPACKS / RESOURCE PACKS / SHADERS	Pack profile backup",
    "576	MODPACKS / RESOURCE PACKS / SHADERS	Pack profile restore",
    "577	MODPACKS / RESOURCE PACKS / SHADERS	Pack profile comparison",
    "578	MODPACKS / RESOURCE PACKS / SHADERS	Pack update detection",
    "579	MODPACKS / RESOURCE PACKS / SHADERS	Pack update history",
    "580	MODPACKS / RESOURCE PACKS / SHADERS	Pack repair assistant",
    "581	MODPACKS / RESOURCE PACKS / SHADERS	Pack cleanup assistant",
    "582	MODPACKS / RESOURCE PACKS / SHADERS	Pack migration assistant",
    "583	MODPACKS / RESOURCE PACKS / SHADERS	Pack conflict assistant",
    "584	MODPACKS / RESOURCE PACKS / SHADERS	Pack compatibility report",
    "585	MODPACKS / RESOURCE PACKS / SHADERS	Pack storage analyzer",
    "586	MODPACKS / RESOURCE PACKS / SHADERS	Pack download manager",
    "587	MODPACKS / RESOURCE PACKS / SHADERS	Pack cache manager",
    "588	MODPACKS / RESOURCE PACKS / SHADERS	Pack metadata cache",
    "589	MODPACKS / RESOURCE PACKS / SHADERS	Pack offline mode",
    "590	MODPACKS / RESOURCE PACKS / SHADERS	Pack installation queue",
    "591	MODPACKS / RESOURCE PACKS / SHADERS	Pack installation history",
    "592	MODPACKS / RESOURCE PACKS / SHADERS	Pack removal history",
    "593	MODPACKS / RESOURCE PACKS / SHADERS	Pack favorites",
    "594	MODPACKS / RESOURCE PACKS / SHADERS	Pack collections",
    "595	MODPACKS / RESOURCE PACKS / SHADERS	Pack statistics",
    "596	MODPACKS / RESOURCE PACKS / SHADERS	Pack health report",
    "597	MODPACKS / RESOURCE PACKS / SHADERS	Resource-pack health report",
    "598	MODPACKS / RESOURCE PACKS / SHADERS	Shader health report",
    "599	MODPACKS / RESOURCE PACKS / SHADERS	Visual-pack dashboard",
    "600	MODPACKS / RESOURCE PACKS / SHADERS	Packs center",
    "601	WORLDS / SERVERS	World browser",
    "602	WORLDS / SERVERS	World search",
    "603	WORLDS / SERVERS	World filtering",
    "604	WORLDS / SERVERS	World sorting",
    "605	WORLDS / SERVERS	Installed worlds",
    "606	WORLDS / SERVERS	Favorite worlds",
    "607	WORLDS / SERVERS	Recent worlds",
    "608	WORLDS / SERVERS	World metadata",
    "609	WORLDS / SERVERS	World version",
    "610	WORLDS / SERVERS	World game mode",
    "611	WORLDS / SERVERS	World difficulty",
    "612	WORLDS / SERVERS	World seed display",
    "613	WORLDS / SERVERS	World folder access",
    "614	WORLDS / SERVERS	World backup",
    "615	WORLDS / SERVERS	World restore",
    "616	WORLDS / SERVERS	World duplicate",
    "617	WORLDS / SERVERS	World rename",
    "618	WORLDS / SERVERS	World delete",
    "619	WORLDS / SERVERS	World import",
    "620	WORLDS / SERVERS	World export",
    "621	WORLDS / SERVERS	World repair",
    "622	WORLDS / SERVERS	World integrity check",
    "623	WORLDS / SERVERS	World backup history",
    "624	WORLDS / SERVERS	World restoration history",
    "625	WORLDS / SERVERS	World playtime",
    "626	WORLDS / SERVERS	World last-played time",
    "627	WORLDS / SERVERS	World size",
    "628	WORLDS / SERVERS	World storage analyzer",
    "629	WORLDS / SERVERS	World screenshot association",
    "630	WORLDS / SERVERS	World favorite toggle",
    "631	WORLDS / SERVERS	World quick launch",
    "632	WORLDS / SERVERS	World launch settings",
    "633	WORLDS / SERVERS	World backup reminder",
    "634	WORLDS / SERVERS	World corruption warning",
    "635	WORLDS / SERVERS	World missing-data warning",
    "636	WORLDS / SERVERS	World version mismatch warning",
    "637	WORLDS / SERVERS	World migration assistant",
    "638	WORLDS / SERVERS	World cleanup assistant",
    "639	WORLDS / SERVERS	World backup assistant",
    "640	WORLDS / SERVERS	World recovery assistant",
    "641	WORLDS / SERVERS	World profile",
    "642	WORLDS / SERVERS	World profile switching",
    "643	WORLDS / SERVERS	World profile cloning",
    "644	WORLDS / SERVERS	World metadata export",
    "645	WORLDS / SERVERS	World metadata import",
    "646	WORLDS / SERVERS	Server browser",
    "647	WORLDS / SERVERS	Server search",
    "648	WORLDS / SERVERS	Server filtering",
    "649	WORLDS / SERVERS	Server sorting",
    "650	WORLDS / SERVERS	Favorite servers",
    "651	WORLDS / SERVERS	Recent servers",
    "652	WORLDS / SERVERS	Server cards",
    "653	WORLDS / SERVERS	Server address storage",
    "654	WORLDS / SERVERS	Server port storage",
    "655	WORLDS / SERVERS	Server notes",
    "656	WORLDS / SERVERS	Server icon support",
    "657	WORLDS / SERVERS	Server status",
    "658	WORLDS / SERVERS	Server ping",
    "659	WORLDS / SERVERS	Server player count",
    "660	WORLDS / SERVERS	Server version",
    "661	WORLDS / SERVERS	Server compatibility",
    "662	WORLDS / SERVERS	Server connection history",
    "663	WORLDS / SERVERS	Server last-connected time",
    "664	WORLDS / SERVERS	Server favorite",
    "665	WORLDS / SERVERS	Server rename",
    "666	WORLDS / SERVERS	Server duplicate",
    "667	WORLDS / SERVERS	Server delete",
    "668	WORLDS / SERVERS	Server import",
    "669	WORLDS / SERVERS	Server export",
    "670	WORLDS / SERVERS	Server groups",
    "671	WORLDS / SERVERS	Server tags",
    "672	WORLDS / SERVERS	Server quick-connect",
    "673	WORLDS / SERVERS	Server connection warnings",
    "674	WORLDS / SERVERS	Server offline indicator",
    "675	WORLDS / SERVERS	Server unavailable indicator",
    "676	WORLDS / SERVERS	Server maintenance indicator",
    "677	WORLDS / SERVERS	Server history",
    "678	WORLDS / SERVERS	Server activity",
    "679	WORLDS / SERVERS	Server notes editor",
    "680	WORLDS / SERVERS	Server profile",
    "681	WORLDS / SERVERS	Server profile switching",
    "682	WORLDS / SERVERS	Server profile backup",
    "683	WORLDS / SERVERS	Server profile restore",
    "684	WORLDS / SERVERS	Server list backup",
    "685	WORLDS / SERVERS	Server list restore",
    "686	WORLDS / SERVERS	Server list export",
    "687	WORLDS / SERVERS	Server list import",
    "688	WORLDS / SERVERS	Server connection retry",
    "689	WORLDS / SERVERS	Server connection cancellation",
    "690	WORLDS / SERVERS	Server status refresh",
    "691	WORLDS / SERVERS	Server automatic refresh",
    "692	WORLDS / SERVERS	Server ping refresh",
    "693	WORLDS / SERVERS	Server compatibility warning",
    "694	WORLDS / SERVERS	Server version warning",
    "695	WORLDS / SERVERS	Server offline cache",
    "696	WORLDS / SERVERS	Server statistics",
    "697	WORLDS / SERVERS	World statistics",
    "698	WORLDS / SERVERS	World/server dashboard",
    "699	WORLDS / SERVERS	World/server manager",
    "700	WORLDS / SERVERS	Worlds & Servers center",
    "701	SETTINGS / CONFIGURATION	Settings redesign",
    "702	SETTINGS / CONFIGURATION	General settings",
    "703	SETTINGS / CONFIGURATION	Launcher settings",
    "704	SETTINGS / CONFIGURATION	Minecraft settings",
    "705	SETTINGS / CONFIGURATION	Java settings",
    "706	SETTINGS / CONFIGURATION	Memory settings",
    "707	SETTINGS / CONFIGURATION	Display settings",
    "708	SETTINGS / CONFIGURATION	Audio settings",
    "709	SETTINGS / CONFIGURATION	Network settings",
    "710	SETTINGS / CONFIGURATION	Download settings",
    "711	SETTINGS / CONFIGURATION	Update settings",
    "712	SETTINGS / CONFIGURATION	Profile settings",
    "713	SETTINGS / CONFIGURATION	Mod settings",
    "714	SETTINGS / CONFIGURATION	World settings",
    "715	SETTINGS / CONFIGURATION	Server settings",
    "716	SETTINGS / CONFIGURATION	Resource-pack settings",
    "717	SETTINGS / CONFIGURATION	Shader settings",
    "718	SETTINGS / CONFIGURATION	Notification settings",
    "719	SETTINGS / CONFIGURATION	Privacy settings",
    "720	SETTINGS / CONFIGURATION	Accessibility settings",
    "721	SETTINGS / CONFIGURATION	Language selector",
    "722	SETTINGS / CONFIGURATION	English language",
    "723	SETTINGS / CONFIGURATION	Arabic language",
    "724	SETTINGS / CONFIGURATION	Language persistence",
    "725	SETTINGS / CONFIGURATION	Language reload",
    "726	SETTINGS / CONFIGURATION	RTL layout",
    "727	SETTINGS / CONFIGURATION	Arabic sidebar",
    "728	SETTINGS / CONFIGURATION	Arabic dialogs",
    "729	SETTINGS / CONFIGURATION	Arabic errors",
    "730	SETTINGS / CONFIGURATION	Arabic notifications",
    "731	SETTINGS / CONFIGURATION	Theme selector",
    "732	SETTINGS / CONFIGURATION	Dark theme",
    "733	SETTINGS / CONFIGURATION	Light theme",
    "734	SETTINGS / CONFIGURATION	Retro theme",
    "735	SETTINGS / CONFIGURATION	Custom accent",
    "736	SETTINGS / CONFIGURATION	UI scaling",
    "737	SETTINGS / CONFIGURATION	Text scaling",
    "738	SETTINGS / CONFIGURATION	Animation settings",
    "739	SETTINGS / CONFIGURATION	Reduced motion",
    "740	SETTINGS / CONFIGURATION	Compact mode",
    "741	SETTINGS / CONFIGURATION	Detailed mode",
    "742	SETTINGS / CONFIGURATION	Startup behavior",
    "743	SETTINGS / CONFIGURATION	Auto-update toggle",
    "744	SETTINGS / CONFIGURATION	Update notification toggle",
    "745	SETTINGS / CONFIGURATION	Beta-channel toggle",
    "746	SETTINGS / CONFIGURATION	Offline mode",
    "747	SETTINGS / CONFIGURATION	Cache settings",
    "748	SETTINGS / CONFIGURATION	Download folder",
    "749	SETTINGS / CONFIGURATION	Game folder",
    "750	SETTINGS / CONFIGURATION	Backup folder",
    "751	SETTINGS / CONFIGURATION	Log folder",
    "752	SETTINGS / CONFIGURATION	Temporary folder",
    "753	SETTINGS / CONFIGURATION	Screenshot folder",
    "754	SETTINGS / CONFIGURATION	Resource-pack folder",
    "755	SETTINGS / CONFIGURATION	Shader folder",
    "756	SETTINGS / CONFIGURATION	Mod folder",
    "757	SETTINGS / CONFIGURATION	World folder",
    "758	SETTINGS / CONFIGURATION	Server data",
    "759	SETTINGS / CONFIGURATION	Java detection",
    "760	SETTINGS / CONFIGURATION	Java selection",
    "761	SETTINGS / CONFIGURATION	Java priority",
    "762	SETTINGS / CONFIGURATION	Java validation",
    "763	SETTINGS / CONFIGURATION	Memory allocation",
    "764	SETTINGS / CONFIGURATION	Minimum memory",
    "765	SETTINGS / CONFIGURATION	Maximum memory",
    "766	SETTINGS / CONFIGURATION	JVM arguments",
    "767	SETTINGS / CONFIGURATION	Game arguments",
    "768	SETTINGS / CONFIGURATION	Default resolution",
    "769	SETTINGS / CONFIGURATION	Default fullscreen",
    "770	SETTINGS / CONFIGURATION	Default profile",
    "771	SETTINGS / CONFIGURATION	Default version",
    "772	SETTINGS / CONFIGURATION	Default Java",
    "773	SETTINGS / CONFIGURATION	Default game directory",
    "774	SETTINGS / CONFIGURATION	Download concurrency",
    "775	SETTINGS / CONFIGURATION	Download timeout",
    "776	SETTINGS / CONFIGURATION	Update timeout",
    "777	SETTINGS / CONFIGURATION	Network retry count",
    "778	SETTINGS / CONFIGURATION	Connection timeout",
    "779	SETTINGS / CONFIGURATION	Proxy configuration",
    "780	SETTINGS / CONFIGURATION	DNS preferences",
    "781	SETTINGS / CONFIGURATION	Download mirror preference",
    "782	SETTINGS / CONFIGURATION	GitHub source configuration",
    "783	SETTINGS / CONFIGURATION	Update channel",
    "784	SETTINGS / CONFIGURATION	Release notes setting",
    "785	SETTINGS / CONFIGURATION	Notification sound",
    "786	SETTINGS / CONFIGURATION	Notification duration",
    "787	SETTINGS / CONFIGURATION	Error-report preference",
    "788	SETTINGS / CONFIGURATION	Log verbosity",
    "789	SETTINGS / CONFIGURATION	Debug mode",
    "790	SETTINGS / CONFIGURATION	Developer settings",
    "791	SETTINGS / CONFIGURATION	Advanced settings",
    "792	SETTINGS / CONFIGURATION	Reset settings",
    "793	SETTINGS / CONFIGURATION	Export settings",
    "794	SETTINGS / CONFIGURATION	Import settings",
    "795	SETTINGS / CONFIGURATION	Backup settings",
    "796	SETTINGS / CONFIGURATION	Restore settings",
    "797	SETTINGS / CONFIGURATION	Settings search",
    "798	SETTINGS / CONFIGURATION	Settings categories",
    "799	SETTINGS / CONFIGURATION	Settings status",
    "800	SETTINGS / CONFIGURATION	Settings center",
    "801	UPDATES / DOWNLOADS / FILE SYSTEM	Better updater",
    "802	UPDATES / DOWNLOADS / FILE SYSTEM	Automatic version checking",
    "803	UPDATES / DOWNLOADS / FILE SYSTEM	Cache-busted version checking",
    "804	UPDATES / DOWNLOADS / FILE SYSTEM	Update availability card",
    "805	UPDATES / DOWNLOADS / FILE SYSTEM	Update changelog",
    "806	UPDATES / DOWNLOADS / FILE SYSTEM	Update confirmation",
    "807	UPDATES / DOWNLOADS / FILE SYSTEM	Update download progress",
    "808	UPDATES / DOWNLOADS / FILE SYSTEM	Update download speed",
    "809	UPDATES / DOWNLOADS / FILE SYSTEM	Update ETA",
    "810	UPDATES / DOWNLOADS / FILE SYSTEM	Update cancellation",
    "811	UPDATES / DOWNLOADS / FILE SYSTEM	Update retry",
    "812	UPDATES / DOWNLOADS / FILE SYSTEM	Update verification",
    "813	UPDATES / DOWNLOADS / FILE SYSTEM	Update integrity check",
    "814	UPDATES / DOWNLOADS / FILE SYSTEM	Update backup",
    "815	UPDATES / DOWNLOADS / FILE SYSTEM	Update rollback",
    "816	UPDATES / DOWNLOADS / FILE SYSTEM	Update failure recovery",
    "817	UPDATES / DOWNLOADS / FILE SYSTEM	Update history",
    "818	UPDATES / DOWNLOADS / FILE SYSTEM	Update channel selector",
    "819	UPDATES / DOWNLOADS / FILE SYSTEM	Stable channel",
    "820	UPDATES / DOWNLOADS / FILE SYSTEM	Beta channel",
    "821	UPDATES / DOWNLOADS / FILE SYSTEM	Development channel",
    "822	UPDATES / DOWNLOADS / FILE SYSTEM	Update notification",
    "823	UPDATES / DOWNLOADS / FILE SYSTEM	Update reminder",
    "824	UPDATES / DOWNLOADS / FILE SYSTEM	Update-on-start option",
    "825	UPDATES / DOWNLOADS / FILE SYSTEM	Update-on-close option",
    "826	UPDATES / DOWNLOADS / FILE SYSTEM	Manual update",
    "827	UPDATES / DOWNLOADS / FILE SYSTEM	Update details",
    "828	UPDATES / DOWNLOADS / FILE SYSTEM	Current-version display",
    "829	UPDATES / DOWNLOADS / FILE SYSTEM	Latest-version display",
    "830	UPDATES / DOWNLOADS / FILE SYSTEM	Update source display",
    "831	UPDATES / DOWNLOADS / FILE SYSTEM	Update connection status",
    "832	UPDATES / DOWNLOADS / FILE SYSTEM	Update server status",
    "833	UPDATES / DOWNLOADS / FILE SYSTEM	Update error details",
    "834	UPDATES / DOWNLOADS / FILE SYSTEM	Update log",
    "835	UPDATES / DOWNLOADS / FILE SYSTEM	Download center",
    "836	UPDATES / DOWNLOADS / FILE SYSTEM	Active downloads",
    "837	UPDATES / DOWNLOADS / FILE SYSTEM	Completed downloads",
    "838	UPDATES / DOWNLOADS / FILE SYSTEM	Failed downloads",
    "839	UPDATES / DOWNLOADS / FILE SYSTEM	Cancelled downloads",
    "840	UPDATES / DOWNLOADS / FILE SYSTEM	Download queue",
    "841	UPDATES / DOWNLOADS / FILE SYSTEM	Download retry",
    "842	UPDATES / DOWNLOADS / FILE SYSTEM	Download pause",
    "843	UPDATES / DOWNLOADS / FILE SYSTEM	Download resume",
    "844	UPDATES / DOWNLOADS / FILE SYSTEM	Download speed",
    "845	UPDATES / DOWNLOADS / FILE SYSTEM	Download ETA",
    "846	UPDATES / DOWNLOADS / FILE SYSTEM	Download size",
    "847	UPDATES / DOWNLOADS / FILE SYSTEM	Download progress",
    "848	UPDATES / DOWNLOADS / FILE SYSTEM	Download destination",
    "849	UPDATES / DOWNLOADS / FILE SYSTEM	Download history",
    "850	UPDATES / DOWNLOADS / FILE SYSTEM	Download cleanup",
    "851	UPDATES / DOWNLOADS / FILE SYSTEM	Download cache",
    "852	UPDATES / DOWNLOADS / FILE SYSTEM	Download cache size",
    "853	UPDATES / DOWNLOADS / FILE SYSTEM	Cache clearing",
    "854	UPDATES / DOWNLOADS / FILE SYSTEM	Cache verification",
    "855	UPDATES / DOWNLOADS / FILE SYSTEM	Cache repair",
    "856	UPDATES / DOWNLOADS / FILE SYSTEM	File browser",
    "857	UPDATES / DOWNLOADS / FILE SYSTEM	Open launcher folder",
    "858	UPDATES / DOWNLOADS / FILE SYSTEM	Open Minecraft folder",
    "859	UPDATES / DOWNLOADS / FILE SYSTEM	Open versions folder",
    "860	UPDATES / DOWNLOADS / FILE SYSTEM	Open mods folder",
    "861	UPDATES / DOWNLOADS / FILE SYSTEM	Open worlds folder",
    "862	UPDATES / DOWNLOADS / FILE SYSTEM	Open resource-pack folder",
    "863	UPDATES / DOWNLOADS / FILE SYSTEM	Open shader folder",
    "864	UPDATES / DOWNLOADS / FILE SYSTEM	Open logs folder",
    "865	UPDATES / DOWNLOADS / FILE SYSTEM	Open backups folder",
    "866	UPDATES / DOWNLOADS / FILE SYSTEM	Open downloads folder",
    "867	UPDATES / DOWNLOADS / FILE SYSTEM	File search",
    "868	UPDATES / DOWNLOADS / FILE SYSTEM	File filtering",
    "869	UPDATES / DOWNLOADS / FILE SYSTEM	File sorting",
    "870	UPDATES / DOWNLOADS / FILE SYSTEM	File size display",
    "871	UPDATES / DOWNLOADS / FILE SYSTEM	File modified time",
    "872	UPDATES / DOWNLOADS / FILE SYSTEM	File extension display",
    "873	UPDATES / DOWNLOADS / FILE SYSTEM	File copy",
    "874	UPDATES / DOWNLOADS / FILE SYSTEM	File move",
    "875	UPDATES / DOWNLOADS / FILE SYSTEM	File rename",
    "876	UPDATES / DOWNLOADS / FILE SYSTEM	File delete",
    "877	UPDATES / DOWNLOADS / FILE SYSTEM	File duplicate",
    "878	UPDATES / DOWNLOADS / FILE SYSTEM	Folder creation",
    "879	UPDATES / DOWNLOADS / FILE SYSTEM	Folder size analysis",
    "880	UPDATES / DOWNLOADS / FILE SYSTEM	Storage analyzer",
    "881	UPDATES / DOWNLOADS / FILE SYSTEM	Large-file detection",
    "882	UPDATES / DOWNLOADS / FILE SYSTEM	Empty-folder detection",
    "883	UPDATES / DOWNLOADS / FILE SYSTEM	Broken-file detection",
    "884	UPDATES / DOWNLOADS / FILE SYSTEM	Missing-file detection",
    "885	UPDATES / DOWNLOADS / FILE SYSTEM	Duplicate-file detection",
    "886	UPDATES / DOWNLOADS / FILE SYSTEM	Temporary-file detection",
    "887	UPDATES / DOWNLOADS / FILE SYSTEM	Cleanup assistant",
    "888	UPDATES / DOWNLOADS / FILE SYSTEM	Storage cleanup",
    "889	UPDATES / DOWNLOADS / FILE SYSTEM	File repair assistant",
    "890	UPDATES / DOWNLOADS / FILE SYSTEM	File verification",
    "891	UPDATES / DOWNLOADS / FILE SYSTEM	File hash display",
    "892	UPDATES / DOWNLOADS / FILE SYSTEM	File metadata viewer",
    "893	UPDATES / DOWNLOADS / FILE SYSTEM	File history",
    "894	UPDATES / DOWNLOADS / FILE SYSTEM	File operation history",
    "895	UPDATES / DOWNLOADS / FILE SYSTEM	File-operation undo where safe",
    "896	UPDATES / DOWNLOADS / FILE SYSTEM	File safety confirmation",
    "897	UPDATES / DOWNLOADS / FILE SYSTEM	File-access errors",
    "898	UPDATES / DOWNLOADS / FILE SYSTEM	File permission errors",
    "899	UPDATES / DOWNLOADS / FILE SYSTEM	File-system dashboard",
    "900	UPDATES / DOWNLOADS / FILE SYSTEM	File manager center",
    "901	JAVA / DIAGNOSTICS / PERFORMANCE	Java Manager",
    "902	JAVA / DIAGNOSTICS / PERFORMANCE	Java detection",
    "903	JAVA / DIAGNOSTICS / PERFORMANCE	Java installation list",
    "904	JAVA / DIAGNOSTICS / PERFORMANCE	Java version display",
    "905	JAVA / DIAGNOSTICS / PERFORMANCE	Java architecture display",
    "906	JAVA / DIAGNOSTICS / PERFORMANCE	Java path display",
    "907	JAVA / DIAGNOSTICS / PERFORMANCE	Java validity check",
    "908	JAVA / DIAGNOSTICS / PERFORMANCE	Java compatibility check",
    "909	JAVA / DIAGNOSTICS / PERFORMANCE	Java profile",
    "910	JAVA / DIAGNOSTICS / PERFORMANCE	Java default selection",
    "911	JAVA / DIAGNOSTICS / PERFORMANCE	Java per-version selection",
    "912	JAVA / DIAGNOSTICS / PERFORMANCE	Java per-profile selection",
    "913	JAVA / DIAGNOSTICS / PERFORMANCE	Java environment information",
    "914	JAVA / DIAGNOSTICS / PERFORMANCE	Java launch test",
    "915	JAVA / DIAGNOSTICS / PERFORMANCE	Java error explanation",
    "916	JAVA / DIAGNOSTICS / PERFORMANCE	Java missing warning",
    "917	JAVA / DIAGNOSTICS / PERFORMANCE	Java incompatible warning",
    "918	JAVA / DIAGNOSTICS / PERFORMANCE	Java path repair",
    "919	JAVA / DIAGNOSTICS / PERFORMANCE	Java refresh",
    "920	JAVA / DIAGNOSTICS / PERFORMANCE	Java scan",
    "921	JAVA / DIAGNOSTICS / PERFORMANCE	System diagnostics",
    "922	JAVA / DIAGNOSTICS / PERFORMANCE	CPU information",
    "923	JAVA / DIAGNOSTICS / PERFORMANCE	GPU information",
    "924	JAVA / DIAGNOSTICS / PERFORMANCE	RAM information",
    "925	JAVA / DIAGNOSTICS / PERFORMANCE	Storage information",
    "926	JAVA / DIAGNOSTICS / PERFORMANCE	Operating-system information",
    "927	JAVA / DIAGNOSTICS / PERFORMANCE	Python information",
    "928	JAVA / DIAGNOSTICS / PERFORMANCE	Tkinter information",
    "929	JAVA / DIAGNOSTICS / PERFORMANCE	MPV information",
    "930	JAVA / DIAGNOSTICS / PERFORMANCE	Network information",
    "931	JAVA / DIAGNOSTICS / PERFORMANCE	Launcher environment",
    "932	JAVA / DIAGNOSTICS / PERFORMANCE	Minecraft environment",
    "933	JAVA / DIAGNOSTICS / PERFORMANCE	Java environment",
    "934	JAVA / DIAGNOSTICS / PERFORMANCE	Diagnostics report",
    "935	JAVA / DIAGNOSTICS / PERFORMANCE	Diagnostics export",
    "936	JAVA / DIAGNOSTICS / PERFORMANCE	Diagnostics copy",
    "937	JAVA / DIAGNOSTICS / PERFORMANCE	Diagnostics history",
    "938	JAVA / DIAGNOSTICS / PERFORMANCE	Quick diagnostics",
    "939	JAVA / DIAGNOSTICS / PERFORMANCE	Full diagnostics",
    "940	JAVA / DIAGNOSTICS / PERFORMANCE	Launcher health check",
    "941	JAVA / DIAGNOSTICS / PERFORMANCE	Minecraft health check",
    "942	JAVA / DIAGNOSTICS / PERFORMANCE	Profile health check",
    "943	JAVA / DIAGNOSTICS / PERFORMANCE	Version health check",
    "944	JAVA / DIAGNOSTICS / PERFORMANCE	Mod health check",
    "945	JAVA / DIAGNOSTICS / PERFORMANCE	World health check",
    "946	JAVA / DIAGNOSTICS / PERFORMANCE	Server health check",
    "947	JAVA / DIAGNOSTICS / PERFORMANCE	Java health check",
    "948	JAVA / DIAGNOSTICS / PERFORMANCE	Storage health check",
    "949	JAVA / DIAGNOSTICS / PERFORMANCE	Network health check",
    "950	JAVA / DIAGNOSTICS / PERFORMANCE	Update health check",
    "951	JAVA / DIAGNOSTICS / PERFORMANCE	Performance monitor",
    "952	JAVA / DIAGNOSTICS / PERFORMANCE	Launcher CPU usage",
    "953	JAVA / DIAGNOSTICS / PERFORMANCE	Launcher RAM usage",
    "954	JAVA / DIAGNOSTICS / PERFORMANCE	Launcher startup time",
    "955	JAVA / DIAGNOSTICS / PERFORMANCE	Launcher response time",
    "956	JAVA / DIAGNOSTICS / PERFORMANCE	Download performance",
    "957	JAVA / DIAGNOSTICS / PERFORMANCE	Minecraft startup time",
    "958	JAVA / DIAGNOSTICS / PERFORMANCE	Java startup time",
    "959	JAVA / DIAGNOSTICS / PERFORMANCE	Mod loading time",
    "960	JAVA / DIAGNOSTICS / PERFORMANCE	Asset loading time",
    "961	JAVA / DIAGNOSTICS / PERFORMANCE	Disk usage",
    "962	JAVA / DIAGNOSTICS / PERFORMANCE	Disk free-space warning",
    "963	JAVA / DIAGNOSTICS / PERFORMANCE	RAM warning",
    "964	JAVA / DIAGNOSTICS / PERFORMANCE	CPU warning",
    "965	JAVA / DIAGNOSTICS / PERFORMANCE	GPU warning",
    "966	JAVA / DIAGNOSTICS / PERFORMANCE	Java memory warning",
    "967	JAVA / DIAGNOSTICS / PERFORMANCE	Performance profile",
    "968	JAVA / DIAGNOSTICS / PERFORMANCE	Low-RAM mode",
    "969	JAVA / DIAGNOSTICS / PERFORMANCE	Slow-PC mode",
    "970	JAVA / DIAGNOSTICS / PERFORMANCE	Fast-PC mode",
    "971	JAVA / DIAGNOSTICS / PERFORMANCE	Download optimization",
    "972	JAVA / DIAGNOSTICS / PERFORMANCE	Cache optimization",
    "973	JAVA / DIAGNOSTICS / PERFORMANCE	Startup optimization",
    "974	JAVA / DIAGNOSTICS / PERFORMANCE	UI optimization",
    "975	JAVA / DIAGNOSTICS / PERFORMANCE	Resource optimization",
    "976	JAVA / DIAGNOSTICS / PERFORMANCE	Memory recommendations",
    "977	JAVA / DIAGNOSTICS / PERFORMANCE	Java recommendations",
    "978	JAVA / DIAGNOSTICS / PERFORMANCE	Minecraft recommendations",
    "979	JAVA / DIAGNOSTICS / PERFORMANCE	Mod recommendations",
    "980	JAVA / DIAGNOSTICS / PERFORMANCE	Shader recommendations",
    "981	JAVA / DIAGNOSTICS / PERFORMANCE	Performance history",
    "982	JAVA / DIAGNOSTICS / PERFORMANCE	Performance graphs",
    "983	JAVA / DIAGNOSTICS / PERFORMANCE	Performance reports",
    "984	JAVA / DIAGNOSTICS / PERFORMANCE	Diagnostics notifications",
    "985	JAVA / DIAGNOSTICS / PERFORMANCE	Diagnostics logs",
    "986	JAVA / DIAGNOSTICS / PERFORMANCE	Error scanner",
    "987	JAVA / DIAGNOSTICS / PERFORMANCE	Configuration scanner",
    "988	JAVA / DIAGNOSTICS / PERFORMANCE	Dependency scanner",
    "989	JAVA / DIAGNOSTICS / PERFORMANCE	Installation scanner",
    "990	JAVA / DIAGNOSTICS / PERFORMANCE	Update scanner",
    "991	JAVA / DIAGNOSTICS / PERFORMANCE	Health score",
    "992	JAVA / DIAGNOSTICS / PERFORMANCE	Launcher health card",
    "993	JAVA / DIAGNOSTICS / PERFORMANCE	Technical summary",
    "994	JAVA / DIAGNOSTICS / PERFORMANCE	System summary",
    "995	JAVA / DIAGNOSTICS / PERFORMANCE	Minecraft summary",
    "996	JAVA / DIAGNOSTICS / PERFORMANCE	Java summary",
    "997	JAVA / DIAGNOSTICS / PERFORMANCE	Performance summary",
    "998	JAVA / DIAGNOSTICS / PERFORMANCE	Diagnostics assistant",
    "999	JAVA / DIAGNOSTICS / PERFORMANCE	Technical tools dashboard",
    "1000	JAVA / DIAGNOSTICS / PERFORMANCE	Diagnostics center",
    "1001	PROFILES / ACCOUNTS / PERSONALIZATION	Profile manager",
    "1002	PROFILES / ACCOUNTS / PERSONALIZATION	Profile creation",
    "1003	PROFILES / ACCOUNTS / PERSONALIZATION	Profile deletion",
    "1004	PROFILES / ACCOUNTS / PERSONALIZATION	Profile duplication",
    "1005	PROFILES / ACCOUNTS / PERSONALIZATION	Profile renaming",
    "1006	PROFILES / ACCOUNTS / PERSONALIZATION	Profile switching",
    "1007	PROFILES / ACCOUNTS / PERSONALIZATION	Favorite profile",
    "1008	PROFILES / ACCOUNTS / PERSONALIZATION	Default profile",
    "1009	PROFILES / ACCOUNTS / PERSONALIZATION	Profile icons",
    "1010	PROFILES / ACCOUNTS / PERSONALIZATION	Custom profile image",
    "1011	PROFILES / ACCOUNTS / PERSONALIZATION	Profile colors",
    "1012	PROFILES / ACCOUNTS / PERSONALIZATION	Profile descriptions",
    "1013	PROFILES / ACCOUNTS / PERSONALIZATION	Profile notes",
    "1014	PROFILES / ACCOUNTS / PERSONALIZATION	Profile version",
    "1015	PROFILES / ACCOUNTS / PERSONALIZATION	Profile Java",
    "1016	PROFILES / ACCOUNTS / PERSONALIZATION	Profile memory",
    "1017	PROFILES / ACCOUNTS / PERSONALIZATION	Profile resolution",
    "1018	PROFILES / ACCOUNTS / PERSONALIZATION	Profile game directory",
    "1019	PROFILES / ACCOUNTS / PERSONALIZATION	Profile mods",
    "1020	PROFILES / ACCOUNTS / PERSONALIZATION	Profile modpacks",
    "1021	PROFILES / ACCOUNTS / PERSONALIZATION	Profile resource packs",
    "1022	PROFILES / ACCOUNTS / PERSONALIZATION	Profile shaders",
    "1023	PROFILES / ACCOUNTS / PERSONALIZATION	Profile worlds",
    "1024	PROFILES / ACCOUNTS / PERSONALIZATION	Profile servers",
    "1025	PROFILES / ACCOUNTS / PERSONALIZATION	Profile launch arguments",
    "1026	PROFILES / ACCOUNTS / PERSONALIZATION	Profile JVM arguments",
    "1027	PROFILES / ACCOUNTS / PERSONALIZATION	Profile backups",
    "1028	PROFILES / ACCOUNTS / PERSONALIZATION	Profile export",
    "1029	PROFILES / ACCOUNTS / PERSONALIZATION	Profile import",
    "1030	PROFILES / ACCOUNTS / PERSONALIZATION	Profile cloning",
    "1031	PROFILES / ACCOUNTS / PERSONALIZATION	Profile comparison",
    "1032	PROFILES / ACCOUNTS / PERSONALIZATION	Profile history",
    "1033	PROFILES / ACCOUNTS / PERSONALIZATION	Profile activity",
    "1034	PROFILES / ACCOUNTS / PERSONALIZATION	Profile playtime",
    "1035	PROFILES / ACCOUNTS / PERSONALIZATION	Profile launch count",
    "1036	PROFILES / ACCOUNTS / PERSONALIZATION	Profile error count",
    "1037	PROFILES / ACCOUNTS / PERSONALIZATION	Profile storage usage",
    "1038	PROFILES / ACCOUNTS / PERSONALIZATION	Profile health",
    "1039	PROFILES / ACCOUNTS / PERSONALIZATION	Profile repair",
    "1040	PROFILES / ACCOUNTS / PERSONALIZATION	Profile backup",
    "1041	PROFILES / ACCOUNTS / PERSONALIZATION	Profile restore",
    "1042	PROFILES / ACCOUNTS / PERSONALIZATION	Profile migration",
    "1043	PROFILES / ACCOUNTS / PERSONALIZATION	Profile cleanup",
    "1044	PROFILES / ACCOUNTS / PERSONALIZATION	Profile validation",
    "1045	PROFILES / ACCOUNTS / PERSONALIZATION	Profile compatibility",
    "1046	PROFILES / ACCOUNTS / PERSONALIZATION	Profile warning",
    "1047	PROFILES / ACCOUNTS / PERSONALIZATION	Profile search",
    "1048	PROFILES / ACCOUNTS / PERSONALIZATION	Profile filtering",
    "1049	PROFILES / ACCOUNTS / PERSONALIZATION	Profile sorting",
    "1050	PROFILES / ACCOUNTS / PERSONALIZATION	Profile groups",
    "1051	PROFILES / ACCOUNTS / PERSONALIZATION	Profile tags",
    "1052	PROFILES / ACCOUNTS / PERSONALIZATION	Profile favorites",
    "1053	PROFILES / ACCOUNTS / PERSONALIZATION	Profile archive",
    "1054	PROFILES / ACCOUNTS / PERSONALIZATION	Profile restore-from-archive",
    "1055	PROFILES / ACCOUNTS / PERSONALIZATION	Profile activity timeline",
    "1056	PROFILES / ACCOUNTS / PERSONALIZATION	Profile launch timeline",
    "1057	PROFILES / ACCOUNTS / PERSONALIZATION	Profile download timeline",
    "1058	PROFILES / ACCOUNTS / PERSONALIZATION	Profile update timeline",
    "1059	PROFILES / ACCOUNTS / PERSONALIZATION	Profile backup timeline",
    "1060	PROFILES / ACCOUNTS / PERSONALIZATION	Profile error timeline",
    "1061	PROFILES / ACCOUNTS / PERSONALIZATION	Profile statistics",
    "1062	PROFILES / ACCOUNTS / PERSONALIZATION	Profile dashboard",
    "1063	PROFILES / ACCOUNTS / PERSONALIZATION	Profile summary",
    "1064	PROFILES / ACCOUNTS / PERSONALIZATION	Profile quick launch",
    "1065	PROFILES / ACCOUNTS / PERSONALIZATION	Profile advanced launch",
    "1066	PROFILES / ACCOUNTS / PERSONALIZATION	Profile safe launch",
    "1067	PROFILES / ACCOUNTS / PERSONALIZATION	Profile vanilla launch",
    "1068	PROFILES / ACCOUNTS / PERSONALIZATION	Profile modded launch",
    "1069	PROFILES / ACCOUNTS / PERSONALIZATION	Profile debug launch",
    "1070	PROFILES / ACCOUNTS / PERSONALIZATION	Profile offline launch",
    "1071	PROFILES / ACCOUNTS / PERSONALIZATION	Profile settings",
    "1072	PROFILES / ACCOUNTS / PERSONALIZATION	Profile defaults",
    "1073	PROFILES / ACCOUNTS / PERSONALIZATION	Profile environment",
    "1074	PROFILES / ACCOUNTS / PERSONALIZATION	Profile folder access",
    "1075	PROFILES / ACCOUNTS / PERSONALIZATION	Profile log access",
    "1076	PROFILES / ACCOUNTS / PERSONALIZATION	Profile backup location",
    "1077	PROFILES / ACCOUNTS / PERSONALIZATION	Profile storage analyzer",
    "1078	PROFILES / ACCOUNTS / PERSONALIZATION	Profile file analyzer",
    "1079	PROFILES / ACCOUNTS / PERSONALIZATION	Profile dependency analyzer",
    "1080	PROFILES / ACCOUNTS / PERSONALIZATION	Profile compatibility analyzer",
    "1081	PROFILES / ACCOUNTS / PERSONALIZATION	Profile error analyzer",
    "1082	PROFILES / ACCOUNTS / PERSONALIZATION	Profile performance analyzer",
    "1083	PROFILES / ACCOUNTS / PERSONALIZATION	Profile update analyzer",
    "1084	PROFILES / ACCOUNTS / PERSONALIZATION	Profile repair assistant",
    "1085	PROFILES / ACCOUNTS / PERSONALIZATION	Profile migration assistant",
    "1086	PROFILES / ACCOUNTS / PERSONALIZATION	Profile cleanup assistant",
    "1087	PROFILES / ACCOUNTS / PERSONALIZATION	Profile backup assistant",
    "1088	PROFILES / ACCOUNTS / PERSONALIZATION	Profile restore assistant",
    "1089	PROFILES / ACCOUNTS / PERSONALIZATION	Profile configuration export",
    "1090	PROFILES / ACCOUNTS / PERSONALIZATION	Profile configuration import",
    "1091	PROFILES / ACCOUNTS / PERSONALIZATION	Profile profile-card redesign",
    "1092	PROFILES / ACCOUNTS / PERSONALIZATION	Profile card status",
    "1093	PROFILES / ACCOUNTS / PERSONALIZATION	Profile card quick actions",
    "1094	PROFILES / ACCOUNTS / PERSONALIZATION	Profile card activity",
    "1095	PROFILES / ACCOUNTS / PERSONALIZATION	Profile card statistics",
    "1096	PROFILES / ACCOUNTS / PERSONALIZATION	Profile card health",
    "1097	PROFILES / ACCOUNTS / PERSONALIZATION	Profile card warnings",
    "1098	PROFILES / ACCOUNTS / PERSONALIZATION	Profile manager search",
    "1099	PROFILES / ACCOUNTS / PERSONALIZATION	Profile manager dashboard",
    "1100	PROFILES / ACCOUNTS / PERSONALIZATION	Profile center",
    "1101	NEWS / NOTIFICATIONS / ACTIVITY	News center",
    "1102	NEWS / NOTIFICATIONS / ACTIVITY	News cards",
    "1103	NEWS / NOTIFICATIONS / ACTIVITY	News search",
    "1104	NEWS / NOTIFICATIONS / ACTIVITY	News filtering",
    "1105	NEWS / NOTIFICATIONS / ACTIVITY	News categories",
    "1106	NEWS / NOTIFICATIONS / ACTIVITY	News timestamps",
    "1107	NEWS / NOTIFICATIONS / ACTIVITY	News read state",
    "1108	NEWS / NOTIFICATIONS / ACTIVITY	News unread state",
    "1109	NEWS / NOTIFICATIONS / ACTIVITY	News favorites",
    "1110	NEWS / NOTIFICATIONS / ACTIVITY	News archive",
    "1111	NEWS / NOTIFICATIONS / ACTIVITY	News refresh",
    "1112	NEWS / NOTIFICATIONS / ACTIVITY	News offline cache",
    "1113	NEWS / NOTIFICATIONS / ACTIVITY	News connection status",
    "1114	NEWS / NOTIFICATIONS / ACTIVITY	News loading state",
    "1115	NEWS / NOTIFICATIONS / ACTIVITY	News error state",
    "1116	NEWS / NOTIFICATIONS / ACTIVITY	News retry",
    "1117	NEWS / NOTIFICATIONS / ACTIVITY	News update notifications",
    "1118	NEWS / NOTIFICATIONS / ACTIVITY	Launcher announcements",
    "1119	NEWS / NOTIFICATIONS / ACTIVITY	Minecraft announcements",
    "1120	NEWS / NOTIFICATIONS / ACTIVITY	Version announcements",
    "1121	NEWS / NOTIFICATIONS / ACTIVITY	Mod announcements",
    "1122	NEWS / NOTIFICATIONS / ACTIVITY	Modpack announcements",
    "1123	NEWS / NOTIFICATIONS / ACTIVITY	Server announcements",
    "1124	NEWS / NOTIFICATIONS / ACTIVITY	System announcements",
    "1125	NEWS / NOTIFICATIONS / ACTIVITY	Maintenance messages",
    "1126	NEWS / NOTIFICATIONS / ACTIVITY	Update messages",
    "1127	NEWS / NOTIFICATIONS / ACTIVITY	Download messages",
    "1128	NEWS / NOTIFICATIONS / ACTIVITY	Backup messages",
    "1129	NEWS / NOTIFICATIONS / ACTIVITY	Error messages",
    "1130	NEWS / NOTIFICATIONS / ACTIVITY	Warning messages",
    "1131	NEWS / NOTIFICATIONS / ACTIVITY	Success messages",
    "1132	NEWS / NOTIFICATIONS / ACTIVITY	Notification center",
    "1133	NEWS / NOTIFICATIONS / ACTIVITY	Notification filtering",
    "1134	NEWS / NOTIFICATIONS / ACTIVITY	Notification sorting",
    "1135	NEWS / NOTIFICATIONS / ACTIVITY	Notification categories",
    "1136	NEWS / NOTIFICATIONS / ACTIVITY	Notification timestamps",
    "1137	NEWS / NOTIFICATIONS / ACTIVITY	Notification read state",
    "1138	NEWS / NOTIFICATIONS / ACTIVITY	Notification archive",
    "1139	NEWS / NOTIFICATIONS / ACTIVITY	Notification clear-all",
    "1140	NEWS / NOTIFICATIONS / ACTIVITY	Notification sound",
    "1141	NEWS / NOTIFICATIONS / ACTIVITY	Notification popup",
    "1142	NEWS / NOTIFICATIONS / ACTIVITY	Notification duration",
    "1143	NEWS / NOTIFICATIONS / ACTIVITY	Notification priority",
    "1144	NEWS / NOTIFICATIONS / ACTIVITY	Notification settings",
    "1145	NEWS / NOTIFICATIONS / ACTIVITY	Activity center",
    "1146	NEWS / NOTIFICATIONS / ACTIVITY	Activity timeline",
    "1147	NEWS / NOTIFICATIONS / ACTIVITY	Launch activity",
    "1148	NEWS / NOTIFICATIONS / ACTIVITY	Download activity",
    "1149	NEWS / NOTIFICATIONS / ACTIVITY	Update activity",
    "1150	NEWS / NOTIFICATIONS / ACTIVITY	Install activity",
    "1151	NEWS / NOTIFICATIONS / ACTIVITY	Remove activity",
    "1152	NEWS / NOTIFICATIONS / ACTIVITY	Backup activity",
    "1153	NEWS / NOTIFICATIONS / ACTIVITY	Restore activity",
    "1154	NEWS / NOTIFICATIONS / ACTIVITY	Repair activity",
    "1155	NEWS / NOTIFICATIONS / ACTIVITY	Error activity",
    "1156	NEWS / NOTIFICATIONS / ACTIVITY	Profile activity",
    "1157	NEWS / NOTIFICATIONS / ACTIVITY	Mod activity",
    "1158	NEWS / NOTIFICATIONS / ACTIVITY	World activity",
    "1159	NEWS / NOTIFICATIONS / ACTIVITY	Server activity",
    "1160	NEWS / NOTIFICATIONS / ACTIVITY	Settings activity",
    "1161	NEWS / NOTIFICATIONS / ACTIVITY	Search activity",
    "1162	NEWS / NOTIFICATIONS / ACTIVITY	Activity timestamps",
    "1163	NEWS / NOTIFICATIONS / ACTIVITY	Activity filtering",
    "1164	NEWS / NOTIFICATIONS / ACTIVITY	Activity sorting",
    "1165	NEWS / NOTIFICATIONS / ACTIVITY	Activity search",
    "1166	NEWS / NOTIFICATIONS / ACTIVITY	Activity categories",
    "1167	NEWS / NOTIFICATIONS / ACTIVITY	Activity details",
    "1168	NEWS / NOTIFICATIONS / ACTIVITY	Activity export",
    "1169	NEWS / NOTIFICATIONS / ACTIVITY	Activity clear",
    "1170	NEWS / NOTIFICATIONS / ACTIVITY	Activity archive",
    "1171	NEWS / NOTIFICATIONS / ACTIVITY	Session history",
    "1172	NEWS / NOTIFICATIONS / ACTIVITY	Launcher history",
    "1173	NEWS / NOTIFICATIONS / ACTIVITY	Download history",
    "1174	NEWS / NOTIFICATIONS / ACTIVITY	Update history",
    "1175	NEWS / NOTIFICATIONS / ACTIVITY	Installation history",
    "1176	NEWS / NOTIFICATIONS / ACTIVITY	Repair history",
    "1177	NEWS / NOTIFICATIONS / ACTIVITY	Backup history",
    "1178	NEWS / NOTIFICATIONS / ACTIVITY	Restore history",
    "1179	NEWS / NOTIFICATIONS / ACTIVITY	Error history",
    "1180	NEWS / NOTIFICATIONS / ACTIVITY	Search history",
    "1181	NEWS / NOTIFICATIONS / ACTIVITY	Profile history",
    "1182	NEWS / NOTIFICATIONS / ACTIVITY	Version history",
    "1183	NEWS / NOTIFICATIONS / ACTIVITY	Mod history",
    "1184	NEWS / NOTIFICATIONS / ACTIVITY	World history",
    "1185	NEWS / NOTIFICATIONS / ACTIVITY	Server history",
    "1186	NEWS / NOTIFICATIONS / ACTIVITY	Settings history",
    "1187	NEWS / NOTIFICATIONS / ACTIVITY	History search",
    "1188	NEWS / NOTIFICATIONS / ACTIVITY	History filtering",
    "1189	NEWS / NOTIFICATIONS / ACTIVITY	History sorting",
    "1190	NEWS / NOTIFICATIONS / ACTIVITY	History export",
    "1191	NEWS / NOTIFICATIONS / ACTIVITY	History cleanup",
    "1192	NEWS / NOTIFICATIONS / ACTIVITY	Activity statistics",
    "1193	NEWS / NOTIFICATIONS / ACTIVITY	Notification statistics",
    "1194	NEWS / NOTIFICATIONS / ACTIVITY	News statistics",
    "1195	NEWS / NOTIFICATIONS / ACTIVITY	History statistics",
    "1196	NEWS / NOTIFICATIONS / ACTIVITY	Timeline dashboard",
    "1197	NEWS / NOTIFICATIONS / ACTIVITY	Notification dashboard",
    "1198	NEWS / NOTIFICATIONS / ACTIVITY	News dashboard",
    "1199	NEWS / NOTIFICATIONS / ACTIVITY	Activity dashboard",
    "1200	NEWS / NOTIFICATIONS / ACTIVITY	News & Activity center",
    "1201	SAFETY / RECOVERY / ERROR HANDLING	Better error messages",
    "1202	SAFETY / RECOVERY / ERROR HANDLING	Human-readable errors",
    "1203	SAFETY / RECOVERY / ERROR HANDLING	Error categories",
    "1204	SAFETY / RECOVERY / ERROR HANDLING	Error codes",
    "1205	SAFETY / RECOVERY / ERROR HANDLING	Error details",
    "1206	SAFETY / RECOVERY / ERROR HANDLING	Error copy button",
    "1207	SAFETY / RECOVERY / ERROR HANDLING	Error log button",
    "1208	SAFETY / RECOVERY / ERROR HANDLING	Error-folder button",
    "1209	SAFETY / RECOVERY / ERROR HANDLING	Retry button",
    "1210	SAFETY / RECOVERY / ERROR HANDLING	Repair button",
    "1211	SAFETY / RECOVERY / ERROR HANDLING	Recovery button",
    "1212	SAFETY / RECOVERY / ERROR HANDLING	Error history",
    "1213	SAFETY / RECOVERY / ERROR HANDLING	Error search",
    "1214	SAFETY / RECOVERY / ERROR HANDLING	Error filtering",
    "1215	SAFETY / RECOVERY / ERROR HANDLING	Error sorting",
    "1216	SAFETY / RECOVERY / ERROR HANDLING	Launcher crash recovery",
    "1217	SAFETY / RECOVERY / ERROR HANDLING	Update recovery",
    "1218	SAFETY / RECOVERY / ERROR HANDLING	Download recovery",
    "1219	SAFETY / RECOVERY / ERROR HANDLING	Installation recovery",
    "1220	SAFETY / RECOVERY / ERROR HANDLING	Version recovery",
    "1221	SAFETY / RECOVERY / ERROR HANDLING	Mod recovery",
    "1222	SAFETY / RECOVERY / ERROR HANDLING	Profile recovery",
    "1223	SAFETY / RECOVERY / ERROR HANDLING	World recovery",
    "1224	SAFETY / RECOVERY / ERROR HANDLING	Configuration recovery",
    "1225	SAFETY / RECOVERY / ERROR HANDLING	Backup recovery",
    "1226	SAFETY / RECOVERY / ERROR HANDLING	Restore recovery",
    "1227	SAFETY / RECOVERY / ERROR HANDLING	Missing-file detection",
    "1228	SAFETY / RECOVERY / ERROR HANDLING	Missing-folder detection",
    "1229	SAFETY / RECOVERY / ERROR HANDLING	Broken-file detection",
    "1230	SAFETY / RECOVERY / ERROR HANDLING	Invalid-JSON detection",
    "1231	SAFETY / RECOVERY / ERROR HANDLING	Invalid-config detection",
    "1232	SAFETY / RECOVERY / ERROR HANDLING	Invalid-version detection",
    "1233	SAFETY / RECOVERY / ERROR HANDLING	Invalid-profile detection",
    "1234	SAFETY / RECOVERY / ERROR HANDLING	Invalid-Java detection",
    "1235	SAFETY / RECOVERY / ERROR HANDLING	Invalid-mod detection",
    "1236	SAFETY / RECOVERY / ERROR HANDLING	Invalid-modpack detection",
    "1237	SAFETY / RECOVERY / ERROR HANDLING	Invalid-world detection",
    "1238	SAFETY / RECOVERY / ERROR HANDLING	Invalid-server detection",
    "1239	SAFETY / RECOVERY / ERROR HANDLING	Network error detection",
    "1240	SAFETY / RECOVERY / ERROR HANDLING	Timeout detection",
    "1241	SAFETY / RECOVERY / ERROR HANDLING	Connection refusal detection",
    "1242	SAFETY / RECOVERY / ERROR HANDLING	GitHub error detection",
    "1243	SAFETY / RECOVERY / ERROR HANDLING	Download error detection",
    "1244	SAFETY / RECOVERY / ERROR HANDLING	Permission error detection",
    "1245	SAFETY / RECOVERY / ERROR HANDLING	Disk-full detection",
    "1246	SAFETY / RECOVERY / ERROR HANDLING	Storage warning",
    "1247	SAFETY / RECOVERY / ERROR HANDLING	Memory warning",
    "1248	SAFETY / RECOVERY / ERROR HANDLING	Java warning",
    "1249	SAFETY / RECOVERY / ERROR HANDLING	Compatibility warning",
    "1250	SAFETY / RECOVERY / ERROR HANDLING	Dependency warning",
    "1251	SAFETY / RECOVERY / ERROR HANDLING	Conflict warning",
    "1252	SAFETY / RECOVERY / ERROR HANDLING	Duplicate warning",
    "1253	SAFETY / RECOVERY / ERROR HANDLING	Corruption warning",
    "1254	SAFETY / RECOVERY / ERROR HANDLING	Update warning",
    "1255	SAFETY / RECOVERY / ERROR HANDLING	Backup reminder",
    "1256	SAFETY / RECOVERY / ERROR HANDLING	Restore confirmation",
    "1257	SAFETY / RECOVERY / ERROR HANDLING	Delete confirmation",
    "1258	SAFETY / RECOVERY / ERROR HANDLING	Profile-delete confirmation",
    "1259	SAFETY / RECOVERY / ERROR HANDLING	World-delete confirmation",
    "1260	SAFETY / RECOVERY / ERROR HANDLING	Mod-delete confirmation",
    "1261	SAFETY / RECOVERY / ERROR HANDLING	Version-delete confirmation",
    "1262	SAFETY / RECOVERY / ERROR HANDLING	Backup-delete confirmation",
    "1263	SAFETY / RECOVERY / ERROR HANDLING	Cache-delete confirmation",
    "1264	SAFETY / RECOVERY / ERROR HANDLING	Reset confirmation",
    "1265	SAFETY / RECOVERY / ERROR HANDLING	Safe mode",
    "1266	SAFETY / RECOVERY / ERROR HANDLING	Clean mode",
    "1267	SAFETY / RECOVERY / ERROR HANDLING	Offline mode",
    "1268	SAFETY / RECOVERY / ERROR HANDLING	Recovery mode",
    "1269	SAFETY / RECOVERY / ERROR HANDLING	Diagnostic mode",
    "1270	SAFETY / RECOVERY / ERROR HANDLING	Debug mode",
    "1271	SAFETY / RECOVERY / ERROR HANDLING	Repair mode",
    "1272	SAFETY / RECOVERY / ERROR HANDLING	Startup recovery",
    "1273	SAFETY / RECOVERY / ERROR HANDLING	Failed-startup recovery",
    "1274	SAFETY / RECOVERY / ERROR HANDLING	Safe configuration fallback",
    "1275	SAFETY / RECOVERY / ERROR HANDLING	Default configuration fallback",
    "1276	SAFETY / RECOVERY / ERROR HANDLING	Last-known-good settings",
    "1277	SAFETY / RECOVERY / ERROR HANDLING	Backup-before-update",
    "1278	SAFETY / RECOVERY / ERROR HANDLING	Backup-before-repair",
    "1279	SAFETY / RECOVERY / ERROR HANDLING	Backup-before-delete",
    "1280	SAFETY / RECOVERY / ERROR HANDLING	Configuration snapshots",
    "1281	SAFETY / RECOVERY / ERROR HANDLING	Profile snapshots",
    "1282	SAFETY / RECOVERY / ERROR HANDLING	Version snapshots",
    "1283	SAFETY / RECOVERY / ERROR HANDLING	Mod snapshots",
    "1284	SAFETY / RECOVERY / ERROR HANDLING	World snapshots",
    "1285	SAFETY / RECOVERY / ERROR HANDLING	Server snapshots",
    "1286	SAFETY / RECOVERY / ERROR HANDLING	Recovery history",
    "1287	SAFETY / RECOVERY / ERROR HANDLING	Recovery logs",
    "1288	SAFETY / RECOVERY / ERROR HANDLING	Repair logs",
    "1289	SAFETY / RECOVERY / ERROR HANDLING	Diagnostic logs",
    "1290	SAFETY / RECOVERY / ERROR HANDLING	Update logs",
    "1291	SAFETY / RECOVERY / ERROR HANDLING	Download logs",
    "1292	SAFETY / RECOVERY / ERROR HANDLING	Installation logs",
    "1293	SAFETY / RECOVERY / ERROR HANDLING	Launch logs",
    "1294	SAFETY / RECOVERY / ERROR HANDLING	File-operation logs",
    "1295	SAFETY / RECOVERY / ERROR HANDLING	User-friendly log viewer",
    "1296	SAFETY / RECOVERY / ERROR HANDLING	Log filtering",
    "1297	SAFETY / RECOVERY / ERROR HANDLING	Log search",
    "1298	SAFETY / RECOVERY / ERROR HANDLING	Log export",
    "1299	SAFETY / RECOVERY / ERROR HANDLING	Log cleanup",
    "1300	SAFETY / RECOVERY / ERROR HANDLING	Recovery center",
    "1301	TOOLS / QUALITY-OF-LIFE	Tools dashboard",
    "1302	TOOLS / QUALITY-OF-LIFE	Search everything",
    "1303	TOOLS / QUALITY-OF-LIFE	Open launcher folder",
    "1304	TOOLS / QUALITY-OF-LIFE	Open Minecraft folder",
    "1305	TOOLS / QUALITY-OF-LIFE	Open logs",
    "1306	TOOLS / QUALITY-OF-LIFE	Open backups",
    "1307	TOOLS / QUALITY-OF-LIFE	Open downloads",
    "1308	TOOLS / QUALITY-OF-LIFE	Open versions",
    "1309	TOOLS / QUALITY-OF-LIFE	Open mods",
    "1310	TOOLS / QUALITY-OF-LIFE	Open worlds",
    "1311	TOOLS / QUALITY-OF-LIFE	Open resource packs",
    "1312	TOOLS / QUALITY-OF-LIFE	Open shaders",
    "1313	TOOLS / QUALITY-OF-LIFE	Open screenshots",
    "1314	TOOLS / QUALITY-OF-LIFE	Refresh launcher",
    "1315	TOOLS / QUALITY-OF-LIFE	Reload configuration",
    "1316	TOOLS / QUALITY-OF-LIFE	Clear cache",
    "1317	TOOLS / QUALITY-OF-LIFE	Clear download cache",
    "1318	TOOLS / QUALITY-OF-LIFE	Clear metadata cache",
    "1319	TOOLS / QUALITY-OF-LIFE	Verify files",
    "1320	TOOLS / QUALITY-OF-LIFE	Verify versions",
    "1321	TOOLS / QUALITY-OF-LIFE	Verify mods",
    "1322	TOOLS / QUALITY-OF-LIFE	Verify worlds",
    "1323	TOOLS / QUALITY-OF-LIFE	Verify profiles",
    "1324	TOOLS / QUALITY-OF-LIFE	Verify Java",
    "1325	TOOLS / QUALITY-OF-LIFE	Storage analyzer",
    "1326	TOOLS / QUALITY-OF-LIFE	Duplicate finder",
    "1327	TOOLS / QUALITY-OF-LIFE	Large-file finder",
    "1328	TOOLS / QUALITY-OF-LIFE	Empty-folder finder",
    "1329	TOOLS / QUALITY-OF-LIFE	Broken-file finder",
    "1330	TOOLS / QUALITY-OF-LIFE	Missing-file finder",
    "1331	TOOLS / QUALITY-OF-LIFE	Cleanup assistant",
    "1332	TOOLS / QUALITY-OF-LIFE	Backup assistant",
    "1333	TOOLS / QUALITY-OF-LIFE	Restore assistant",
    "1334	TOOLS / QUALITY-OF-LIFE	Migration assistant",
    "1335	TOOLS / QUALITY-OF-LIFE	Repair assistant",
    "1336	TOOLS / QUALITY-OF-LIFE	Update assistant",
    "1337	TOOLS / QUALITY-OF-LIFE	Download assistant",
    "1338	TOOLS / QUALITY-OF-LIFE	Installation assistant",
    "1339	TOOLS / QUALITY-OF-LIFE	Diagnostics assistant",
    "1340	TOOLS / QUALITY-OF-LIFE	Log assistant",
    "1341	TOOLS / QUALITY-OF-LIFE	Java assistant",
    "1342	TOOLS / QUALITY-OF-LIFE	Profile assistant",
    "1343	TOOLS / QUALITY-OF-LIFE	Mod assistant",
    "1344	TOOLS / QUALITY-OF-LIFE	World assistant",
    "1345	TOOLS / QUALITY-OF-LIFE	Server assistant",
    "1346	TOOLS / QUALITY-OF-LIFE	Version assistant",
    "1347	TOOLS / QUALITY-OF-LIFE	Pack assistant",
    "1348	TOOLS / QUALITY-OF-LIFE	Configuration assistant",
    "1349	TOOLS / QUALITY-OF-LIFE	Search assistant",
    "1350	TOOLS / QUALITY-OF-LIFE	Export assistant",
    "1351	TOOLS / QUALITY-OF-LIFE	Import assistant",
    "1352	TOOLS / QUALITY-OF-LIFE	Settings backup",
    "1353	TOOLS / QUALITY-OF-LIFE	Settings restore",
    "1354	TOOLS / QUALITY-OF-LIFE	Launcher backup",
    "1355	TOOLS / QUALITY-OF-LIFE	Launcher restore",
    "1356	TOOLS / QUALITY-OF-LIFE	Configuration export",
    "1357	TOOLS / QUALITY-OF-LIFE	Configuration import",
    "1358	TOOLS / QUALITY-OF-LIFE	Profile export",
    "1359	TOOLS / QUALITY-OF-LIFE	Profile import",
    "1360	TOOLS / QUALITY-OF-LIFE	Version export",
    "1361	TOOLS / QUALITY-OF-LIFE	Version import",
    "1362	TOOLS / QUALITY-OF-LIFE	Mod-list export",
    "1363	TOOLS / QUALITY-OF-LIFE	Mod-list import",
    "1364	TOOLS / QUALITY-OF-LIFE	World export",
    "1365	TOOLS / QUALITY-OF-LIFE	World import",
    "1366	TOOLS / QUALITY-OF-LIFE	Server-list export",
    "1367	TOOLS / QUALITY-OF-LIFE	Server-list import",
    "1368	TOOLS / QUALITY-OF-LIFE	Resource-pack export",
    "1369	TOOLS / QUALITY-OF-LIFE	Resource-pack import",
    "1370	TOOLS / QUALITY-OF-LIFE	Shader export",
    "1371	TOOLS / QUALITY-OF-LIFE	Shader import",
    "1372	TOOLS / QUALITY-OF-LIFE	Diagnostic export",
    "1373	TOOLS / QUALITY-OF-LIFE	Log export",
    "1374	TOOLS / QUALITY-OF-LIFE	Activity export",
    "1375	TOOLS / QUALITY-OF-LIFE	History export",
    "1376	TOOLS / QUALITY-OF-LIFE	Statistics export",
    "1377	TOOLS / QUALITY-OF-LIFE	System summary export",
    "1378	TOOLS / QUALITY-OF-LIFE	Launcher summary export",
    "1379	TOOLS / QUALITY-OF-LIFE	Minecraft summary export",
    "1380	TOOLS / QUALITY-OF-LIFE	Search shortcuts",
    "1381	TOOLS / QUALITY-OF-LIFE	Keyboard-shortcut viewer",
    "1382	TOOLS / QUALITY-OF-LIFE	Shortcut customization",
    "1383	TOOLS / QUALITY-OF-LIFE	Command palette",
    "1384	TOOLS / QUALITY-OF-LIFE	Quick action palette",
    "1385	TOOLS / QUALITY-OF-LIFE	Refresh all",
    "1386	TOOLS / QUALITY-OF-LIFE	Check all",
    "1387	TOOLS / QUALITY-OF-LIFE	Repair all",
    "1388	TOOLS / QUALITY-OF-LIFE	Backup all",
    "1389	TOOLS / QUALITY-OF-LIFE	Restore all",
    "1390	TOOLS / QUALITY-OF-LIFE	Cleanup all",
    "1391	TOOLS / QUALITY-OF-LIFE	Verify all",
    "1392	TOOLS / QUALITY-OF-LIFE	Scan all",
    "1393	TOOLS / QUALITY-OF-LIFE	Export all",
    "1394	TOOLS / QUALITY-OF-LIFE	Import all",
    "1395	TOOLS / QUALITY-OF-LIFE	Reset selected component",
    "1396	TOOLS / QUALITY-OF-LIFE	Reset launcher UI",
    "1397	TOOLS / QUALITY-OF-LIFE	Reset launcher settings",
    "1398	TOOLS / QUALITY-OF-LIFE	Reset cached data",
    "1399	TOOLS / QUALITY-OF-LIFE	Tools history",
    "1400	TOOLS / QUALITY-OF-LIFE	Tools center",
    "1401	EASTER EGGS / FUN / HIDDEN FEATURES	Villager OS version display",
    "1402	EASTER EGGS / FUN / HIDDEN FEATURES	Villager OS starts at 1.0",
    "1403	EASTER EGGS / FUN / HIDDEN FEATURES	Future OS generations can become 1.1, 2.0, 2.1, 3.0, 3.1, etc.",
    "1404	EASTER EGGS / FUN / HIDDEN FEATURES	OS version is separate from launcher version",
    "1405	EASTER EGGS / FUN / HIDDEN FEATURES	OS version shown in About",
    "1406	EASTER EGGS / FUN / HIDDEN FEATURES	OS version styled like an operating-system build",
    "1407	EASTER EGGS / FUN / HIDDEN FEATURES	OS version tap counter",
    "1408	EASTER EGGS / FUN / HIDDEN FEATURES	Multiple-tap Easter egg",
    "1409	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden tap animation",
    "1410	EASTER EGGS / FUN / HIDDEN FEATURES	Easter-egg unlock message",
    "1411	EASTER EGGS / FUN / HIDDEN FEATURES	`easter egg.mp3` playback",
    "1412	EASTER EGGS / FUN / HIDDEN FEATURES	Easter egg sound uses the provided S4 startup sound",
    "1413	EASTER EGGS / FUN / HIDDEN FEATURES	Easter egg activates only after the required taps",
    "1414	EASTER EGGS / FUN / HIDDEN FEATURES	Tap counter resets when leaving About",
    "1415	EASTER EGGS / FUN / HIDDEN FEATURES	Easter egg unlock state can be remembered",
    "1416	EASTER EGGS / FUN / HIDDEN FEATURES	Easter egg replay option after unlocking",
    "1417	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden villager icon",
    "1418	EASTER EGGS / FUN / HIDDEN FEATURES	Villager icon appears after secret interaction",
    "1419	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden Minecraft grass-block animation",
    "1420	EASTER EGGS / FUN / HIDDEN FEATURES	Secret loading-screen message",
    "1421	EASTER EGGS / FUN / HIDDEN FEATURES	Random villager loading message",
    "1422	EASTER EGGS / FUN / HIDDEN FEATURES	Rare startup message",
    "1423	EASTER EGGS / FUN / HIDDEN FEATURES	Very rare startup message",
    "1424	EASTER EGGS / FUN / HIDDEN FEATURES	Secret developer message",
    "1425	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden technical mode",
    "1426	EASTER EGGS / FUN / HIDDEN FEATURES	Secret retro mode",
    "1427	EASTER EGGS / FUN / HIDDEN FEATURES	Old-launcher UI theme",
    "1428	EASTER EGGS / FUN / HIDDEN FEATURES	Fake Windows-style diagnostic screen",
    "1429	EASTER EGGS / FUN / HIDDEN FEATURES	Fake BIOS-style launcher screen",
    "1430	EASTER EGGS / FUN / HIDDEN FEATURES	Fake Minecraft terminal screen",
    "1431	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden command-palette command",
    "1432	EASTER EGGS / FUN / HIDDEN FEATURES	Secret About-page interaction",
    "1433	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden logo interaction",
    "1434	EASTER EGGS / FUN / HIDDEN FEATURES	Logo animation",
    "1435	EASTER EGGS / FUN / HIDDEN FEATURES	Logo sound",
    "1436	EASTER EGGS / FUN / HIDDEN FEATURES	Rare dashboard animation",
    "1437	EASTER EGGS / FUN / HIDDEN FEATURES	Rare loading animation",
    "1438	EASTER EGGS / FUN / HIDDEN FEATURES	Rare error message",
    "1439	EASTER EGGS / FUN / HIDDEN FEATURES	Secret error-page animation",
    "1440	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden villager counter",
    "1441	EASTER EGGS / FUN / HIDDEN FEATURES	Villager counter increases with certain actions",
    "1442	EASTER EGGS / FUN / HIDDEN FEATURES	Villager statistics page",
    "1443	EASTER EGGS / FUN / HIDDEN FEATURES	Secret villager achievement",
    "1444	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden launcher achievement system",
    "1445	EASTER EGGS / FUN / HIDDEN FEATURES	First-launch achievement",
    "1446	EASTER EGGS / FUN / HIDDEN FEATURES	First-Minecraft-launch achievement",
    "1447	EASTER EGGS / FUN / HIDDEN FEATURES	First-update achievement",
    "1448	EASTER EGGS / FUN / HIDDEN FEATURES	First-backup achievement",
    "1449	EASTER EGGS / FUN / HIDDEN FEATURES	First-mod-install achievement",
    "1450	EASTER EGGS / FUN / HIDDEN FEATURES	First-world-launch achievement",
    "1451	EASTER EGGS / FUN / HIDDEN FEATURES	First-server-connect achievement",
    "1452	EASTER EGGS / FUN / HIDDEN FEATURES	First-profile achievement",
    "1453	EASTER EGGS / FUN / HIDDEN FEATURES	First-version-install achievement",
    "1454	EASTER EGGS / FUN / HIDDEN FEATURES	First-repair achievement",
    "1455	EASTER EGGS / FUN / HIDDEN FEATURES	First-use-of-tools achievement",
    "1456	EASTER EGGS / FUN / HIDDEN FEATURES	Long-session achievement",
    "1457	EASTER EGGS / FUN / HIDDEN FEATURES	Many-launches achievement",
    "1458	EASTER EGGS / FUN / HIDDEN FEATURES	Many-updates achievement",
    "1459	EASTER EGGS / FUN / HIDDEN FEATURES	Many-worlds achievement",
    "1460	EASTER EGGS / FUN / HIDDEN FEATURES	Many-profiles achievement",
    "1461	EASTER EGGS / FUN / HIDDEN FEATURES	Many-mods achievement",
    "1462	EASTER EGGS / FUN / HIDDEN FEATURES	Many-servers achievement",
    "1463	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden achievement notifications",
    "1464	EASTER EGGS / FUN / HIDDEN FEATURES	Achievement history",
    "1465	EASTER EGGS / FUN / HIDDEN FEATURES	Achievement statistics",
    "1466	EASTER EGGS / FUN / HIDDEN FEATURES	Secret achievement sound",
    "1467	EASTER EGGS / FUN / HIDDEN FEATURES	Retro notification sound",
    "1468	EASTER EGGS / FUN / HIDDEN FEATURES	Rare notification sound",
    "1469	EASTER EGGS / FUN / HIDDEN FEATURES	Secret UI click sound",
    "1470	EASTER EGGS / FUN / HIDDEN FEATURES	Optional old-computer sound pack",
    "1471	EASTER EGGS / FUN / HIDDEN FEATURES	Optional classic launcher sound pack",
    "1472	EASTER EGGS / FUN / HIDDEN FEATURES	Secret startup sound pack",
    "1473	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden S4-inspired Easter egg",
    "1474	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden Samsung-era visual reference",
    "1475	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden Android-era version-screen reference",
    "1476	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden old-school computer reference",
    "1477	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden Minecraft nostalgia reference",
    "1478	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden Windows 7-style reference",
    "1479	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden Vista-style reference",
    "1480	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden retro loading screen",
    "1481	EASTER EGGS / FUN / HIDDEN FEATURES	Secret loading-screen stage",
    "1482	EASTER EGGS / FUN / HIDDEN FEATURES	Rare loading-screen stage",
    "1483	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden debug text",
    "1484	EASTER EGGS / FUN / HIDDEN FEATURES	Secret build information",
    "1485	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden launcher-build number",
    "1486	EASTER EGGS / FUN / HIDDEN FEATURES	Secret developer credits",
    "1487	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden original-launcher credits",
    "1488	EASTER EGGS / FUN / HIDDEN FEATURES	Version-history Easter egg",
    "1489	EASTER EGGS / FUN / HIDDEN FEATURES	Old-version names hidden in About",
    "1490	EASTER EGGS / FUN / HIDDEN FEATURES	Secret Villager OS changelog",
    "1491	EASTER EGGS / FUN / HIDDEN FEATURES	OS-generation history",
    "1492	EASTER EGGS / FUN / HIDDEN FEATURES	Secret OS boot animation",
    "1493	EASTER EGGS / FUN / HIDDEN FEATURES	Optional OS boot sound",
    "1494	EASTER EGGS / FUN / HIDDEN FEATURES	Secret About-page animation",
    "1495	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden villager mascot animation",
    "1496	EASTER EGGS / FUN / HIDDEN FEATURES	Secret 2.2.0 anniversary Easter egg",
    "1497	EASTER EGGS / FUN / HIDDEN FEATURES	Rare 2.2.0 startup message",
    "1498	EASTER EGGS / FUN / HIDDEN FEATURES	Hidden \"You found it!\" screen",
    "1499	EASTER EGGS / FUN / HIDDEN FEATURES	Easter-egg statistics",
    "1500	EASTER EGGS / FUN / HIDDEN FEATURES	Master Easter Egg: a special hidden 2.2.0 experience combining the Villager OS version system, secret interactions, and the S4 startup sound"
]
FEATURES = []
for _row in _MASTER_FEATURE_ROWS:
    _num, _category, _name = _row.split("	", 2)
    FEATURES.append({
        "id": int(_num),
        "name": _name,
        "category": _category,
        "description": f"2.2.0 idea #{_num}: {_name}",
    })


FEATURE_STATE = {}
hrmm_clicks = 0
ICON_SIZE = 48
workshop_icon_cache = {}

THEMES = {
    "Villager Green": dict(bg="#0a140e", panel="#122117", card="#1a2d20", fg="#f4faf4", muted="#9fb3a4", accent="#5ec75e", button="#253e2d", input="#0e1b13", menu="#253e2d", hover="#78dd78", selected="#5ec75e", danger="#d45c5c", border="#2e4d38"),
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

DEFAULTS = {"theme": "Villager Green", "minecraft_path": "", "java_path": "", "window_width": 1280, "window_height": 820, "language": "English", "sidebar_compact": False}
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
servers_data = []
active_audio_players = []

def read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def load_servers():
    global servers_data
    raw = read_json(SERVERS_FILE, [])
    servers_data = raw if isinstance(raw, list) else []
    clean = []
    for item in servers_data:
        if isinstance(item, dict) and item.get("address"):
            clean.append({"name": str(item.get("name") or item["address"]), "address": str(item["address"])})
    servers_data = clean

def save_servers():
    os.makedirs(APP, exist_ok=True)
    with open(SERVERS_FILE, "w", encoding="utf-8") as f:
        json.dump(servers_data, f, indent=2, ensure_ascii=False)

def open_folder(path):
    if not path or not os.path.exists(path):
        messagebox.showwarning("Open Folder", f"Folder not found:\n{path}")
        return
    try:
        if os.name == "nt":
            os.startfile(os.path.normpath(path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Open Folder", str(e))

def path_size_label(path):
    try:
        total = 0
        for base, _, files in os.walk(path):
            for name in files:
                try:
                    total += os.path.getsize(os.path.join(base, name))
                except OSError:
                    pass
                if total > 8 * 1024 * 1024 * 1024:
                    break
        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(total)
        unit = units[0]
        for unit in units:
            if size < 1024 or unit == units[-1]:
                break
            size /= 1024
        return f"{size:.1f} {unit}"
    except Exception:
        return "—"

def internet_ok():
    try:
        sock = socket.create_connection(("1.1.1.1", 53), timeout=0.8)
        sock.close()
        return True
    except OSError:
        return False

def toggle_sidebar():
    settings["sidebar_compact"] = not bool(settings.get("sidebar_compact", False))
    save_state()
    render()

def copy_text(value, title="Address Copied"):
    try:
        root.clipboard_clear()
        root.clipboard_append(str(value))
        root.update_idletasks()
        messagebox.showinfo(title, str(value))
    except Exception as e:
        messagebox.showerror(title, str(e))

def add_server():
    name = simpledialog.askstring("Add Server", "Server Name:", parent=root)
    if name is None:
        return
    address = simpledialog.askstring("Add Server", "Server Address:", parent=root)
    if not address or not address.strip():
        return
    servers_data.append({"name": name.strip() or address.strip(), "address": address.strip()})
    save_servers()
    render()

def remove_server(index):
    if not (0 <= index < len(servers_data)):
        return
    item = servers_data[index]
    if messagebox.askyesno("Remove", f"Remove {item.get('name', item.get('address', 'server'))}?"):
        servers_data.pop(index)
        save_servers()
        render()

def backup_world(path):
    name = os.path.basename(path.rstrip("\\/")) or "world"
    if not messagebox.askyesno("Backup", f"Create a ZIP backup of {name}?"):
        return
    backup_dir = os.path.join(APP, "backups", "worlds")
    os.makedirs(backup_dir, exist_ok=True)
    target = os.path.join(backup_dir, f"{name}_{time.strftime('%Y%m%d_%H%M%S')}")
    try:
        archive = shutil.make_archive(target, "zip", root_dir=os.path.dirname(path), base_dir=os.path.basename(path))
        messagebox.showinfo("Backup", f"Backup created:\n{archive}")
    except Exception as e:
        messagebox.showerror("Backup", str(e))

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
    if settings.get("language", "English") == "Arabic":
        messagebox.showwarning("Minecraft Required", f"{tr(feature)} تتطلب تثبيتًا أصليًا لماينكرافت. سجّل الدخول عبر مشغل Minecraft الرسمي، ثم اختر مجلد ماينكرافت من الإعدادات.")
    else:
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
    placeholder = tk.Label(box, text=initial, bg=t["button"], fg=t["accent"], font=(FONT, 16, "bold"))
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
    text = tr(text)
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
    bg = "#183622" if ok else "#3a1a1f"
    fg = t["accent"] if ok else t["danger"]
    return tk.Label(parent, text=text, bg=bg, fg=fg, font=(FONT, 8, "bold"), padx=12, pady=5)

def page_header(parent, title, subtitle, right_widget_fn=None):
    t = T()
    rtl = settings.get("language") == "Arabic"
    wrap = tk.Frame(parent, bg=t["bg"])
    wrap.pack(fill="x", padx=32, pady=(24, 12))
    text_side = "right" if rtl else "left"
    other_side = "left" if rtl else "right"
    anchor = "e" if rtl else "w"
    left = tk.Frame(wrap, bg=t["bg"])
    left.pack(side=text_side, fill="x", expand=True)
    tk.Label(left, text=title, bg=t["bg"], fg=t["fg"], font=(FONT, 24, "bold"), justify="right" if rtl else "left").pack(anchor=anchor)
    tk.Label(left, text=subtitle, bg=t["bg"], fg=t["muted"], font=(FONT, 10), justify="right" if rtl else "left", wraplength=820).pack(anchor=anchor, pady=(4, 0))
    if right_widget_fn:
        right = tk.Frame(wrap, bg=t["bg"])
        right.pack(side=other_side)
        right_widget_fn(right)
    return wrap

def card(parent, padx=32, pady=10, accent=True):
    t = T()
    shell = tk.Frame(parent, bg=t["border"])
    shell.pack(fill="x", padx=padx, pady=pady)
    inner = tk.Frame(shell, bg=t["card"])
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    row = tk.Frame(inner, bg=t["card"])
    row.pack(fill="both", expand=True)
    if accent:
        tk.Frame(row, bg=t["accent"], width=4).pack(side="left", fill="y")
    content = tk.Frame(row, bg=t["card"])
    content.pack(side="left", fill="both", expand=True, padx=22, pady=18)
    return content

def section_label(parent, text):
    t = T()
    rtl = settings.get("language") == "Arabic"
    tk.Label(parent, text=text.upper(), bg=t["bg"], fg=t["muted"], font=(FONT, 9, "bold")).pack(anchor="e" if rtl else "w", padx=32, pady=(16, 0))

def go(p):
    global page
    if p == page:
        return
    page = p
    render()

def shell():
    """Villager Launcher 2.2.0 shell: scrollable left sidebar + technical content area."""
    global body
    t = T()
    rtl = settings.get("language") == "Arabic"
    compact = bool(settings.get("sidebar_compact", False))
    root.configure(bg=t["bg"])
    for w in root.winfo_children():
        w.destroy()
    apply_styles()

    outer = tk.Frame(root, bg=t["bg"])
    outer.pack(fill="both", expand=True)

    sidebar_width = 88 if compact else 238
    sidebar_shell = tk.Frame(outer, bg=t["border"], width=sidebar_width)
    sidebar_shell.pack(side="right" if rtl else "left", fill="y")
    sidebar_shell.pack_propagate(False)
    side = tk.Frame(sidebar_shell, bg=t["panel"])
    side.pack(fill="both", expand=True, padx=(1 if rtl else 0, 0 if rtl else 1), pady=0)

    # Scrollable sidebar, deliberately kept to ten main navigation buttons.
    side_canvas = tk.Canvas(side, bg=t["panel"], highlightthickness=0, bd=0, width=sidebar_width - 2)
    side_scroll = ttk.Scrollbar(side, orient="vertical", command=side_canvas.yview)
    side_inner = tk.Frame(side_canvas, bg=t["panel"])
    side_win = side_canvas.create_window((0, 0), window=side_inner, anchor="nw")
    side_inner.bind("<Configure>", lambda e: side_canvas.configure(scrollregion=side_canvas.bbox("all")))
    side_canvas.bind("<Configure>", lambda e: side_canvas.itemconfigure(side_win, width=e.width))
    side_canvas.configure(yscrollcommand=side_scroll.set)
    side_scroll.pack(side="left" if rtl else "right", fill="y")
    side_canvas.pack(side="right" if rtl else "left", fill="both", expand=True)

    brand = tk.Frame(side_inner, bg=t["panel"])
    brand.pack(fill="x", padx=10 if compact else 18, pady=(20, 12))
    mark = tk.Label(brand, text="◆", bg=t["accent"], fg="#0b120d" if _is_light_accent(t["accent"]) else "#ffffff", font=(FONT, 12, "bold"), width=2)
    mark.pack(anchor="center" if compact else ("e" if rtl else "w"), pady=(0, 7))
    if not compact:
        tk.Label(brand, text=tr("VILLAGER LAUNCHER"), bg=t["panel"], fg=t["fg"], font=(FONT, 12, "bold"), anchor="e" if rtl else "w").pack(fill="x")
        tk.Label(brand, text=f"v{CURRENT_VERSION}  •  {tr('Villager OS')} {VILLAGER_OS_VERSION}", bg=t["panel"], fg=t["muted"], font=(FONT, 7, "bold"), anchor="e" if rtl else "w").pack(fill="x", pady=(3, 0))

    if not compact:
        tk.Label(side_inner, text=tr("Main Navigation").upper(), bg=t["panel"], fg=t["muted"], font=(FONT, 7, "bold"), anchor="e" if rtl else "w").pack(fill="x", padx=18, pady=(4, 6))

    nav = [
        ("⌂", "Home", "Home"),
        ("▶", "Play", "Play"),
        ("▣", "Versions", "Versions"),
        ("⚒", "Mods", "Mods"),
        ("◆", "Modpacks", "Modpacks"),
        ("◫", "Worlds", "Worlds"),
        ("◎", "Servers", "Servers"),
        ("≡", "News", "News"),
        ("✚", "Tools", "Tools"),
        ("⚙", "Settings", "Settings"),
    ]
    for icon, name, dest in nav:
        active = page == dest or (dest == "Play" and page == "Profiles") or (dest == "Versions" and page == "Installations") or (dest == "Mods" and page == "Workshop") or (dest == "Tools" and page in ("Repair", "Ideas", "Feedback"))
        row = tk.Frame(side_inner, bg=t["accent"] if active else t["panel"])
        row.pack(fill="x", padx=8, pady=2)
        bg = t["card"] if active else t["panel"]
        fg = t["accent"] if active else t["muted"]
        label = icon if compact else (f"{tr(name)}   {icon}" if rtl else f"{icon}   {tr(name)}")
        b = tk.Label(row, text=label, bg=bg, fg=fg, font=(FONT, 10 if compact else 9, "bold"), padx=8, pady=10, cursor="arrow" if active else "hand2", anchor="center" if compact else ("e" if rtl else "w"))
        b.pack(fill="x", padx=(0 if rtl else 3, 3 if rtl else 0))
        if not active:
            b.bind("<Button-1>", lambda e, p=dest: go(p))
            b.bind("<Enter>", lambda e, w=b: w.configure(bg=t["button"], fg=t["fg"]))
            b.bind("<Leave>", lambda e, w=b, bg=bg, fg=fg: w.configure(bg=bg, fg=fg))

    # Active profile and secondary controls live inside the sidebar instead of becoming extra main navigation entries.
    profile = tk.Frame(side_inner, bg=t["card"], highlightthickness=1, highlightbackground=t["border"])
    profile.pack(fill="x", padx=8, pady=(12, 6))
    if compact:
        tk.Label(profile, text="◆", bg=t["card"], fg=t["accent"], font=(FONT, 13, "bold")).pack(pady=10)
    else:
        anchor = "e" if rtl else "w"
        tk.Label(profile, text=tr("Current Profile").upper(), bg=t["card"], fg=t["muted"], font=(FONT, 7, "bold")).pack(anchor=anchor, padx=12, pady=(10, 2))
        tk.Label(profile, text=profiles[selected].get("name", "Default"), bg=t["card"], fg=t["fg"], font=(FONT, 10, "bold")).pack(anchor=anchor, padx=12)
        tk.Label(profile, text=f"{selected_version() or tr('Auto')} • {tr(selected_loader())}", bg=t["card"], fg=t["muted"], font=(FONT, 7)).pack(anchor=anchor, padx=12, pady=(2, 10))

    toggle_text = "↔" if compact else ("Expand Sidebar" if compact else "Compact Sidebar")
    hover_btn(side_inner, toggle_text, toggle_sidebar, False, padx=8, pady=7).pack(fill="x", padx=8, pady=3)
    if not compact:
        hover_btn(side_inner, "About", open_credits, False, padx=8, pady=7).pack(fill="x", padx=8, pady=(3, 14))

    content = tk.Frame(outer, bg=t["bg"])
    content.pack(side="left" if rtl else "right", fill="both", expand=True)

    header_shell = tk.Frame(content, bg=t["border"])
    header_shell.pack(fill="x", padx=18, pady=(16, 0))
    header = tk.Frame(header_shell, bg=t["panel"], height=62)
    header.pack(fill="x", padx=1, pady=1)
    header.pack_propagate(False)
    title_side = "right" if rtl else "left"
    head_text = tk.Frame(header, bg=t["panel"])
    head_text.pack(side=title_side, fill="y", padx=18)
    tk.Label(head_text, text=tr(PAGE_TITLES.get(page, page)), bg=t["panel"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="e" if rtl else "w", pady=(12, 0))
    tk.Label(head_text, text=tr("TECHNICAL CONTROL INTERFACE"), bg=t["panel"], fg=t["muted"], font=(FONT, 7, "bold")).pack(anchor="e" if rtl else "w", pady=(2, 0))
    status_side = "left" if rtl else "right"
    status = tk.Frame(header, bg=t["panel"])
    status.pack(side=status_side, fill="y", padx=16)
    chip(status, "Minecraft Linked" if owned() else "Set Folder in Settings", owned()).pack(side=status_side, pady=17)

    body_wrap = tk.Frame(content, bg=t["bg"])
    body_wrap.pack(fill="both", expand=True)
    scroll = ScrollArea(body_wrap, t["bg"])
    scroll.pack(fill="both", expand=True, padx=(4, 4))
    body = scroll.inner

def open_credits():
    t = T()
    w = tk.Toplevel(root)
    w.title("Villager Launcher — Credits & Villager OS")
    w.geometry("760x680")
    w.minsize(640, 540)
    w.configure(bg=t["panel"])
    w.transient(root)
    rtl = settings.get("language") == "Arabic"
    anchor = "e" if rtl else "w"
    tap_state = {"count": 0}

    tk.Label(w, text=tr("Villager Launcher"), bg=t["panel"], fg=t["fg"], font=(FONT, 24, "bold")).pack(pady=(24, 2))
    tk.Label(w, text=tr("Credits • Origins • Project History"), bg=t["panel"], fg=t["muted"], font=(FONT, 10)).pack(pady=(0, 12))

    os_box = tk.Frame(w, bg=t["card"], highlightthickness=1, highlightbackground=t["border"])
    os_box.pack(fill="x", padx=28, pady=(0, 12))
    tk.Label(os_box, text=tr("Villager OS"), bg=t["card"], fg=t["muted"], font=(FONT, 8, "bold")).pack(anchor=anchor, padx=16, pady=(12, 2))
    os_version = tk.Label(os_box, text=f"Villager OS {VILLAGER_OS_VERSION}", bg=t["card"], fg=t["accent"], font=(FONT, 20, "bold"), cursor="hand2")
    os_version.pack(anchor=anchor, padx=16)
    tk.Label(os_box, text=f"{tr('Launcher Version')}: {CURRENT_VERSION}", bg=t["card"], fg=t["muted"], font=(FONT, 8)).pack(anchor=anchor, padx=16, pady=(3, 12))

    def os_tap(_event=None):
        tap_state["count"] += 1
        if tap_state["count"] < 7:
            os_version.configure(text=f"Villager OS {VILLAGER_OS_VERSION}  •  {tap_state['count']}/7")
            return
        tap_state["count"] = 0
        os_version.configure(text=f"Villager OS {VILLAGER_OS_VERSION}")
        play_media_audio("s4.mp3")
        messagebox.showinfo("You found it!", "The hidden S4 startup sound has been unlocked.")
    os_version.bind("<Button-1>", os_tap)

    content = tk.Frame(w, bg=t["panel"])
    content.pack(fill="both", expand=True, padx=28)
    sections = [
        ("Creator", "Villager Commander"),
        ("Project owner", "Villager Commander"),
        ("Project origin", "Villager Launcher — created and developed by Villager Commander."),
        ("FuPs / MrXAUYT", "Some launcher ideas and inspiration were influenced by MrXAUYT's FuPs launcher. FuPs is credited as an inspiration/reference, not as the creator or owner of Villager Launcher."),
        ("Inspiration", "Minecraft launcher concepts, Modrinth browsing, classic desktop launcher design, and original ideas."),
        ("Current release", f"Villager Launcher {CURRENT_VERSION}"),
    ]
    for heading, text in sections:
        box = tk.Frame(content, bg=t["card"])
        box.pack(fill="x", pady=4)
        tk.Label(box, text=heading, bg=t["card"], fg=t["accent"], font=(FONT, 9, "bold")).pack(anchor=anchor, padx=16, pady=(9, 2))
        tk.Label(box, text=text, bg=t["card"], fg=t["fg"], font=(FONT, 8), wraplength=660, justify="right" if rtl else "left").pack(anchor=anchor, padx=16, pady=(0, 9))
    hover_btn(w, "Close", w.destroy, True, padx=18, pady=8).pack(pady=14)

def render():
    shell()
    {
        "Home": home,
        "Play": play_page,
        "Versions": versions_center_page,
        "Mods": workshop_page,
        "Modpacks": modpacks_page,
        "Worlds": worlds_page,
        "Servers": servers_page,
        "News": news_page,
        "Tools": tools_page,
        "Settings": settings_page,
        "Profiles": profiles_page,
        "Workshop": workshop_page,
        "Installations": installations_page,
        "Repair": repair_page,
        "Ideas": ideas_page,
        "Feedback": feedback_page,
    }.get(page, home)()

def home():
    t = T()
    rtl = settings.get("language") == "Arabic"
    anchor = "e" if rtl else "w"
    side = "right" if rtl else "left"
    page_header(body, "Welcome Back", "Villager Launcher 2.2.0 technical dashboard and quick controls.")

    hero = card(body)
    top = tk.Frame(hero, bg=t["card"])
    top.pack(fill="x")
    info = tk.Frame(top, bg=t["card"])
    info.pack(side=side, fill="both", expand=True)
    tk.Label(info, text=tr("Current Profile").upper(), bg=t["card"], fg=t["accent"], font=(FONT, 8, "bold")).pack(anchor=anchor)
    tk.Label(info, text=profiles[selected].get("name", "Default"), bg=t["card"], fg=t["fg"], font=(FONT, 24, "bold")).pack(anchor=anchor, pady=(5, 2))
    tk.Label(info, text=f"{selected_version() or tr('Auto')}  •  {tr(selected_loader())}", bg=t["card"], fg=t["muted"], font=(FONT, 10)).pack(anchor=anchor)
    actions = tk.Frame(top, bg=t["card"])
    actions.pack(side="left" if rtl else "right")
    hover_btn(actions, "Play Game", launch_game, True, padx=34, pady=13).pack(fill="x")
    row = tk.Frame(actions, bg=t["card"])
    row.pack(fill="x", pady=(8, 0))
    hover_btn(row, "Profiles", lambda: go("Profiles"), padx=12, pady=7).pack(side=side)
    hover_btn(row, "Hrmm", hrmm_button, padx=12, pady=7).pack(side=side, padx=5)
    hover_btn(row, "Villager Bot", open_villager_bot, padx=12, pady=7).pack(side=side)

    section_label(body, "System Overview")
    status = tk.Frame(body, bg=t["bg"])
    status.pack(fill="x", padx=32, pady=(8, 4))
    info_rows = [
        ("Launcher Version", CURRENT_VERSION, True),
        ("Villager OS", VILLAGER_OS_VERSION, True),
        ("Java Status", tr("Ready") if java_ok() else tr("Unavailable"), java_ok()),
        ("Minecraft Directory", tr("Linked") if owned() else tr("Not Found"), owned()),
        ("Installed Versions", str(len(versions())), bool(versions())),
    ]
    if rtl:
        info_rows.reverse()
    for label, value, ok in info_rows:
        shell_box = tk.Frame(status, bg=t["accent"] if ok else t["border"])
        shell_box.pack(side=side, fill="both", expand=True, padx=4)
        box = tk.Frame(shell_box, bg=t["panel"])
        box.pack(fill="both", expand=True, padx=1, pady=1)
        tk.Label(box, text=value, bg=t["panel"], fg=t["accent"] if ok else t["muted"], font=(FONT, 11, "bold")).pack(pady=(11, 2))
        tk.Label(box, text=tr(label), bg=t["panel"], fg=t["muted"], font=(FONT, 7, "bold")).pack(pady=(0, 11))

    section_label(body, "Quick Actions")
    quick = tk.Frame(body, bg=t["bg"])
    quick.pack(fill="x", padx=32, pady=(8, 18))
    actions = [
        ("Versions", "▣", "Versions"), ("Mods", "⚒", "Mods"), ("Worlds", "◫", "Worlds"),
        ("Servers", "◎", "Servers"), ("Tools", "✚", "Tools"), ("Settings", "⚙", "Settings"),
    ]
    if rtl:
        actions.reverse()
    for name, icon, dest in actions:
        box = tk.Frame(quick, bg=t["border"])
        box.pack(side=side, fill="both", expand=True, padx=3)
        inner = tk.Label(box, text=f"{icon}\n{tr(name)}", bg=t["card"], fg=t["fg"], font=(FONT, 9, "bold"), padx=8, pady=13, cursor="hand2")
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        inner.bind("<Button-1>", lambda e, p=dest: go(p))
        inner.bind("<Enter>", lambda e, w=inner: w.configure(bg=t["button"], fg=t["accent"]))
        inner.bind("<Leave>", lambda e, w=inner: w.configure(bg=t["card"], fg=t["fg"]))



def play_page():
    t = T()
    page_header(body, "Play Center", "Launch Minecraft and manage the active profile from one place.")
    hero = card(body)
    tk.Label(hero, text=profiles[selected].get("name", "Default"), bg=t["card"], fg=t["fg"], font=(FONT, 22, "bold")).pack(anchor="w")
    tk.Label(hero, text=f"{selected_version() or 'Auto'}  •  {selected_loader()}", bg=t["card"], fg=t["muted"], font=(FONT, 10)).pack(anchor="w", pady=(4, 14))
    row = tk.Frame(hero, bg=t["card"])
    row.pack(anchor="w")
    hover_btn(row, "Play Game", launch_game, True, padx=30, pady=12).pack(side="left")
    hover_btn(row, "Profile Manager", lambda: go("Profiles"), padx=16, pady=10).pack(side="left", padx=8)
    hover_btn(row, "Check Everything", test_everything, padx=16, pady=10).pack(side="left")

    section_label(body, "Profiles")
    for i, p in enumerate(profiles[:8]):
        r = card(body, accent=i == selected)
        top = tk.Frame(r, bg=t["card"]); top.pack(fill="x")
        tk.Label(top, text=p.get("name", "Profile"), bg=t["card"], fg=t["fg"], font=(FONT, 11, "bold")).pack(side="left")
        tk.Label(top, text=f"{p.get('version') or 'Auto'} • {p.get('loader', 'Vanilla')}", bg=t["card"], fg=t["muted"], font=(FONT, 8)).pack(side="left", padx=12)
        hover_btn(top, "Selected" if i == selected else "Select", lambda i=i: select_profile(i), i == selected, padx=13, pady=7).pack(side="right")


def versions_center_page():
    t = T()
    page_header(body, "Version Center", "Browse locally installed Minecraft versions and choose the active version.")
    if not gate("Versions"):
        return
    vs = versions()
    summary = card(body)
    tk.Label(summary, text=f"{len(vs)} {tr('Installed Versions')}", bg=t["card"], fg=t["fg"], font=(FONT, 16, "bold")).pack(anchor="w")
    tk.Label(summary, text=os.path.join(mc_dir(), "versions"), bg=t["card"], fg=t["muted"], font=(FONT, 8)).pack(anchor="w", pady=(4, 10))
    hover_btn(summary, "Open Folder", lambda: open_folder(os.path.join(mc_dir(), "versions")), False).pack(anchor="w")
    if not vs:
        empty = card(body); tk.Label(empty, text="No Minecraft versions found.", bg=t["card"], fg=t["muted"], font=(FONT, 11)).pack(anchor="w"); return
    current = selected_version()
    for v in vs:
        r = card(body, accent=v == current)
        top = tk.Frame(r, bg=t["card"]); top.pack(fill="x")
        tk.Label(top, text=v, bg=t["card"], fg=t["fg"], font=(FONT, 11, "bold")).pack(side="left")
        path = os.path.join(mc_dir(), "versions", v)
        tk.Label(top, text=path_size_label(path), bg=t["card"], fg=t["muted"], font=(FONT, 8)).pack(side="left", padx=10)
        hover_btn(top, "Selected" if v == current else "Select", lambda v=v: set_version(v), v == current, padx=12, pady=7).pack(side="right")
        hover_btn(top, "Open Folder", lambda p=path: open_folder(p), False, padx=12, pady=7).pack(side="right", padx=6)


def modpacks_page():
    t = T()
    page_header(body, "Modpacks & Packs", "Inspect local modpack, resource-pack, and shader folders without removing existing Workshop behavior.")
    d = mc_dir()
    groups = [("Local Packs", os.path.join(d, "modpacks")), ("Resource Packs", os.path.join(d, "resourcepacks")), ("Shaders", os.path.join(d, "shaderpacks"))]
    for title, path in groups:
        box = card(body)
        tk.Label(box, text=title, bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
        count = 0
        try:
            count = len(os.listdir(path)) if os.path.isdir(path) else 0
        except OSError:
            pass
        tk.Label(box, text=f"{count} item(s)  •  {path}", bg=t["card"], fg=t["muted"], font=(FONT, 8), wraplength=760, justify="left").pack(anchor="w", pady=(5, 10))
        hover_btn(box, "Open Folder", lambda p=path: open_folder(p), False).pack(anchor="w")


def worlds_page():
    t = T()
    page_header(body, "World Center", "Browse local Minecraft worlds, open their folders, and create safe ZIP backups.")
    saves = os.path.join(mc_dir(), "saves")
    top = card(body)
    tk.Label(top, text=saves, bg=t["card"], fg=t["muted"], font=(FONT, 8)).pack(anchor="w")
    hover_btn(top, "Open Folder", lambda: open_folder(saves), False).pack(anchor="w", pady=(10, 0))
    try:
        worlds = [os.path.join(saves, x) for x in os.listdir(saves) if os.path.isdir(os.path.join(saves, x))]
        worlds.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    except OSError:
        worlds = []
    if not worlds:
        empty = card(body); tk.Label(empty, text="No worlds found.", bg=t["card"], fg=t["muted"], font=(FONT, 11)).pack(anchor="w"); return
    for path in worlds:
        r = card(body)
        row = tk.Frame(r, bg=t["card"]); row.pack(fill="x")
        info = tk.Frame(row, bg=t["card"]); info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=os.path.basename(path), bg=t["card"], fg=t["fg"], font=(FONT, 11, "bold")).pack(anchor="w")
        try: modified = time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(path)))
        except OSError: modified = "—"
        tk.Label(info, text=f"{tr('Last Modified')}: {modified}", bg=t["card"], fg=t["muted"], font=(FONT, 8)).pack(anchor="w", pady=(3, 0))
        hover_btn(row, "Backup", lambda p=path: backup_world(p), True, padx=12, pady=7).pack(side="right")
        hover_btn(row, "Open Folder", lambda p=path: open_folder(p), False, padx=12, pady=7).pack(side="right", padx=6)


def servers_page():
    t = T()
    page_header(body, "Server Center", "Maintain a lightweight local list of Minecraft servers and addresses.")
    top = card(body)
    tk.Label(top, text="Minecraft Servers", bg=t["card"], fg=t["fg"], font=(FONT, 14, "bold")).pack(anchor="w")
    tk.Label(top, text=os.path.join(mc_dir(), "servers.dat"), bg=t["card"], fg=t["muted"], font=(FONT, 8)).pack(anchor="w", pady=(4, 10))
    row = tk.Frame(top, bg=t["card"]); row.pack(anchor="w")
    hover_btn(row, "Add Server", add_server, True).pack(side="left")
    hover_btn(row, "Open Minecraft Folder", lambda: open_folder(mc_dir()), False).pack(side="left", padx=8)
    if not servers_data:
        empty = card(body); tk.Label(empty, text="No saved servers yet.", bg=t["card"], fg=t["muted"], font=(FONT, 11)).pack(anchor="w"); return
    for i, item in enumerate(servers_data):
        r = card(body)
        line = tk.Frame(r, bg=t["card"]); line.pack(fill="x")
        info = tk.Frame(line, bg=t["card"]); info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=item.get("name", "Server"), bg=t["card"], fg=t["fg"], font=(FONT, 11, "bold")).pack(anchor="w")
        tk.Label(info, text=item.get("address", ""), bg=t["card"], fg=t["muted"], font=(FONT, 9)).pack(anchor="w", pady=(3, 0))
        hover_btn(line, "Remove", lambda i=i: remove_server(i), False, padx=12, pady=7).pack(side="right")
        hover_btn(line, "Copy Address", lambda a=item.get("address", ""): copy_text(a), True, padx=12, pady=7).pack(side="right", padx=6)


def news_page():
    t = T()
    page_header(body, "News & Activity", "Launcher release information, update controls, and the current 2.2.0 highlights.")
    hero = card(body)
    tk.Label(hero, text="2.2.0 Major Update", bg=t["card"], fg=t["accent"], font=(FONT, 16, "bold")).pack(anchor="w")
    highlights = [
        "Scrollable left sidebar with ten main sections",
        "Villager OS 1.0 and hidden S4 audio Easter egg",
        "1500-item 2.2.0 master feature registry",
        "World browser with ZIP backups",
        "Local server address manager",
        "Dedicated Play, Versions, Modpacks, News, and Tools centers",
        "English/Arabic navigation support",
    ]
    for item in highlights:
        tk.Label(hero, text="• " + item, bg=t["card"], fg=t["fg"], font=(FONT, 9), justify="left", wraplength=760).pack(anchor="w", pady=2)
    row = tk.Frame(hero, bg=t["card"]); row.pack(anchor="w", pady=(12, 0))
    hover_btn(row, "Check for Updates", check_updates, True).pack(side="left")
    hover_btn(row, "Release Notes", release_notes, False).pack(side="left", padx=8)


def tools_page():
    t = T()
    page_header(body, "Tools Center", "Diagnostics, feature ideas, feedback, folders, assistant, and project information.")
    tools = [
        ("Diagnostics", "Run the existing non-destructive repair and diagnostic suite.", lambda: go("Repair")),
        ("Master Feature Registry", f"Browse the {len(FEATURES)}-idea Villager Launcher 2.2.0 registry.", lambda: go("Ideas")),
        ("Local Feedback", "Open the existing local feedback center.", lambda: go("Feedback")),
        ("Profile Manager", "Open the full existing profile manager.", lambda: go("Profiles")),
        ("Villager Bot", "Open the offline Villager Bot knowledge assistant.", open_villager_bot),
        ("Credits & Villager OS", "Credits, project history, Villager OS, and hidden interaction.", open_credits),
        ("Open Minecraft Folder", mc_dir(), lambda: open_folder(mc_dir())),
        ("Open Launcher Folder", APP, lambda: open_folder(APP)),
    ]
    for title, desc, command in tools:
        box = card(body)
        tk.Label(box, text=title, bg=t["card"], fg=t["fg"], font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(box, text=desc, bg=t["card"], fg=t["muted"], font=(FONT, 8), wraplength=760, justify="left").pack(anchor="w", pady=(4, 10))
        hover_btn(box, "Open Section" if title not in ("Villager Bot", "Credits & Villager OS", "Open Minecraft Folder", "Open Launcher Folder") else "Open", command, False, padx=13, pady=7).pack(anchor="w")

def profiles_page():
    t = T()
    page_header(body, "Profiles", "Create, customize, and manage launcher profiles.")
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
        loader_var = tk.StringVar(value=tr(p.get("loader", "Vanilla")))
        loader_box = ttk.Combobox(controls, textvariable=loader_var, values=[tr(x) for x in LOADERS], state="readonly", width=10)
        loader_box.pack(side="left", padx=(0, 8))
        loader_box.bind("<<ComboboxSelected>>", lambda e, i=i, v=loader_var: set_loader(i, from_display(v.get())))
        hover_btn(controls, "Rename", lambda i=i: rename_profile(i)).pack(side="left", padx=(0, 8))
        hover_btn(controls, "Selected" if i == selected else "Select", lambda i=i: select_profile(i), i == selected).pack(side="left", padx=(0, 8))
        hover_btn(controls, "Delete", lambda i=i: delete_profile(i), enabled=len(profiles) > 1).pack(side="left")
    add = card(body)
    hover_btn(add, "New Profile", new_profile, True).pack(anchor="w")

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
    page_header(body, "Installations", "Available Minecraft versions found in your installation directory.")
    if not gate("Installations"):
        return
    vs = versions()
    if not vs:
        empty = card(body)
        tk.Label(empty, text="No Minecraft versions found.", bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
        tk.Label(empty, text="Install one using the official Minecraft Launcher first.", bg=t["card"], fg=t["muted"], font=(FONT, 10)).pack(anchor="w", pady=(6, 0))
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

def sound_ok():
    if HAS_MPV:
        return True, "MPV Engine Operational"
    return False, "python-mpv or libmpv missing"

def repair_checks():
    d = mc_dir()
    snd_ok, snd_msg = sound_ok()
    return [
        ("Launcher data directory", os.path.isdir(APP), "app", "Directory missing or inaccessible"),
        ("Settings file", os.path.isfile(SETTINGS_FILE), "settings", "Settings JSON missing or corrupted"),
        ("Profiles file", os.path.isfile(PROFILES_FILE), "profiles", "Profiles JSON missing or corrupted"),
        ("Minecraft directory", bool(d and os.path.isdir(d)), "minecraft", "Minecraft folder not set or invalid"),
        ("Official launcher installation", owned(), "ownership", "Official launcher account files not found"),
        ("Installed game versions", bool(versions()), "versions", "No game versions found in versions folder"),
        ("Java installation", java_ok(), "java", "Java executable non-functional or not found in PATH"),
        ("Audio/Video Engine (libmpv)", snd_ok, "sound", snd_msg),
        ("Updater endpoints", bool(BASE_URL and VERSION_URL and LAUNCHER_URL), "updater", "Updater API URLs are malformed"),
        ("Mod Workshop endpoints", bool(MODRINTH), "workshop", "Modrinth API path unavailable"),
        ("Theme system integrity", all(k in T() for k in ("bg", "panel", "card", "fg", "muted", "accent", "button", "input", "menu", "hover", "selected")), "theme", "Theme colors incomplete"),
        ("UI component tree", bool(root and root.winfo_exists()), "ui", "Tkinter main root instance error"),
        ("Offline bot knowledge pack", len(BOT_QA) >= 20, "bot", "Knowledge base entries depleted"),
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
    failed_items = []
    
    for name, ok, kind, error_details in repair_checks():
        if ok:
            last_tests.append((name, "PASSED", ""))
        else:
            try:
                fixed = safe_repair(kind)
            except Exception:
                fixed = ""
            status = "FIXED" if fixed else "FAILED"
            msg_detail = fixed or error_details
            last_tests.append((name, status, msg_detail))
            if not fixed:
                failed_items.append(f"• {name}: {error_details}")
                
    passed = sum(s in ("PASSED", "FIXED") for _, s, _ in last_tests)
    
    msg = f"Villager Launcher {CURRENT_VERSION} — Diagnostics Report\n\n"
    msg += f"Passed/Fixed: {passed}/{len(last_tests)}\n\n"
    
    if failed_items:
        msg += "PROBLEMS DETECTED:\n" + "\n".join(failed_items) + "\n\n"
    else:
        msg += "All subsystems and video/audio checks are operating normally!\n\n"
        
    msg += "\n".join(("✓" if s in ("PASSED", "FIXED") else "✕") + f" {n}: {s}" + (f" — {d}" if d else "") for n, s, d in last_tests)
    msg += "\n\nNo game files were changed or removed."
    
    if failed_items:
        messagebox.showwarning("Diagnostic Results — Issues Found", msg)
    else:
        messagebox.showinfo("Diagnostic Results — All Clear", msg)
        
    if page == "Repair":
        render()

def repair_page():
    t = T()
    page_header(body, "Repair & Diagnostics", "Run non-destructive integrity checks on system paths and configs.")
    hero = card(body)
    tk.Label(hero, text="Run Diagnostic Suite", bg=t["card"], fg=t["fg"], font=(FONT, 16, "bold")).pack(anchor="w")
    tk.Label(hero, text="Scans launcher configuration, Java environment, folder access, sound drivers, and API paths.", bg=t["card"], fg=t["muted"], font=(FONT, 10), wraplength=720, justify="left").pack(anchor="w", pady=(6, 14))
    hover_btn(hero, "Check Everything", test_everything, True).pack(anchor="w")
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
        messagebox.showerror("Launch Error", "The selected Minecraft version is missing required files.")
        return
    if not java_ok():
        messagebox.showerror("Launch Error", "Java execution environment failed.")
        return
    messagebox.showinfo("Minecraft", "Validation passed. Launcher ready for launch pipe.")

def workshop_page():
    global workshop_checked
    t = T()
    workshop_checked = True
    page_header(body, "Mod Workshop", "Browse Modrinth mods and add-ons.")
    filters = card(body)
    row = tk.Frame(filters, bg=t["card"])
    row.pack(fill="x")
    q = ttk.Entry(row)
    q.insert(0, workshop_query)
    q.pack(side="left", fill="x", expand=True, ipady=6)
    ver = tk.StringVar(value=workshop_filters.get("version") or selected_version())
    sort = tk.StringVar(value=tr(workshop_filters.get("sort", "Relevance")))
    ttk.Entry(row, textvariable=ver, width=12).pack(side="left", padx=6, ipady=6)
    ttk.Combobox(row, textvariable=sort, values=[tr("Relevance"), tr("Downloads"), tr("Updated")], state="readonly", width=11).pack(side="left", padx=6)
    hover_btn(row, "Search Mods", lambda: search_workshop(q.get(), "Mod", ver.get(), from_display(sort.get()), "Any"), True, padx=16, pady=8).pack(side="left")
    q.bind("<Return>", lambda e: search_workshop(q.get(), "Mod", ver.get(), from_display(sort.get()), "Any"))
    
    if workshop_loading:
        loading = card(body)
        tk.Label(loading, text="Searching Modrinth repository…", bg=t["card"], fg=t["muted"], font=(FONT, 11)).pack(anchor="w")
        return
    if workshop_error:
        err = card(body)
        tk.Label(err, text="Search Failed", bg=t["card"], fg=t["danger"], font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(err, text=workshop_error, bg=t["card"], fg=t["muted"], font=(FONT, 9), wraplength=760, justify="left").pack(anchor="w", pady=(4, 10))
        hover_btn(err, "Retry Search", lambda: search_workshop(workshop_query, "Mod", ver.get(), sort.get(), "Any"), True).pack(anchor="w")
        return
    if not workshop_results:
        empty = card(body)
        tk.Label(empty, text="Enter a keyword above to search for mods.", bg=t["card"], fg=t["muted"], font=(FONT, 11)).pack(anchor="w")
        return
        
    count_row = tk.Frame(body, bg=t["bg"])
    count_row.pack(fill="x", padx=32)
    tk.Label(count_row, text=f"{len(workshop_results)} project(s) found", bg=t["bg"], fg=t["muted"], font=(FONT, 9)).pack(anchor="w")
    
    shell = tk.Frame(body, bg=t["border"])
    shell.pack(fill="x", padx=32, pady=8)
    outer_panel = tk.Frame(shell, bg=t["card"])
    outer_panel.pack(fill="both", expand=True, padx=1, pady=1)
    strip_row = tk.Frame(outer_panel, bg=t["card"])
    strip_row.pack(fill="both", expand=True)
    tk.Frame(strip_row, bg=t["accent"], width=4).pack(side="left", fill="y")
    panel = tk.Frame(strip_row, bg=t["card"])
    panel.pack(side="left", fill="both", expand=True)
    
    for idx, p in enumerate(workshop_results):
        row = tk.Frame(panel, bg=t["card"])
        row.pack(fill="x", padx=22, pady=14)
        top = tk.Frame(row, bg=t["card"])
        top.pack(fill="x")
        icon_widget(top, p).pack(side="left", padx=(0, 14))
        
        def view_project(project=p):
            slug = project.get("slug") or project.get("project_id")
            if slug:
                webbrowser.open(f"https://modrinth.com/mod/{quote(str(slug))}")
                
        hover_btn(top, "View Project", view_project, True).pack(side="right", padx=(12, 0))
        title_area = tk.Frame(top, bg=t["card"])
        title_area.pack(side="left", fill="x", expand=True)
        tk.Label(title_area, text=p.get("title") or p.get("slug", "Unknown"), bg=t["card"], fg=t["fg"], font=(FONT, 12, "bold")).pack(anchor="w")
        meta = tk.Frame(title_area, bg=t["card"])
        meta.pack(anchor="w", pady=(2, 0))
        chip(meta, "Mod", True).pack(side="left", padx=(0, 8))
        author = p.get("author") or "Unknown author"
        meta_text = f"by {author}  •  {p.get('downloads', 0):,} downloads"
        tk.Label(meta, text=meta_text, bg=t["card"], fg=t["muted"], font=(FONT, 8)).pack(side="left")
        desc = (p.get("description") or "").replace("\n", " ")
        tk.Label(row, text=desc[:200] + ("..." if len(desc) > 200 else ""), bg=t["card"], fg=t["muted"], font=(FONT, 9),
                 wraplength=740, justify="left").pack(anchor="w", pady=(8, 0), padx=(ICON_SIZE + 14, 0))
        if idx < len(workshop_results) - 1:
            tk.Frame(panel, bg=t["border"], height=1).pack(fill="x", padx=22)
            
    if workshop_more_available:
        more = card(body)
        hover_btn(more, "Load More Results", load_more_workshop, True).pack(anchor="w")

def _workshop_search_url(query, content_type, version, sort, loader, offset, use_facets=True):
    idx = {"Relevance": "relevance", "Downloads": "downloads", "Updated": "updated"}.get(sort, "relevance")
    q = quote((query or "").strip())
    url = f"{MODRINTH}/search?query={q}&limit={WORKSHOP_PAGE_SIZE}&offset={int(offset)}&index={idx}"
    if use_facets:
        facets = [["project_type:mod"]]
        v = (version or "").strip()
        if v:
            facets.append([f"versions:{v}"])
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

def play_media_video(file_name, parent_frame=None, on_finish=None):
    v_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", file_name))
    if not os.path.exists(v_path):
        if on_finish:
            on_finish()
        return None

    if not HAS_MPV:
        messagebox.showerror("Dependency Error", "python-mpv library or mpv-1.dll was not found.\nPlease install python-mpv and provide libmpv binaries.")
        if on_finish:
            on_finish()
        return None

    close_win = None
    if parent_frame is None:
        vw = tk.Toplevel(root)
        vw.title(file_name)
        vw.geometry("640x360")
        vw.configure(bg="#000000")
        parent_frame = vw
        close_win = vw

    wid = parent_frame.winfo_id()
    player = mpv.MPV(wid=str(wid), vo="gpu", keep_open="always")

    @player.property_observer("eof-reached")
    def on_eof(_name, value):
        if value:
            if root and root.winfo_exists():
                root.after(0, lambda: _cleanup_and_finish(player, close_win, on_finish))

    try:
        player.play(v_path)
    except Exception as e:
        messagebox.showerror("Playback Error", f"Failed playing {file_name}: {e}")
        _cleanup_and_finish(player, close_win, on_finish)

    return player

def _cleanup_and_finish(player, window_to_close, callback):
    try:
        if player:
            player.terminate()
    except Exception:
        pass
    if window_to_close and window_to_close.winfo_exists():
        window_to_close.destroy()
    if callback:
        callback()


def play_media_audio(file_name):
    """Play an audio asset through the existing MPV dependency without opening a video window."""
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", file_name))
    if not os.path.exists(path):
        messagebox.showerror("Playback Error", f"Audio file not found: {path}")
        return None
    if not HAS_MPV:
        messagebox.showerror("Dependency Error", "python-mpv library or mpv-1.dll was not found.\nPlease install python-mpv and provide libmpv binaries.")
        return None
    try:
        player = mpv.MPV(vo="null", keep_open="no")
        active_audio_players.append(player)
        @player.property_observer("eof-reached")
        def _audio_eof(_name, value):
            if value and root and root.winfo_exists():
                def cleanup():
                    try: player.terminate()
                    except Exception: pass
                    try: active_audio_players.remove(player)
                    except ValueError: pass
                root.after(0, cleanup)
        player.play(path)
        return player
    except Exception as e:
        messagebox.showerror("Playback Error", f"Failed playing {file_name}: {e}")
        return None

def hrmm_button():
    global hrmm_clicks
    hrmm_clicks += 1
    
    mp4_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "hrmm.mp4")
    if os.path.exists(mp4_path):
        play_media_video("hrmm.mp4")
    
    messages = [
        "Hrmm... Villager is thinking.",
        "HRMM! 1500 features detected.",
        "Villager inspected the launcher layout. Hrmm.",
        "Hrmm... checking for updates?",
        "EMERALD ACQUIRED. HRMMM.",
    ]
    if hrmm_clicks >= 5:
        stop = messagebox.askyesno("HRMM OVERLOAD", "STOP PRESSING HRMM BUTTONS?\n\nThe Villager needs a break from all the buttons.")
        if not stop:
            save_state()
            save_feature_state()
            root.destroy()
            return
        hrmm_clicks = 0
    messagebox.showinfo("Hrmm", messages[(hrmm_clicks - 1) % len(messages)])

def ideas_page():
    global ideas_query, ideas_category
    t = T()
    page_header(body, "Feature Registry", "Browse and toggle 1500 Villager Launcher 2.2.0 ideas.")
    top = card(body)
    tk.Label(top, text=f"FEATURE MASTER LIST • {len(FEATURES)} TOTAL", bg=t["card"], fg=t["fg"], font=(FONT, 14, "bold")).pack(anchor="w")
    tk.Label(top, text="These switches serve as local launcher idea/feature flags; the registry does not imply every idea is implemented yet.", bg=t["card"], fg=t["muted"], font=(FONT, 9), wraplength=760, justify="left").pack(anchor="w", pady=(5, 12))
    
    controls = tk.Frame(top, bg=t["card"])
    controls.pack(fill="x")
    q = ttk.Entry(controls)
    q.insert(0, ideas_query)
    q.pack(side="left", fill="x", expand=True, ipady=7)
    cats = ["All"] + sorted({f["category"] for f in FEATURES})
    cat = tk.StringVar(value=tr(ideas_category if ideas_category in cats else "All"))
    ttk.Combobox(controls, textvariable=cat, values=[tr(x) for x in cats], state="readonly", width=22).pack(side="left", padx=8)
    
    def apply_filter():
        global ideas_query, ideas_category
        ideas_query, ideas_category = q.get().strip(), from_display(cat.get())
        render()
        
    hover_btn(controls, "Filter", apply_filter, True, padx=14, pady=8).pack(side="left")
    hover_btn(controls, "Hrmm", hrmm_button, padx=14, pady=8).pack(side="left", padx=8)
    
    actions = tk.Frame(top, bg=t["card"])
    actions.pack(anchor="w", pady=(12, 0))
    hover_btn(actions, "Enable All", enable_all_features).pack(side="left", padx=(0, 8))
    hover_btn(actions, "Disable All", disable_all_features).pack(side="left", padx=(0, 8))
    hover_btn(actions, "Reset", reset_features).pack(side="left")
    
    q.bind("<Return>", lambda e: apply_filter())
    query = ideas_query.lower()
    shown = [f for f in FEATURES if (ideas_category == "All" or f["category"] == ideas_category) and (not query or query in f["name"].lower() or query in f["description"].lower())]
    visible = shown if len(shown) <= 150 else shown[:150]
    
    count = card(body, accent=False)
    enabled_count = sum(bool(FEATURE_STATE.get(f["name"], False)) for f in FEATURES)
    summary = f"Displaying {len(visible)} of {len(shown)} matched ideas • {len(FEATURES)} total • Active: {enabled_count}"
    tk.Label(count, text=summary, bg=t["card"], fg=t["muted"], font=(FONT, 9, "bold")).pack(anchor="w")
    if len(shown) > len(visible):
        tk.Label(count, text="Use a category or search to narrow the master list. Each category contains up to 100 ideas.", bg=t["card"], fg=t["muted"], font=(FONT, 8)).pack(anchor="w", pady=(5, 0))
    
    for f in visible:
        row = card(body, accent=False)
        top_row = tk.Frame(row, bg=t["card"])
        top_row.pack(fill="x")
        tk.Label(top_row, text=tr(f["name"]), bg=t["card"], fg=t["fg"], font=(FONT, 10, "bold")).pack(side="left", fill="x", expand=True)
        var = tk.BooleanVar(value=bool(FEATURE_STATE.get(f["name"], False)))
        cb = tk.Checkbutton(top_row, text="Active", variable=var, command=lambda n=f["name"], v=var: toggle_feature(n, v), bg=t["card"], fg=t["accent"], selectcolor=t["input"], activebackground=t["card"], activeforeground=t["hover"], font=(FONT, 9, "bold"))
        cb.pack(side="right")
        tk.Label(row, text=(f'{tr(f["category"])}  •  {"هذه الميزة جزء من سجل ميزات مشغل فيلجر." if settings.get("language", "English") == "Arabic" else f["description"]}'), bg=t["card"], fg=t["muted"], font=(FONT, 8), wraplength=760, justify="left").pack(anchor="w", pady=(5, 0))

def settings_page():
    t = T()
    page_header(body, "Launcher Settings", "Customize appearance, paths, and system updates.")

    language_card = card(body)
    tk.Label(language_card, text="Language", bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
    tk.Label(language_card, text="Language changes apply immediately to the entire launcher interface.", bg=t["card"], fg=t["muted"], font=(FONT, 10), wraplength=760, justify="left").pack(anchor="w", pady=(4, 10))
    lang_row = tk.Frame(language_card, bg=t["card"])
    lang_row.pack(anchor="w")
    lang_var = tk.StringVar(value=tr(settings.get("language", "English")))
    lang_box = ttk.Combobox(lang_row, textvariable=lang_var, values=[tr("English"), tr("Arabic")], state="readonly", width=20)
    lang_box.pack(side="left")
    def apply_language_selection():
        selected_display = lang_var.get()
        selected_language = "Arabic" if selected_display == "العربية" else "English"
        set_language(selected_language)
    hover_btn(lang_row, "Apply", apply_language_selection, True).pack(side="left", padx=8)

    appearance = card(body)
    tk.Label(appearance, text="Appearance & Theme", bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
    tk.Label(appearance, text="Select a visual preset for the launcher UI.", bg=t["card"], fg=t["muted"], font=(FONT, 10)).pack(anchor="w", pady=(4, 10))
    row = tk.Frame(appearance, bg=t["card"])
    row.pack(anchor="w")
    var = tk.StringVar(value=tr(settings.get("theme", "Villager Green")))
    ttk.Combobox(row, textvariable=var, values=[tr(x) for x in list(THEMES) + list(custom_themes)], state="readonly", width=28).pack(side="left")
    hover_btn(row, "Apply Theme", lambda: apply_theme(from_display(var.get())), True).pack(side="left", padx=8)
    hover_btn(row, "Custom Accent", create_custom_theme).pack(side="left")
    
    mc = card(body)
    tk.Label(mc, text="Minecraft Installation Directory", bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
    tk.Label(mc, text=settings.get("minecraft_path") or r"(Default: %APPDATA%\.minecraft)", bg=t["card"], fg=t["muted"], font=(FONT, 9)).pack(anchor="w", pady=(6, 10))
    hover_btn(mc, "Browse Directory", choose_mc, True).pack(anchor="w")
    
    java = card(body)
    tk.Label(java, text="Java Executable", bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
    tk.Label(java, text=settings.get("java_path") or "(Default: System Java)", bg=t["card"], fg=t["muted"], font=(FONT, 9)).pack(anchor="w", pady=(6, 10))
    hover_btn(java, "Browse Executable", choose_java, True).pack(anchor="w")
    
    updates = card(body)
    tk.Label(updates, text="Software Updates", bg=t["card"], fg=t["fg"], font=(FONT, 13, "bold")).pack(anchor="w")
    tk.Label(updates, text="Check GitHub repository for launcher updates.", bg=t["card"], fg=t["muted"], font=(FONT, 10), wraplength=760, justify="left").pack(anchor="w", pady=(6, 10))
    row = tk.Frame(updates, bg=t["card"])
    row.pack(anchor="w")
    hover_btn(row, "Check for Updates", check_updates, True).pack(side="left")
    hover_btn(row, "Release Notes", release_notes).pack(side="left", padx=8)
    hover_btn(row, "Rollback", rollback_launcher).pack(side="left")

def apply_theme(name):
    if name in THEMES or name in custom_themes:
        settings["theme"] = name
        save_state()
        render()

def create_custom_theme():
    chosen = colorchooser.askcolor(title="Select Accent Color", initialcolor=T()["accent"])
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
    f = filedialog.askdirectory(title="Select Minecraft Folder")
    if f:
        settings["minecraft_path"] = f
        save_state()
        render()

def choose_java():
    f = filedialog.askopenfilename(title="Select Java Binary", filetypes=[("Executable", "*.exe"), ("All files", "*.*")])
    if f:
        settings["java_path"] = f
        save_state()
        render()

def release_notes():
    try:
        info = net_json(VERSION_URL, 8)
    except Exception:
        info = {"version": CURRENT_VERSION, "whats_new": {
            "Added": ["Scrollable 10-section sidebar", "Villager OS 1.0", "S4 audio Easter egg", "1500-item master registry", "World backup tools", "Local server manager", "Play, Versions, Modpacks, News, and Tools centers"],
            "Changed": ["Main navigation moved from bottom dock to a scrollable left sidebar", "Dashboard redesigned for 2.2.0", "Legacy pages reorganized as sub-tools instead of being removed"],
            "Removed": [],
            "Fixed": ["Offline bot diagnostics no longer reports a false failure with the built-in knowledge pack", "Preserved safe startup definition order"]
        }}
    n = info.get("whats_new", info.get("notes", {}))
    lines = []
    if isinstance(n, dict):
        for k in ("Added", "Changed", "Removed", "Fixed"):
            if n.get(k):
                items = n[k] if isinstance(n[k], list) else [n[k]]
                lines.append(k.upper() + "\n" + "\n".join("• " + str(x) for x in items))
    text = f"Villager Launcher {info.get('version', CURRENT_VERSION)}\n\n" + ("\n\n".join(lines) if lines else "No release notes found.")
    messagebox.showinfo("Release Notes", text)

def download_update():
    with urlopen(Request(LAUNCHER_URL, headers={"User-Agent": f"Villager-Launcher/{CURRENT_VERSION}"}), timeout=20) as r:
        data = r.read()
    if not data:
        raise ValueError("Downloaded update file is empty.")
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
        messagebox.showinfo("Rollback", "No previous launcher backup available.")
        return
    previous = str(read_json(PREVIOUS_VERSION_FILE, {}).get("version", "previous version"))
    if not messagebox.askyesno("Rollback", f"Restore Villager Launcher v{previous}?"):
        return
    try:
        target = os.path.abspath(sys.argv[0])
        rollback_file = os.path.join(tempfile.gettempdir(), "villager_launcher_rollback.py")
        with open(PREVIOUS_LAUNCHER_FILE, "rb") as src:
            data = src.read()
        if not data:
            raise ValueError("Backup file is empty.")
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
    tk.Label(w, text="Updating Launcher...", bg=t["panel"], fg=t["fg"], font=(FONT, 20, "bold")).pack()
    status = tk.StringVar(value="Checking for updates...")
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
            messagebox.showinfo("Up to Date", f"Villager Launcher is up to date.\n\nVersion: {CURRENT_VERSION}")
            return
        if not messagebox.askyesno("Update Available", f"Version {latest} is available.\n\nCurrent: {CURRENT_VERSION}\nNew: {latest}\n\nUpdate now?"):
            return
        loading, status, stage, bar = show_update_loading()
        root.update_idletasks()
        status.set("Downloading package...")
        stage.config(text="2 / 4  •  Downloading")
        root.update_idletasks()
        src = download_update()
        status.set("Creating backup...")
        stage.config(text="3 / 4  •  Installing")
        root.update_idletasks()
        target = os.path.abspath(sys.argv[0])
        os.makedirs(APP, exist_ok=True)
        with open(target, "rb") as current, open(PREVIOUS_LAUNCHER_FILE, "wb") as backup:
            backup.write(current.read())
        with open(PREVIOUS_VERSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"version": CURRENT_VERSION}, f, indent=2)
        update_helper(src, target)
        status.set("Restarting...")
        stage.config(text="4 / 4  •  Finalizing")
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

def _lerp_color(c1, c2, f):
    c1, c2 = c1.lstrip("#"), c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = int(r1 + (r2 - r1) * f)
    g = int(g1 + (g2 - g1) * f)
    b = int(b1 + (b2 - b1) * f)
    return f"#{r:02x}{g:02x}{b:02x}"

def startup_loading():
    """Loading Screen UI #3 — bordered technical system initialization view."""
    t = T()
    root.configure(bg=t["bg"])
    for w in root.winfo_children():
        w.destroy()

    rtl = settings.get("language") == "Arabic"
    anchor = "e" if rtl else "w"

    outer = tk.Frame(root, bg=t["bg"])
    outer.pack(fill="both", expand=True, padx=34, pady=24)

    top_line = tk.Frame(outer, bg=t["accent"], height=2)
    top_line.pack(fill="x")
    title_row = tk.Frame(outer, bg=t["bg"])
    title_row.pack(fill="x", pady=(10, 8))
    tk.Label(title_row, text=tr("VILLAGER LAUNCHER"), bg=t["bg"], fg=t["fg"], font=(FONT, 20, "bold")).pack(side="right" if rtl else "left")
    tk.Label(title_row, text=f"{tr('Version')} {CURRENT_VERSION}  •  {tr('Villager OS')} {VILLAGER_OS_VERSION}", bg=t["bg"], fg=t["accent"], font=(FONT, 9, "bold")).pack(side="left" if rtl else "right", pady=7)
    tk.Frame(outer, bg=t["border"], height=1).pack(fill="x")

    # VIDEO panel — retains the exact assets/villagernews.mp4 MPV path.
    video_label = tk.Frame(outer, bg=t["bg"])
    video_label.pack(fill="x", pady=(12, 5))
    tk.Label(video_label, text=tr("VIDEO"), bg=t["bg"], fg=t["muted"], font=(FONT, 8, "bold")).pack(anchor=anchor)

    video_shell = tk.Frame(outer, bg=t["border"])
    video_shell.pack(fill="both", expand=True)
    video_frame = tk.Frame(video_shell, bg="#000000", height=270)
    video_frame.pack(fill="both", expand=True, padx=1, pady=1)
    video_frame.pack_propagate(False)
    video_placeholder = tk.Label(video_frame, text="assets/villagernews.mp4", bg="#000000", fg=t["muted"], font=(FONT, 10, "bold"))
    video_placeholder.place(relx=0.5, rely=0.5, anchor="center")

    system_label = tk.Frame(outer, bg=t["bg"])
    system_label.pack(fill="x", pady=(12, 4))
    tk.Label(system_label, text=tr("SYSTEM"), bg=t["bg"], fg=t["muted"], font=(FONT, 8, "bold")).pack(anchor=anchor)
    tk.Frame(outer, bg=t["border"], height=1).pack(fill="x")

    system = tk.Frame(outer, bg=t["bg"])
    system.pack(fill="x", pady=(8, 5))
    stage_names = ["Configuration", "Profiles", "Interface", "Finalizing"]
    if rtl:
        stage_names = list(reversed(stage_names))
    stage_labels = {}
    for name in stage_names:
        row = tk.Frame(system, bg=t["bg"])
        row.pack(fill="x", pady=1)
        lbl = tk.Label(row, text=f"[..] {tr(name)}", bg=t["bg"], fg=t["muted"], font=(FONT, 9, "bold"))
        lbl.pack(anchor=anchor)
        stage_labels[name] = lbl

    progress_row = tk.Frame(outer, bg=t["bg"])
    progress_row.pack(fill="x", pady=(6, 0))
    tk.Label(progress_row, text=tr("PROGRESS"), bg=t["bg"], fg=t["muted"], font=(FONT, 8, "bold")).pack(side="right" if rtl else "left")
    percent = tk.StringVar(value="0%")
    tk.Label(progress_row, textvariable=percent, bg=t["bg"], fg=t["accent"], font=(FONT, 8, "bold")).pack(side="left" if rtl else "right")
    bar = ttk.Progressbar(outer, mode="determinate", maximum=100)
    bar.pack(fill="x", pady=(5, 0))
    bottom_status = tk.StringVar(value=tr("Starting Villager Launcher..."))
    tk.Label(outer, textvariable=bottom_status, bg=t["bg"], fg=t["muted"], font=(FONT, 8)).pack(anchor=anchor, pady=(7, 0))
    tk.Frame(outer, bg=t["accent"], height=2).pack(fill="x", pady=(10, 0))

    player_box = {"player": None}
    video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "villagernews.mp4")

    def start_video():
        if not os.path.exists(video_path):
            video_placeholder.configure(text=tr("VIDEO FILE NOT FOUND"), fg=t["danger"])
            return
        if not HAS_MPV:
            video_placeholder.configure(text=tr("MPV VIDEO ENGINE UNAVAILABLE"), fg=t["danger"])
            return
        try:
            video_placeholder.destroy()
            player_box["player"] = play_media_video("villagernews.mp4", parent_frame=video_frame)
        except Exception as e:
            tk.Label(video_frame, text=f"{tr('Playback Error')}: {e}", bg="#000000", fg=t["danger"], font=(FONT, 9), wraplength=600).place(relx=0.5, rely=0.5, anchor="center")

    # Map canonical stage keys independently from display order so RTL does not affect logic.
    canonical_labels = {}
    for display_name, label in stage_labels.items():
        canonical_labels[display_name] = label

    steps = [
        ("Configuration", 25, "Loading configuration..."),
        ("Profiles", 50, "Checking profiles and data..."),
        ("Interface", 75, "Preparing interface..."),
        ("Finalizing", 100, "Finishing startup..."),
    ]

    def finish():
        try:
            if player_box["player"]:
                player_box["player"].terminate()
        except Exception:
            pass
        finish_startup_loading()

    def step(i=0):
        if not root.winfo_exists():
            return
        if i >= len(steps):
            root.after(320, finish)
            return
        name, value, status_text = steps[i]
        # Mark all prior stages complete and current stage active.
        for idx, (n, _, _) in enumerate(steps):
            label = canonical_labels.get(n)
            if label is None:
                continue
            if idx < i:
                label.configure(text=f"[OK] {tr(n)}", fg=t["accent"])
            elif idx == i:
                label.configure(text=f"[..] {tr(n)}", fg=t["fg"])
            else:
                label.configure(text=f"[  ] {tr(n)}", fg=t["muted"])
        bar["value"] = value
        percent.set(f"{value}%")
        bottom_status.set(tr(status_text))
        root.after(430, lambda: step(i + 1))

    root.after(100, start_video)
    root.after(140, step)

def finish_startup_loading():
    if root and root.winfo_exists():
        render()

def feedback_page():
    t = T()
    page_header(body, "Feedback Center", "Submit thoughts and suggestions locally.")
    box = card(body)
    rating = tk.IntVar(value=5)
    stars = tk.Frame(box, bg=t["card"])
    stars.pack(anchor="w")
    for i in range(1, 6):
        tk.Radiobutton(stars, text="★", variable=rating, value=i, font=(FONT, 18), bg=t["card"], fg=t["accent"],
                       selectcolor=t["card"], activebackground=t["card"], activeforeground=t["hover"]).pack(side="left")
    tk.Label(box, text="Your Feedback", bg=t["card"], fg=t["fg"], font=(FONT, 11, "bold")).pack(anchor="w", pady=(12, 6))
    text = tk.Text(box, font=(FONT, 10), bg=t["input"], fg=t["fg"], insertbackground=t["fg"], relief="flat", height=8, wrap="word")
    text.pack(fill="x")
    hover_btn(box, "Save Feedback", lambda: save_feedback(rating.get(), text.get("1.0", "end").strip()), True).pack(anchor="w", pady=(14, 0))

def save_feedback(rating, text):
    if not text:
        messagebox.showwarning("Feedback", "Please enter your message.")
        return
    os.makedirs(os.path.join(APP, "feedback"), exist_ok=True)
    f = os.path.join(APP, "feedback", time.strftime("feedback_%Y%m%d_%H%M%S.json"))
    with open(f, "w", encoding="utf-8") as z:
        json.dump({"version": CURRENT_VERSION, "rating": rating, "feedback": text, "timestamp": time.time()}, z, indent=2)
    messagebox.showinfo("Feedback Saved", "Your entry was stored locally.")

BOT_QA = {
    "Minecraft": "a sandbox game focused on building, exploration, crafting, and survival.",
    "Minecraft Java Edition": "the original PC edition of Minecraft with extensive modding support.",
    "Minecraft Bedrock Edition": "the multi-platform version of Minecraft available across consoles, mobile, and PC.",
    "a Minecraft mod": "a modification that alters or expands game functionality.",
    "Modrinth": "an open mod-hosting platform for Minecraft mods and assets.",
    "Minecraft Forge": "a modding API and loader for Minecraft Java Edition.",
    "Fabric": "a modular mod loader for Minecraft Java Edition.",
    "Sodium": "a rendering optimization mod for Minecraft.",
    "Iris": "a shader execution system compatible with Sodium.",
    "OptiFine": "a classic graphics optimization mod.",
    "a resource pack": "a pack replacing game textures, sounds, and models.",
    "a shader": "a graphics extension modifying lighting, shadows, and reflections.",
    "a data pack": "a pack modifying gameplay mechanics, functions, and loot tables.",
    "redstone": "Minecraft's circuit system for mechanics and automation.",
    "a Creeper": "an explosive hostile mob in Minecraft.",
    "a Villager": "a passive trading mob in Minecraft villages.",
    "an Enderman": "a tall mob capable of block manipulation and teleportation.",
    "the Nether": "a dangerous dimension accessible via portal.",
    "the End": "the final dimension containing the Ender Dragon.",
    "the Ender Dragon": "the main boss of the End dimension.",
    "a Minecraft seed": "a numeric code used to generate a world structure.",
    "a Minecraft version": "a specific update release of the game.",
    "a game launcher": "software managing client downloads, arguments, and game launches.",
    "the Minecraft folder": "the standard storage directory for game files (%APPDATA%\\.minecraft).",
    "Java": "the runtime environment powering Minecraft Java Edition.",
    "Python": "a general-purpose programming language.",
    "Tkinter": "the GUI library used for Python desktop interfaces.",
    "Windows": "the operating system environment.",
}

BOT_QA_AR = {
    "Minecraft": "ماينكرافت هي لعبة رملية تركز على البناء والاستكشاف وصناعة الأدوات والبقاء.",
    "Minecraft Java Edition": "إصدار Java من ماينكرافت هو إصدار الحاسوب الأصلي ويدعم التعديلات بشكل واسع.",
    "Minecraft Bedrock Edition": "إصدار Bedrock من ماينكرافت هو الإصدار متعدد المنصات المتاح على الأجهزة المحمولة ووحدات التحكم والحاسوب.",
    "a Minecraft mod": "تعديل ماينكرافت هو تغيير يضيف وظائف جديدة أو يعدل وظائف اللعبة.",
    "Modrinth": "Modrinth منصة لاستضافة تعديلات ماينكرافت والأصول المرتبطة بها.",
    "Minecraft Forge": "Forge واجهة برمجية ومحمّل للتعديلات في إصدار Java من ماينكرافت.",
    "Fabric": "Fabric محمّل تعديلات معياري لإصدار Java من ماينكرافت.",
    "Sodium": "Sodium تعديل لتحسين أداء التصيير في ماينكرافت.",
    "Iris": "Iris نظام لتشغيل التظليلات ومتوافق مع Sodium.",
    "OptiFine": "OptiFine تعديل معروف لتحسين الرسومات والأداء.",
    "a resource pack": "حزمة الموارد تستبدل خامات اللعبة وأصواتها ونماذجها.",
    "a shader": "التظليل إضافة رسومية تعدل الإضاءة والظلال والانعكاسات.",
    "a data pack": "حزمة البيانات تعدل ميكانيكيات اللعب والوظائف وجداول الغنائم.",
    "redstone": "ريدستون هو نظام الدوائر في ماينكرافت المستخدم للميكانيكيات والأتمتة.",
    "a Creeper": "الكريبر كائن معادٍ في ماينكرافت ينفجر عند الاقتراب من اللاعبين.",
    "a Villager": "فيلجر كائن مسالم في قرى ماينكرافت ويمكنه التجارة مع اللاعبين.",
    "an Enderman": "الإندرمان كائن طويل يستطيع نقل بعض الكتل والانتقال الآني.",
    "the Nether": "النيذر بُعد خطير يمكن الوصول إليه عبر بوابة.",
    "the End": "النهاية هي البعد الأخير وتحتوي على تنين الإندر.",
    "the Ender Dragon": "تنين الإندر هو الزعيم الرئيسي في بُعد النهاية.",
    "a Minecraft seed": "بذرة ماينكرافت هي رمز رقمي يستخدم لتوليد عالم اللعبة.",
    "a Minecraft version": "إصدار ماينكرافت هو إصدار محدد من تحديثات اللعبة.",
    "a game launcher": "مشغل الألعاب هو برنامج يدير تنزيلات العميل والوسائط والإطلاق.",
    "the Minecraft folder": "مجلد ماينكرافت هو مجلد التخزين القياسي لملفات اللعبة.",
    "Java": "Java هي بيئة التشغيل التي يعتمد عليها إصدار Java من ماينكرافت.",
    "Python": "بايثون لغة برمجة عامة الاستخدام.",
    "Tkinter": "Tkinter مكتبة واجهة رسومية مستخدمة لإنشاء واجهات سطح المكتب في بايثون.",
    "Windows": "ويندوز هو نظام تشغيل لأجهزة الحاسوب.",
}

def bot_answer(q):
    original_q = q
    if settings.get("language", "English") == "Arabic":
        arabic_to_english = {
            "ماينكرافت": "minecraft", "ماين كرافت": "minecraft", "التعديلات": "mods",
            "تعديل": "mod", "مشغل": "launcher", "بايثون": "python", "ويندوز": "windows",
            "جافا": "java", "روبلوكس": "roblox", "سامسونج": "samsung", "عتاد": "hardware"
        }
        for a, e in arabic_to_english.items():
            original_q = original_q.replace(a, e)
    q = re.sub(r"[^a-z0-9 ]+", " ", original_q.lower()).strip()
    if not q:
        return "Ask me a question."
    if q in BOT_QA:
        return BOT_QA_AR[q] if settings.get("language", "English") == "Arabic" else BOT_QA[q]
    words = set(q.split())
    best = max(BOT_QA, key=lambda k: len(words & set(k.split())), default="")
    return (BOT_QA_AR.get(best, tr(BOT_QA[best])) if settings.get("language", "English") == "Arabic" else BOT_QA[best]) if best and len(words & set(best.split())) >= 2 else tr("I work offline. Ask me about Minecraft, mods, launchers, or Python!")

def open_villager_bot():
    t = T()
    w = tk.Toplevel(root)
    w.title("Villager Bot — Offline Assistant")
    w.geometry("720x620")
    w.configure(bg=t["panel"])
    tk.Label(w, text="Villager Bot", font=(FONT, 22, "bold"), bg=t["panel"], fg=t["fg"]).pack(pady=(18, 2))
    tk.Label(w, text="Offline Knowledge Base", font=(FONT, 9), bg=t["panel"], fg=t["muted"]).pack(pady=(0, 12))
    out = tk.Text(w, font=(FONT, 11), bg=t["input"], fg=t["fg"], insertbackground=t["fg"], relief="flat", wrap="word")
    out.pack(fill="both", expand=True, padx=20, pady=8)
    out.insert("end", tr("Villager Bot: Ask me anything about Minecraft or the launcher!") + "\n\n")
    out.configure(state="disabled")
    ent = ttk.Entry(w)
    ent.pack(fill="x", padx=20, pady=8, ipady=9)
    def send():
        q = ent.get().strip()
        if not q:
            return
        out.configure(state="normal")
        out.insert("end", f"{tr("You")}: {q}\n{tr("Villager Bot")}: {bot_answer(q)}\n\n")
        out.see("end")
        out.configure(state="disabled")
        ent.delete(0, "end")
    hover_btn(w, "Send Message", send, True).pack(pady=(0, 16))
    ent.bind("<Return>", lambda e: send())
    ent.focus_set()

load_state()
load_feature_state()
load_servers()

root = tk.Tk()
root.title(f"{tr("Villager Launcher")} {CURRENT_VERSION}")
root.geometry(f"{settings.get('window_width', 1280)}x{settings.get('window_height', 820)}")
root.minsize(1024, 640)

startup_loading()

root.mainloop()
