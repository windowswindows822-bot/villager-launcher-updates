
using System.Text.Json.Serialization;

namespace villagerlauncher.Models;

public sealed class LauncherSettings
{
    [JsonPropertyName("language")]
    public string Language { get; set; } = "English";

    [JsonPropertyName("minecraft_path")]
    public string MinecraftPath { get; set; } = "";

    [JsonPropertyName("java_path")]
    public string JavaPath { get; set; } = "";

    [JsonPropertyName("village_name")]
    public string VillageName { get; set; } = "My Village";

    [JsonPropertyName("theme")]
    public string Theme { get; set; } = "System";
}
