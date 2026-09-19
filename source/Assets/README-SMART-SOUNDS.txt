VILLAGER LAUNCHER - SMART SOUNDS

YOU DO NOT NEED SPECIAL FILENAMES.

SUPPORTED AUDIO:
.mp3
.wav
.m4a
.aac
.wma

EXAMPLES

Drop:
Assets\Sounds\UI\anything.mp3

or:
Assets\Sounds\UI\banana.wav

or:
Assets\Sounds\UI\button_sound_884.m4a

All are valid. The launcher scans the folder and randomly picks a supported file.

FOLDERS

Assets\Sounds\UI
- Automatically used for normal Button clicks.

Assets\Sounds\Startup
- Automatically used when the launcher startup sequence begins.

Assets\Sounds\Notifications
- For update/success/error notification sounds.

Assets\Sounds\Minecraft
- For Minecraft launch-related sounds.

Assets\Sounds\Villager
- For Villager/Hrmm sounds.

Assets\Sounds\Custom
- General custom sounds.

Assets\Sounds\Easter\Clicks
- Automatically used when the hidden Settings entry is clicked.
- Filename does not matter.

Assets\Sounds\Easter\Success
- Optional extra sound used when the hidden click sequence completes.

Assets\s4.mp3
- Preserved as the fifth-click payoff.
- It stays at this exact path for compatibility.

AUTOMATIC FALLBACK

If a normal sound category is empty, SoundService can scan the other NORMAL
sound folders and pick an available sound automatically.

Easter sounds are intentionally excluded from normal fallback so the launcher
does not accidentally reveal hidden sounds during ordinary button clicks.

WHY THESE OTHER ASSET FOLDERS EXIST

Assets\Videos
- Startup videos such as villagernews.mp4 or future UI video.

Assets\Images
- General pictures used by the launcher.

Assets\Backgrounds
- Wallpaper/background art for pages.

Assets\Icons
- Custom launcher/page/button icons.

Assets\Fonts
- Optional custom Arabic/English fonts if you ever want them.

Assets\Music was REMOVED.
The removed folder is backed up outside the project instead of deleting files.

NOTE:
The name "Music" was only a technical asset category; it was not connected
to the USA or any country. It is removed here because you do not want a
music system in Villager Launcher.