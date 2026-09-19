
using System;
using System.IO;

namespace villagerlauncher.Services;

public static class LauncherPaths
{
    public static string DataDirectory =>
        Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "VillagerLauncher");

    public static string SettingsFile => Path.Combine(DataDirectory, "settings.json");
    public static string ProfilesFile => Path.Combine(DataDirectory, "profiles.json");
    public static string ServersFile => Path.Combine(DataDirectory, "servers.json");
    public static string LogsDirectory => Path.Combine(DataDirectory, "logs");
    public static string BackupsDirectory => Path.Combine(DataDirectory, "backups");

    public static string DefaultMinecraftDirectory =>
        Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            ".minecraft");

    public static void EnsureDirectories()
    {
        Directory.CreateDirectory(DataDirectory);
        Directory.CreateDirectory(LogsDirectory);
        Directory.CreateDirectory(BackupsDirectory);
    }
}
