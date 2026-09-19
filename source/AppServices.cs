
using villagerlauncher.Services;

namespace villagerlauncher;

public static class AppServices
{
    public static SettingsService Settings { get; } = new();
    public static ProfileService Profiles { get; } = new();
    public static ServerService Servers { get; } = new();
    public static UpdateService Updates { get; } = new();

    public static void Initialize()
    {
        LauncherPaths.EnsureDirectories();
        Settings.Load();
        Profiles.Load();
        Servers.Load();
        LogService.Write("Startup", $"Villager Launcher {LauncherInfo.CurrentVersion} initialized.");
    }
}
