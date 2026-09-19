using System;
using System.Diagnostics;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using villagerlauncher.Pages;

namespace villagerlauncher
{
    public sealed partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();

            try
            {
                string iconPath = System.IO.Path.Combine(
                    AppContext.BaseDirectory,
                    "Assets",
                    "VillagerLauncher.ico");

                if (System.IO.File.Exists(iconPath))
                    AppWindow.SetIcon(iconPath);
            }
            catch
            {
                // Icon failure must never stop launcher startup.
            }

            // Attach after XAML initialization so ContentFrame cannot be null.
            NavView.SelectionChanged += NavView_SelectionChanged;

            ContentFrame.Navigate(typeof(HomePage));
            NavView.SelectedItem = HomeNavItem;
        }

        private void NavView_SelectionChanged(
            NavigationView sender,
            NavigationViewSelectionChangedEventArgs args)
        {
            if (ContentFrame is null)
                return;

            if (args.SelectedItemContainer?.Tag is not string tag)
                return;

            Type pageType = tag switch
            {
                "Home" => typeof(HomePage),
                "Play" => typeof(PlayPage),
                "Profiles" => typeof(ProfilesPage),
                "Versions" => typeof(VersionsPage),
                "Mods" => typeof(ModsPage),
                "Modpacks" => typeof(ModpacksPage),
                "Worlds" => typeof(WorldsPage),
                "Servers" => typeof(ServersPage),
                "News" => typeof(NewsPage),
                "Tools" => typeof(ToolsPage),
                "Settings" => typeof(SettingsPage),
                "Features223" => typeof(Features223Page),
                "MasterFeatures" => typeof(MasterFeaturesPage),                "Themes223" => typeof(ThemeGalleryPage),
                _ => typeof(HomePage)
            };

            Navigate(pageType);
        }

        private void Navigate(Type pageType)
        {
            if (ContentFrame is null)
                return;

            if (ContentFrame.CurrentSourcePageType != pageType)
                ContentFrame.Navigate(pageType);
        }

        private void CheckUpdates_Click(object sender, RoutedEventArgs e)
        {
            Navigate(typeof(NewsPage));
            SelectNavigationItem("News");
        }

        private void OpenSettings_Click(object sender, RoutedEventArgs e)
        {
            Navigate(typeof(SettingsPage));
            SelectNavigationItem("Settings");
        }

        private void OpenTools_Click(object sender, RoutedEventArgs e)
        {
            Navigate(typeof(ToolsPage));
            SelectNavigationItem("Tools");
        }

        private void RefreshSidePanel_Click(object sender, RoutedEventArgs e)
        {
            // Visual refresh placeholder; actual status services can be connected here.
        }

        private void GitHub_Click(object sender, RoutedEventArgs e)
        {
            Process.Start(new ProcessStartInfo
            {
                FileName = "https://github.com/windowswindows822-bot/villager-launcher-updates",
                UseShellExecute = true
            });
        }

        private void SelectNavigationItem(string tag)
        {
            foreach (object item in NavView.MenuItems)
            {
                if (item is NavigationViewItem navItem &&
                    navItem.Tag is string itemTag &&
                    string.Equals(itemTag, tag, StringComparison.Ordinal))
                {
                    NavView.SelectedItem = navItem;
                    return;
                }
            }

            foreach (object item in NavView.FooterMenuItems)
            {
                if (item is NavigationViewItem navItem &&
                    navItem.Tag is string itemTag &&
                    string.Equals(itemTag, tag, StringComparison.Ordinal))
                {
                    NavView.SelectedItem = navItem;
                    return;
                }
            }
        }
    }
}