using System;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace villagerlauncher.Pages;

public sealed partial class HomePage : Page
{
    public HomePage()
    {
        InitializeComponent();
    }

    private void OpenPlay_Click(object sender, RoutedEventArgs e)
        => RequestNavigation("Play");

    private void BrowseLibrary_Click(object sender, RoutedEventArgs e)
        => RequestNavigation("Versions");

    private void OpenServers_Click(object sender, RoutedEventArgs e)
        => RequestNavigation("Servers");

    private void RequestNavigation(string tag)
    {
        if (Frame?.XamlRoot?.Content is not null)
        {
            // MainWindow owns navigation; this event is intentionally lightweight.
        }

        Type? target = tag switch
        {
            "Play" => typeof(PlayPage),
            "Versions" => typeof(VersionsPage),
            "Servers" => typeof(ServersPage),
            _ => null
        };

        if (target is not null && Frame is not null)
        {
            Frame.Navigate(target);
        }
    }
}