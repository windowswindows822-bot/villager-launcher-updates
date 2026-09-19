using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using villagerlauncher.Data;
using villagerlauncher.Models;

namespace villagerlauncher.Pages;

public sealed partial class ThemeGalleryPage : Page
{
    private readonly IReadOnlyList<Theme223> _themes =
        ThemeRegistry223.All;

    public ThemeGalleryPage()
    {
        InitializeComponent();

        var categories = new List<string>
        {
            "All categories"
        };

        categories.AddRange(
            _themes
                .Select(theme => theme.Category)
                .Distinct()
                .OrderBy(category => category));

        CategoryCombo.ItemsSource = categories;
        CategoryCombo.SelectedIndex = 0;

        ApplyFilter();
    }

    private void SearchBox_TextChanged(
        object sender,
        TextChangedEventArgs e)
        => ApplyFilter();

    private void CategoryCombo_SelectionChanged(
        object sender,
        SelectionChangedEventArgs e)
        => ApplyFilter();

    private void ThemeList_SelectionChanged(
        object sender,
        SelectionChangedEventArgs e)
    {
        if (ThemeList.SelectedItem is not Theme223 theme)
            return;

        ThemeNameText.Text = theme.Name;
        ThemeCategoryText.Text = theme.Category;

        PreviewCard.Background =
            new SolidColorBrush(ParseColor(theme.BackgroundHex));

        PreviewTitle.Foreground =
            new SolidColorBrush(ParseColor(theme.ForegroundHex));

        PreviewButton.Background =
            new SolidColorBrush(ParseColor(theme.AccentHex));

        ThemeModeText.Text = theme.IsGlass
            ? "Glass theme. Aero Glass and other glass variants are marked for translucent/backdrop treatment."
            : "Solid theme.";
    }

    private void ApplyPreview_Click(
        object sender,
        RoutedEventArgs e)
    {
        if (ThemeList.SelectedItem is not Theme223 theme)
            return;

        Resources["Villager223PreviewBackground"] =
            new SolidColorBrush(ParseColor(theme.BackgroundHex));

        Resources["Villager223PreviewForeground"] =
            new SolidColorBrush(ParseColor(theme.ForegroundHex));

        Resources["Villager223PreviewAccent"] =
            new SolidColorBrush(ParseColor(theme.AccentHex));
    }

    private void ApplyFilter()
    {
        string search =
            SearchBox?.Text?.Trim() ?? "";

        string category =
            CategoryCombo?.SelectedItem as string ??
            "All categories";

        IEnumerable<Theme223> result = _themes;

        if (!string.Equals(
                category,
                "All categories",
                StringComparison.Ordinal))
        {
            result = result.Where(
                theme =>
                    string.Equals(
                        theme.Category,
                        category,
                        StringComparison.Ordinal));
        }

        if (!string.IsNullOrWhiteSpace(search))
        {
            result = result.Where(
                theme =>
                    theme.Name.Contains(
                        search,
                        StringComparison.OrdinalIgnoreCase) ||
                    theme.Category.Contains(
                        search,
                        StringComparison.OrdinalIgnoreCase));
        }

        List<Theme223> visible = result.ToList();

        ThemeList.ItemsSource = visible;

        if (visible.Count > 0)
            ThemeList.SelectedIndex = 0;
    }

    private static Windows.UI.Color ParseColor(string hex)
    {
        string value = hex.TrimStart('#');

        byte r = Convert.ToByte(value.Substring(0, 2), 16);
        byte g = Convert.ToByte(value.Substring(2, 2), 16);
        byte b = Convert.ToByte(value.Substring(4, 2), 16);

        return Windows.UI.Color.FromArgb(255, r, g, b);
    }
}
