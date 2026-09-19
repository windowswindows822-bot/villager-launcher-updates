
namespace villagerlauncher.Models;

public sealed class UpdateInfo
{
    public string Version { get; set; } = LauncherInfo.CurrentVersion;
    public bool Beta { get; set; }
    public string WhatsNewText { get; set; } = "";
    public string DownloadUrl { get; set; } = "";
    public string Sha256 { get; set; } = "";
    public bool IsNewer { get; set; }
}
