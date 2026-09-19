
using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace villagerlauncher.Services;

public sealed class ServerService
{
    private static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = true
    };

    public List<string> Servers { get; private set; } = new();

    public void Load()
    {
        try
        {
            if (File.Exists(LauncherPaths.ServersFile))
            {
                Servers =
                    JsonSerializer.Deserialize<List<string>>(
                        File.ReadAllText(LauncherPaths.ServersFile),
                        Options)
                    ?? new List<string>();
            }
        }
        catch (Exception ex)
        {
            LogService.WriteException("Servers", ex);
            Servers = new List<string>();
        }
    }

    public void Save()
    {
        File.WriteAllText(
            LauncherPaths.ServersFile,
            JsonSerializer.Serialize(Servers, Options));
    }

    public void Add(string address)
    {
        address = address.Trim();

        if (address.Length == 0 ||
            Servers.Exists(x => string.Equals(x, address, StringComparison.OrdinalIgnoreCase)))
            return;

        Servers.Add(address);
        Save();
    }
}
