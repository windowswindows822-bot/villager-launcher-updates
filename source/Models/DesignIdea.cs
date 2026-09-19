
namespace villagerlauncher.Models;

public sealed class DesignIdea
{
    public int Number { get; }
    public string Category { get; }
    public string Title { get; }
    public string Description { get; }

    public DesignIdea(int number, string category, string title, string description)
    {
        Number = number;
        Category = category;
        Title = title;
        Description = description;
    }

    public string NumberText => $"#{Number:000}";
}
