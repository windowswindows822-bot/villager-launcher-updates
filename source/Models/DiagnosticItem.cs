
namespace villagerlauncher.Models;

public sealed class DiagnosticItem
{
    public string Subsystem { get; set; } = "";
    public string Status { get; set; } = "";
    public string Details { get; set; } = "";

    public override string ToString() => $"[{Status}] {Subsystem} — {Details}";
}
