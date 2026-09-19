
using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using villagerlauncher.Models;

namespace villagerlauncher.Services;

public sealed class ProfileService
{
    private static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = true,
        PropertyNameCaseInsensitive = true
    };

    public List<LauncherProfile> Profiles { get; private set; } = new();

    public LauncherProfile Selected =>
        Profiles.Count == 0 ? new LauncherProfile() : Profiles[0];

    public void Load()
    {
        LauncherPaths.EnsureDirectories();

        try
        {
            if (File.Exists(LauncherPaths.ProfilesFile))
            {
                var json = File.ReadAllText(LauncherPaths.ProfilesFile);
                Profiles = JsonSerializer.Deserialize<List<LauncherProfile>>(json, Options)
                           ?? new List<LauncherProfile>();
            }
        }
        catch (Exception ex)
        {
            LogService.WriteException("Profiles", ex);
            Profiles = new List<LauncherProfile>();
        }

        if (Profiles.Count == 0)
        {
            Profiles.Add(new LauncherProfile());
            Save();
        }
    }

    public void Save()
    {
        var json = JsonSerializer.Serialize(Profiles, Options);
        File.WriteAllText(LauncherPaths.ProfilesFile, json);
        LogService.Write("Profiles", $"Saved {Profiles.Count} profile(s).");
    }

    public LauncherProfile AddProfile()
    {
        var profile = new LauncherProfile
        {
            Name = $"Profile {Profiles.Count + 1}"
        };

        Profiles.Add(profile);
        Save();
        return profile;
    }
}
