namespace villagerlauncher.Models;

public sealed class Theme223
{
    public int Id { get; }
    public string Name { get; }
    public string Category { get; }
    public string BackgroundHex { get; }
    public string ForegroundHex { get; }
    public string AccentHex { get; }
    public bool IsGlass { get; }

    public Theme223(
        int id,
        string name,
        string category,
        string backgroundHex,
        string foregroundHex,
        string accentHex,
        bool isGlass)
    {
        Id = id;
        Name = name;
        Category = category;
        BackgroundHex = backgroundHex;
        ForegroundHex = foregroundHex;
        AccentHex = accentHex;
        IsGlass = isGlass;
    }

    public string IdText => $"#{Id:000}";
    public string GlassText => IsGlass ? "Glass" : "Solid";
}
