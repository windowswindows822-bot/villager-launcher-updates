
using System;
using System.Diagnostics;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace villagerlauncher.Pages;

public sealed partial class NewsPage : Page
{
    private const string CurrentVersion = "2.2.2";
    private const string VersionUrl =
        "https://raw.githubusercontent.com/windowswindows822-bot/villager-launcher-updates/main/version.json";
    private const string RepositoryUrl =
        "https://github.com/windowswindows822-bot/villager-launcher-updates";

    private readonly HttpClient _httpClient = new();

    public NewsPage()
    {
        InitializeComponent();
        _httpClient.DefaultRequestHeaders.UserAgent.ParseAdd("VillagerLauncher/2.2.2");
    }

    private void OpenGitHub_Click(object sender, RoutedEventArgs e)
    {
        Process.Start(new ProcessStartInfo
        {
            FileName = RepositoryUrl,
            UseShellExecute = true
        });
    }

    private async void CheckUpdate_Click(object sender, RoutedEventArgs e)
    {
        UpdateInfoBar.IsOpen = true;
        UpdateInfoBar.Severity = InfoBarSeverity.Informational;
        UpdateInfoBar.Title = "Checking GitHub…";
        UpdateInfoBar.Message = VersionUrl;

        try
        {
            string json = await _httpClient.GetStringAsync(
                VersionUrl + "?t=" + DateTimeOffset.UtcNow.ToUnixTimeMilliseconds());

            using JsonDocument document = JsonDocument.Parse(json);
            JsonElement root = document.RootElement;

            string latest = root.TryGetProperty("version", out JsonElement versionElement)
                ? versionElement.GetString() ?? CurrentVersion
                : CurrentVersion;

            bool newer = CompareVersions(latest, CurrentVersion) > 0;

            UpdateInfoBar.Title = newer
                ? $"Update {latest} available"
                : "Villager Launcher is up to date";

            UpdateInfoBar.Message =
                $"Current: {CurrentVersion} · GitHub: {latest}";

            UpdateInfoBar.Severity = newer
                ? InfoBarSeverity.Success
                : InfoBarSeverity.Informational;

            ReleaseNotesText.Text = ExtractNotes(root);
        }
        catch (Exception ex)
        {
            UpdateInfoBar.Severity = InfoBarSeverity.Error;
            UpdateInfoBar.Title = "GitHub check failed";
            UpdateInfoBar.Message = ex.Message;
        }
    }

    private static string ExtractNotes(JsonElement root)
    {
        if (!root.TryGetProperty("whats_new", out JsonElement notes) &&
            !root.TryGetProperty("notes", out notes))
        {
            return "No release notes were provided in version.json.";
        }

        if (notes.ValueKind == JsonValueKind.String)
            return notes.GetString() ?? "";

        if (notes.ValueKind != JsonValueKind.Object)
            return notes.ToString();

        StringBuilder builder = new();

        foreach (string sectionName in new[] { "Added", "Changed", "Fixed", "Removed" })
        {
            if (!notes.TryGetProperty(sectionName, out JsonElement section))
                continue;

            builder.AppendLine(sectionName.ToUpperInvariant());

            if (section.ValueKind == JsonValueKind.Array)
            {
                foreach (JsonElement item in section.EnumerateArray())
                    builder.AppendLine("• " + item.ToString());
            }
            else
            {
                builder.AppendLine("• " + section.ToString());
            }

            builder.AppendLine();
        }

        return builder.ToString().Trim();
    }

    private static int CompareVersions(string left, string right)
    {
        static Version Parse(string text)
        {
            string clean = text.Trim().TrimStart('v', 'V').Split('-')[0];
            return Version.TryParse(clean, out Version? parsed)
                ? parsed
                : new Version(0, 0, 0);
        }

        return Parse(left).CompareTo(Parse(right));
    }
}
