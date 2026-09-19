
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;
using villagerlauncher.Models;

namespace villagerlauncher.Services;

public static class DiagnosticsService
{
    public static List<DiagnosticItem> Scan()
    {
        var results = new List<DiagnosticItem>();

        Add(results, "Launcher data directory",
            Directory.Exists(LauncherPaths.DataDirectory),
            LauncherPaths.DataDirectory);

        Add(results, "Settings JSON",
            ValidateJson(LauncherPaths.SettingsFile),
            LauncherPaths.SettingsFile);

        Add(results, "Profiles JSON",
            ValidateJson(LauncherPaths.ProfilesFile),
            LauncherPaths.ProfilesFile);

        Add(results, "Minecraft directory",
            Directory.Exists(MinecraftService.MinecraftDirectory),
            MinecraftService.MinecraftDirectory);

        Add(results, "Installed versions",
            MinecraftService.Versions().Count > 0,
            $"{MinecraftService.Versions().Count} detected");

        var javaOk = MinecraftService.JavaWorks(out var javaDetails);
        Add(results, "Java", javaOk, javaDetails);

        var baseDir = AppContext.BaseDirectory;

        Add(results, "Startup video",
            File.Exists(Path.Combine(baseDir, "Assets", "villagernews.mp4")),
            "Assets/villagernews.mp4");


        Add(results, "GitHub updater URL",
            Uri.TryCreate(LauncherInfo.VersionUrl, UriKind.Absolute, out _),
            LauncherInfo.VersionUrl);

        LogService.Write("Diagnostics", $"Scan completed with {results.Count} checks.");
        return results;
    }

    public static string RepairAll()
    {
        LauncherPaths.EnsureDirectories();

        var backupDir = Path.Combine(
            LauncherPaths.BackupsDirectory,
            $"repair_{DateTime.Now:yyyyMMdd_HHmmss}");

        Directory.CreateDirectory(backupDir);

        var report = new StringBuilder();
        report.AppendLine("VILLAGER LAUNCHER REPAIR REPORT");
        report.AppendLine($"Time: {DateTime.Now:yyyy-MM-dd HH:mm:ss}");
        report.AppendLine($"Version: {LauncherInfo.CurrentVersion}");
        report.AppendLine();

        BackupIfExists(LauncherPaths.SettingsFile, backupDir);
        BackupIfExists(LauncherPaths.ProfilesFile, backupDir);
        BackupIfExists(LauncherPaths.ServersFile, backupDir);

        if (!File.Exists(LauncherPaths.SettingsFile) ||
            !ValidateJson(LauncherPaths.SettingsFile))
        {
            try
            {
                AppServices.Settings.Save();
                report.AppendLine("REPAIRED: settings.json");
            }
            catch (Exception ex)
            {
                report.AppendLine("FAILED: settings.json — " + ex.Message);
            }
        }

        if (!File.Exists(LauncherPaths.ProfilesFile) ||
            !ValidateJson(LauncherPaths.ProfilesFile))
        {
            try
            {
                if (AppServices.Profiles.Profiles.Count == 0)
                    AppServices.Profiles.AddProfile();

                AppServices.Profiles.Save();
                report.AppendLine("REPAIRED: profiles.json");
            }
            catch (Exception ex)
            {
                report.AppendLine("FAILED: profiles.json — " + ex.Message);
            }
        }

        report.AppendLine();
        report.AppendLine("No worlds, mods, profiles, resource packs, or shaders were deleted.");
        report.AppendLine($"Backup: {backupDir}");

        var output = report.ToString();
        LogService.Write("Repair", output);
        return output;
    }

    private static bool ValidateJson(string path)
    {
        if (!File.Exists(path))
            return false;

        try
        {
            using var document = JsonDocument.Parse(File.ReadAllText(path));
            return true;
        }
        catch
        {
            return false;
        }
    }

    private static void Add(
        List<DiagnosticItem> results,
        string subsystem,
        bool ok,
        string details)
    {
        results.Add(new DiagnosticItem
        {
            Subsystem = subsystem,
            Status = ok ? "PASS" : "ISSUE",
            Details = details
        });
    }

    private static void BackupIfExists(string path, string destination)
    {
        try
        {
            if (File.Exists(path))
                File.Copy(path, Path.Combine(destination, Path.GetFileName(path)), true);
        }
        catch
        {
        }
    }
}
