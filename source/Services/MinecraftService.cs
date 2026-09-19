
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace villagerlauncher.Services;

public static class MinecraftService
{
    public static string MinecraftDirectory
    {
        get
        {
            var custom = AppServices.Settings.Current.MinecraftPath;
            return !string.IsNullOrWhiteSpace(custom)
                ? custom
                : LauncherPaths.DefaultMinecraftDirectory;
        }
    }

    public static IReadOnlyList<string> Versions()
    {
        var path = Path.Combine(MinecraftDirectory, "versions");

        if (!Directory.Exists(path))
            return Array.Empty<string>();

        try
        {
            return Directory.GetDirectories(path)
                .Select(Path.GetFileName)
                .Where(x => !string.IsNullOrWhiteSpace(x))
                .OrderByDescending(x => x, StringComparer.OrdinalIgnoreCase)
                .ToList()!;
        }
        catch
        {
            return Array.Empty<string>();
        }
    }

    public static IReadOnlyList<string> Mods()
    {
        var path = Path.Combine(MinecraftDirectory, "mods");

        if (!Directory.Exists(path))
            return Array.Empty<string>();

        try
        {
            return Directory.GetFiles(path, "*.jar")
                .Select(Path.GetFileName)
                .Where(x => !string.IsNullOrWhiteSpace(x))
                .OrderBy(x => x, StringComparer.OrdinalIgnoreCase)
                .ToList()!;
        }
        catch
        {
            return Array.Empty<string>();
        }
    }

    public static IReadOnlyList<string> Worlds()
    {
        var path = Path.Combine(MinecraftDirectory, "saves");

        if (!Directory.Exists(path))
            return Array.Empty<string>();

        try
        {
            return Directory.GetDirectories(path)
                .Select(Path.GetFileName)
                .Where(x => !string.IsNullOrWhiteSpace(x))
                .OrderBy(x => x, StringComparer.OrdinalIgnoreCase)
                .ToList()!;
        }
        catch
        {
            return Array.Empty<string>();
        }
    }

    public static bool JavaWorks(out string details)
    {
        var java = AppServices.Settings.Current.JavaPath;

        if (string.IsNullOrWhiteSpace(java))
            java = "java";

        try
        {
            using var process = Process.Start(new ProcessStartInfo
            {
                FileName = java,
                Arguments = "-version",
                UseShellExecute = false,
                RedirectStandardError = true,
                RedirectStandardOutput = true,
                CreateNoWindow = true
            });

            if (process == null)
            {
                details = "Java process could not start.";
                return false;
            }

            process.WaitForExit(5000);
            details = process.StandardError.ReadToEnd();
            if (string.IsNullOrWhiteSpace(details))
                details = process.StandardOutput.ReadToEnd();

            return process.ExitCode == 0;
        }
        catch (Exception ex)
        {
            details = ex.Message;
            return false;
        }
    }

    public static string ValidateLaunch(string version)
    {
        if (!Directory.Exists(MinecraftDirectory))
            return "Minecraft directory was not found.";

        if (string.IsNullOrWhiteSpace(version))
            return "No Minecraft version is selected.";

        var versionDir = Path.Combine(MinecraftDirectory, "versions", version);
        var json = Path.Combine(versionDir, version + ".json");
        var jar = Path.Combine(versionDir, version + ".jar");

        if (!File.Exists(json))
            return $"Missing version metadata: {json}";

        if (!File.Exists(jar))
            return $"Missing Minecraft JAR: {jar}";

        if (!JavaWorks(out var java))
            return "Java validation failed: " + java;

        return "Validation passed. Minecraft files and Java are ready for the launch pipeline.";
    }

    public static void OpenFolder(string path)
    {
        try
        {
            Directory.CreateDirectory(path);
            Process.Start(new ProcessStartInfo
            {
                FileName = path,
                UseShellExecute = true
            });
        }
        catch (Exception ex)
        {
            LogService.WriteException("File Manager", ex);
        }
    }

    public static int CountFiles(string folder, string pattern = "*")
    {
        var path = Path.Combine(MinecraftDirectory, folder);
        try
        {
            return Directory.Exists(path)
                ? Directory.GetFiles(path, pattern).Length
                : 0;
        }
        catch
        {
            return 0;
        }
    }
}
