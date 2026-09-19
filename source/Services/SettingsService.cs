
using System;
using System.IO;
using System.Text.Json;
using villagerlauncher.Models;

namespace villagerlauncher.Services;

public sealed class SettingsService
{
    private static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = true,
        PropertyNameCaseInsensitive = true
    };

    public LauncherSettings Current { get; private set; } = new();

    public void Load()
    {
        LauncherPaths.EnsureDirectories();

        if (!File.Exists(LauncherPaths.SettingsFile))
        {
            Save();
            return;
        }

        try
        {
            var json = File.ReadAllText(LauncherPaths.SettingsFile);
            Current = JsonSerializer.Deserialize<LauncherSettings>(json, Options)
                      ?? new LauncherSettings();
        }
        catch (Exception ex)
        {
            LogService.WriteException("Settings", ex);
            BackupBrokenFile(LauncherPaths.SettingsFile);
            Current = new LauncherSettings();
            Save();
        }
    }

    public void Save()
    {
        LauncherPaths.EnsureDirectories();
        var json = JsonSerializer.Serialize(Current, Options);
        File.WriteAllText(LauncherPaths.SettingsFile, json);
        LogService.Write("Settings", "Settings saved.");
    }

    private static void BackupBrokenFile(string path)
    {
        try
        {
            if (!File.Exists(path))
                return;

            var backup = Path.Combine(
                LauncherPaths.BackupsDirectory,
                $"broken_settings_{DateTime.Now:yyyyMMdd_HHmmss}.json");

            File.Copy(path, backup, true);
        }
        catch
        {
        }
    }
}
