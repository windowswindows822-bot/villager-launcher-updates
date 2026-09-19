
using System;
using System.IO;
using System.Text;
using System.Text.RegularExpressions;

namespace villagerlauncher.Services;

public static class LogService
{
    private static readonly object Sync = new();

    public static string CurrentLogFile
    {
        get
        {
            LauncherPaths.EnsureDirectories();
            return Path.Combine(
                LauncherPaths.LogsDirectory,
                $"villager-{DateTime.Now:yyyy-MM-dd}.log");
        }
    }

    public static void Write(string subsystem, string message)
    {
        try
        {
            var safe = Redact(message);
            var line =
                $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] [{subsystem}] {safe}{Environment.NewLine}";

            lock (Sync)
            {
                File.AppendAllText(CurrentLogFile, line, Encoding.UTF8);
            }
        }
        catch
        {
            // Logging must never crash the launcher.
        }
    }

    public static void WriteException(string subsystem, Exception ex)
    {
        Write(subsystem, $"{ex.GetType().Name}: {ex.Message}\n{ex.StackTrace}");
    }

    public static string Redact(string text)
    {
        if (string.IsNullOrEmpty(text))
            return text;

        text = Regex.Replace(
            text,
            @"(?i)(password|passwd|token|api[_-]?key|authorization)\s*[:=]\s*([^\s,;]+)",
            "$1=[REDACTED]");

        text = Regex.Replace(
            text,
            @"(?i)bearer\s+[A-Za-z0-9\-\._~\+\/]+=*",
            "Bearer [REDACTED]");

        return text;
    }

    public static string ExportCopy()
    {
        LauncherPaths.EnsureDirectories();
        var desktop = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
        var output = Path.Combine(
            desktop,
            $"VillagerLauncher_Log_{DateTime.Now:yyyyMMdd_HHmmss}.txt");

        if (File.Exists(CurrentLogFile))
            File.Copy(CurrentLogFile, output, true);
        else
            File.WriteAllText(output, "No launcher log entries have been recorded yet.", Encoding.UTF8);

        return output;
    }
}
