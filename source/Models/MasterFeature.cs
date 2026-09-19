namespace villagerlauncher.Models;

public sealed class MasterFeature
{
    public int Id { get; set; }
    public int SourceNumber { get; set; }
    public string Title { get; set; } = "";
    public string Category { get; set; } = "";
    public int Batch { get; set; }
    public bool IsHidden { get; set; }

    public string MasterIdLabel => $"#{Id:0000}";
    public string SourceNumberLabel => $"Source {SourceNumber}";
    public string BatchLabel => $"Batch {Batch}";
}
