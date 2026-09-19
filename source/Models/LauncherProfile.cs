
using System.Text.Json.Serialization;

namespace villagerlauncher.Models;

public sealed class LauncherProfile
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = "Default";

    [JsonPropertyName("version")]
    public string Version { get; set; } = "";

    [JsonPropertyName("loader")]
    public string Loader { get; set; } = "Vanilla";

    public override string ToString() => Name;
}
