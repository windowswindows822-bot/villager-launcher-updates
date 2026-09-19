using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Windows.Media.Core;
using Windows.Media.Playback;
using Windows.Storage;

namespace villagerlauncher.Services;

public static class SoundService
{
    private static readonly object PlayerLock = new();
    private static readonly List<MediaPlayer> ActivePlayers = new();

    private static readonly HashSet<string> SupportedExtensions =
        new(StringComparer.OrdinalIgnoreCase)
        {
            ".mp3",
            ".wav",
            ".m4a",
            ".aac",
            ".wma"
        };

    private static readonly Random Random = new();

    public static bool Enabled { get; set; } = true;
    public static double Volume { get; set; } = 0.75;

    public static string SoundsRoot =>
        Path.Combine(AppContext.BaseDirectory, "Assets", "Sounds");

    /// <summary>
    /// Finds every supported sound in a folder.
    /// Filenames do NOT matter.
    /// Subfolders are searched automatically.
    /// </summary>
    public static IReadOnlyList<string> FindSounds(
        string? relativeFolder = null,
        bool recursive = true)
    {
        var root = string.IsNullOrWhiteSpace(relativeFolder)
            ? SoundsRoot
            : Path.Combine(
                SoundsRoot,
                relativeFolder
                    .Replace('/', Path.DirectorySeparatorChar)
                    .Trim(Path.DirectorySeparatorChar));

        if (!Directory.Exists(root))
            return Array.Empty<string>();

        try
        {
            var option = recursive
                ? SearchOption.AllDirectories
                : SearchOption.TopDirectoryOnly;

            return Directory
                .EnumerateFiles(root, "*.*", option)
                .Where(path =>
                    SupportedExtensions.Contains(
                        Path.GetExtension(path)))
                .ToArray();
        }
        catch (Exception ex)
        {
            LogService.WriteException("Sound Scan", ex);
            return Array.Empty<string>();
        }
    }

    /// <summary>
    /// Plays a random sound from the requested folder.
    /// If the folder is empty, it can fall back to any NORMAL sound
    /// below Assets\Sounds. Easter sounds are excluded from fallback.
    /// </summary>
    public static async Task<bool> PlayFromFolderAsync(
        string relativeFolder,
        bool fallbackToAnyNormalSound = true,
        double? volume = null)
    {
        if (!Enabled)
            return false;

        var matches = FindSounds(relativeFolder);

        if (matches.Count == 0 && fallbackToAnyNormalSound)
        {
            matches = FindNormalSounds();
        }

        if (matches.Count == 0)
        {
            LogService.Write(
                "Sound",
                $"No supported audio files found for folder '{relativeFolder}'.");
            return false;
        }

        var picked = matches[Random.Next(matches.Count)];
        return await PlayFileAsync(picked, volume);
    }

    /// <summary>
    /// Plays any normal sound anywhere in Assets\Sounds.
    /// Easter folders are intentionally excluded here.
    /// </summary>
    public static async Task<bool> PlayAnyAsync(double? volume = null)
    {
        if (!Enabled)
            return false;

        var matches = FindNormalSounds();

        if (matches.Count == 0)
            return false;

        var picked = matches[Random.Next(matches.Count)];
        return await PlayFileAsync(picked, volume);
    }

    /// <summary>
    /// Plays a sound by exact path only when you specifically want that.
    /// This keeps compatibility with Assets\s4.mp3.
    /// </summary>
    public static async Task<bool> PlayAssetAsync(
        string assetRelativePath,
        double? volume = null)
    {
        var clean = assetRelativePath
            .Replace('/', Path.DirectorySeparatorChar)
            .TrimStart(Path.DirectorySeparatorChar);

        var fullPath = Path.Combine(
            AppContext.BaseDirectory,
            "Assets",
            clean);

        return await PlayFileAsync(fullPath, volume);
    }

    public static Task<bool> PlayUiAsync() =>
        PlayFromFolderAsync("UI");

    public static Task<bool> PlayStartupAsync() =>
        PlayFromFolderAsync("Startup");

    public static Task<bool> PlayNotificationAsync() =>
        PlayFromFolderAsync("Notifications");

    public static Task<bool> PlayMinecraftAsync() =>
        PlayFromFolderAsync("Minecraft");

    public static Task<bool> PlayVillagerAsync() =>
        PlayFromFolderAsync("Villager");

    public static Task<bool> PlayCustomAsync() =>
        PlayFromFolderAsync("Custom");

    /// <summary>
    /// Hidden-click audio. Filename does not matter.
    /// It ONLY scans Assets\Sounds\Easter\Clicks.
    /// No fallback is used so normal UI audio cannot accidentally become
    /// the hidden click sound.
    /// </summary>
    public static Task<bool> PlayEasterClickAsync() =>
        PlayFromFolderAsync(
            Path.Combine("Easter", "Clicks"),
            false);

    public static Task<bool> PlayEasterSuccessAsync() =>
        PlayFromFolderAsync(
            Path.Combine("Easter", "Success"),
            false);

    public static void StopAll()
    {
        lock (PlayerLock)
        {
            foreach (var player in ActivePlayers.ToArray())
            {
                try
                {
                    player.Pause();
                    player.Dispose();
                }
                catch
                {
                }
            }

            ActivePlayers.Clear();
        }
    }

    private static IReadOnlyList<string> FindNormalSounds()
    {
        return FindSounds()
            .Where(path =>
            {
                var relative = Path.GetRelativePath(
                    SoundsRoot,
                    path);

                return !relative.StartsWith(
                    "Easter" + Path.DirectorySeparatorChar,
                    StringComparison.OrdinalIgnoreCase);
            })
            .ToArray();
    }

    private static async Task<bool> PlayFileAsync(
        string fullPath,
        double? volume)
    {
        if (!Enabled || !File.Exists(fullPath))
            return false;

        try
        {
            var file =
                await StorageFile.GetFileFromPathAsync(fullPath);

            var player = new MediaPlayer
            {
                AutoPlay = false,
                Volume = Math.Clamp(
                    volume ?? Volume,
                    0.0,
                    1.0)
            };

            player.Source =
                MediaSource.CreateFromStorageFile(file);

            player.MediaEnded += (_, _) =>
                DisposePlayer(player);

            player.MediaFailed += (_, args) =>
            {
                LogService.Write(
                    "Sound",
                    "Media failed: " + args.ErrorMessage);

                DisposePlayer(player);
            };

            lock (PlayerLock)
            {
                ActivePlayers.Add(player);
            }

            player.Play();

            LogService.Write(
                "Sound",
                "Playing: " + Path.GetFileName(fullPath));

            return true;
        }
        catch (Exception ex)
        {
            LogService.WriteException("Sound", ex);
            return false;
        }
    }

    private static void DisposePlayer(MediaPlayer player)
    {
        lock (PlayerLock)
        {
            try
            {
                player.Dispose();
            }
            catch
            {
            }

            ActivePlayers.Remove(player);
        }
    }
}