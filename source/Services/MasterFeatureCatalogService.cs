using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using villagerlauncher.Models;

namespace villagerlauncher.Services;

public sealed class MasterFeatureSnapshot
{
    public IReadOnlyList<MasterFeature> Features { get; init; } = Array.Empty<MasterFeature>();
    public int InstalledBatchCount { get; init; }
    public int LoadedEntryCount { get; init; }
}

public static class MasterFeatureCatalogService
{
    public const int ExpectedEntryCount = 1501;

    public static MasterFeatureSnapshot Load()
    {
        var all = new List<MasterFeature>();
        var loadedBatches = new HashSet<int>();

        foreach (string directory in CandidateDirectories())
        {
            if (!Directory.Exists(directory))
                continue;

            foreach (string file in Directory
                         .EnumerateFiles(directory, "batch-*.json", SearchOption.TopDirectoryOnly)
                         .OrderBy(path => path, StringComparer.OrdinalIgnoreCase))
            {
                try
                {
                    string json = File.ReadAllText(file);

                    List<MasterFeature>? batch = JsonSerializer.Deserialize<List<MasterFeature>>(
                        json,
                        new JsonSerializerOptions
                        {
                            PropertyNameCaseInsensitive = true
                        });

                    if (batch is null)
                        continue;

                    foreach (MasterFeature feature in batch)
                    {
                        all.Add(feature);
                        loadedBatches.Add(feature.Batch);
                    }
                }
                catch
                {
                    // One bad batch must not stop the whole launcher.
                }
            }

            if (all.Count > 0)
                break;
        }

        IReadOnlyList<MasterFeature> ordered = all
            .GroupBy(feature => feature.Id)
            .Select(group => group.First())
            .OrderBy(feature => feature.Id)
            .ToList();

        return new MasterFeatureSnapshot
        {
            Features = ordered,
            InstalledBatchCount = loadedBatches.Count,
            LoadedEntryCount = ordered.Count
        };
    }

    private static IEnumerable<string> CandidateDirectories()
    {
        yield return Path.Combine(AppContext.BaseDirectory, "Data", "FeatureBatches");
        yield return Path.Combine(AppContext.BaseDirectory, "FeatureBatches");
        yield return Path.Combine(Directory.GetCurrentDirectory(), "Data", "FeatureBatches");
    }
}
