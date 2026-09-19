namespace villagerlauncher.Models;

public sealed class Feature223
{
    public int Id { get; }
    public string Category { get; }
    public string Title { get; }
    public bool Required { get; }
    public string Status { get; }

    public Feature223(
        int id,
        string category,
        string title,
        bool required,
        string status)
    {
        Id = id;
        Category = category;
        Title = title;
        Required = required;
        Status = status;
    }

    public string IdText => $"#{Id:000}";
    public string RequiredText => Required ? "Required" : "Optional";
}
