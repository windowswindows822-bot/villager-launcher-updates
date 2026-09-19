
using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using villagerlauncher.Models;

namespace villagerlauncher.Services;

public sealed class UpdateService
{
    private readonly HttpClient _http = new();

    public UpdateService()
    {
        _http.DefaultRequestHeaders.UserAgent.ParseAdd(
            $"Villager-Launcher/{LauncherInfo.CurrentVersion}");
    }

    public async Task<UpdateInfo> CheckAsync()
    {
        try
        {
            var url = LauncherInfo.VersionUrl +
                      "?t=" + DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();

            var json = await _http.GetStringAsync(url);
            using var document = JsonDocument.Parse(json);
            var root = document.RootElement;

            var info = new UpdateInfo
            {
                Version = root.TryGetProperty("version", out var version)
                    ? version.GetString() ?? LauncherInfo.CurrentVersion
                    : LauncherInfo.CurrentVersion,
                Beta = root.TryGetProperty("beta", out var beta) && beta.GetBoolean()
            };

            if (root.TryGetProperty("download_url", out var downloadUrl))
                info.DownloadUrl = downloadUrl.GetString() ?? "";

            if (string.IsNullOrWhiteSpace(info.DownloadUrl) &&
                root.TryGetProperty("installer_url", out var installerUrl))
            {
                info.DownloadUrl = installerUrl.GetString() ?? "";
            }

            if (root.TryGetProperty("sha256", out var sha))
                info.Sha256 = sha.GetString() ?? "";

            JsonElement notes;
            if (root.TryGetProperty("whats_new", out notes) ||
                root.TryGetProperty("notes", out notes))
            {
                info.WhatsNewText = FormatNotes(notes);
            }

            info.IsNewer = CompareVersions(info.Version, LauncherInfo.CurrentVersion) > 0;

            LogService.Write(
                "Updater",
                $"GitHub check complete. Current={LauncherInfo.CurrentVersion}, Latest={info.Version}, Newer={info.IsNewer}");

            return info;
        }
        catch (Exception ex)
        {
            LogService.WriteException("Updater", ex);
            throw;
        }
    }

    public async Task<string> StartUpdateAsync(UpdateInfo info)
    {
        if (string.IsNullOrWhiteSpace(info.DownloadUrl))
        {
            OpenRepository();
            return "No compiled download_url is present in version.json. Opened the GitHub repository instead.";
        }

        try
        {
            var uri = new Uri(info.DownloadUrl);
            var fileName = Path.GetFileName(uri.LocalPath);

            if (string.IsNullOrWhiteSpace(fileName))
                fileName = "VillagerLauncherUpdate.bin";

            var target = Path.Combine(
                Path.GetTempPath(),
                "VillagerLauncher",
                "Updates",
                fileName);

            Directory.CreateDirectory(Path.GetDirectoryName(target)!);

            var bytes = await _http.GetByteArrayAsync(uri);

            if (!string.IsNullOrWhiteSpace(info.Sha256))
            {
                using var hasher = SHA256.Create();
                var hash = Convert.ToHexString(hasher.ComputeHash(bytes));

                if (!hash.Equals(
                        info.Sha256.Replace(" ", ""),
                        StringComparison.OrdinalIgnoreCase))
                {
                    throw new InvalidDataException(
                        "The downloaded update failed SHA-256 verification.");
                }
            }

            await File.WriteAllBytesAsync(target, bytes);

            var extension = Path.GetExtension(target).ToLowerInvariant();

            if (extension is ".exe" or ".msix" or ".msixbundle" or ".appinstaller")
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = target,
                    UseShellExecute = true
                });

                return "Update package downloaded and started.";
            }

            Process.Start(new ProcessStartInfo
            {
                FileName = info.DownloadUrl,
                UseShellExecute = true
            });

            return $"Downloaded update to {target}. Opened the download URL because this package type is not directly executable.";
        }
        catch (Exception ex)
        {
            LogService.WriteException("Updater", ex);
            throw;
        }
    }

    public void OpenRepository()
    {
        Process.Start(new ProcessStartInfo
        {
            FileName = LauncherInfo.RepositoryUrl,
            UseShellExecute = true
        });
    }

    private static string FormatNotes(JsonElement notes)
    {
        if (notes.ValueKind == JsonValueKind.String)
            return notes.GetString() ?? "";

        if (notes.ValueKind != JsonValueKind.Object)
            return notes.ToString();

        var sb = new StringBuilder();

        foreach (var section in new[] { "Added", "Changed", "Removed", "Fixed" })
        {
            if (!notes.TryGetProperty(section, out var value))
                continue;

            sb.AppendLine(section.ToUpperInvariant());

            if (value.ValueKind == JsonValueKind.Array)
            {
                foreach (var item in value.EnumerateArray())
                    sb.AppendLine("• " + item.ToString());
            }
            else
            {
                sb.AppendLine("• " + value);
            }

            sb.AppendLine();
        }

        return sb.ToString().Trim();
    }

    private static int CompareVersions(string a, string b)
    {
        static Version Parse(string input)
        {
            var clean = input.TrimStart('v', 'V').Split('-')[0];
            return Version.TryParse(clean, out var v) ? v : new Version(0, 0, 0);
        }

        return Parse(a).CompareTo(Parse(b));
    }
}
