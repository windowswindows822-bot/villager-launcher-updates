using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using villagerlauncher.Data;
using villagerlauncher.Models;

namespace villagerlauncher.Pages;

public sealed partial class Features223Page : Page
{
    private readonly IReadOnlyList<Feature223> _allFeatures =
        FeatureRegistry223.All;

    public Features223Page()
    {
        InitializeComponent();

        TotalCountText.Text =
            $"{FeatureRegistry223.RequiredFeatureCount} required";

        var categories = new List<string>
        {
            "All categories"
        };

        categories.AddRange(
            _allFeatures
                .Select(feature => feature.Category)
                .Distinct()
                .OrderBy(category => category));

        CategoryCombo.ItemsSource = categories;
        CategoryCombo.SelectedIndex = 0;

        StatusCombo.ItemsSource = new[]
        {
            "All statuses",
            "Queued",
            "In Progress",
            "Implemented",
            "Needs Review"
        };
        StatusCombo.SelectedIndex = 0;

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

    private void StatusCombo_SelectionChanged(
        object sender,
        SelectionChangedEventArgs e)
        => ApplyFilter();

    private void FeatureList_SelectionChanged(
        object sender,
        SelectionChangedEventArgs e)
    {
        if (FeatureList.SelectedItem is not Feature223 feature)
        {
            DetailIdText.Text = "";
            DetailTitleText.Text = "Select a feature";
            DetailCategoryText.Text = "";
            return;
        }

        DetailIdText.Text =
            $"{feature.IdText} · {feature.RequiredText} · {feature.Status}";

        DetailTitleText.Text = feature.Title;
        DetailCategoryText.Text = feature.Category;
    }

    private void RandomFeature_Click(
        object sender,
        RoutedEventArgs e)
    {
        if (FeatureList.Items.Count == 0)
            return;

        int index = Random.Shared.Next(FeatureList.Items.Count);

        FeatureList.SelectedIndex = index;
        FeatureList.ScrollIntoView(FeatureList.SelectedItem);
    }

    private void ClearFilters_Click(
        object sender,
        RoutedEventArgs e)
    {
        SearchBox.Text = "";
        CategoryCombo.SelectedIndex = 0;
        StatusCombo.SelectedIndex = 0;
        ApplyFilter();
    }

    private void ApplyFilter()
    {
        string search =
            SearchBox?.Text?.Trim() ?? "";

        string category =
            CategoryCombo?.SelectedItem as string ??
            "All categories";

        string status =
            StatusCombo?.SelectedItem as string ??
            "All statuses";

        IEnumerable<Feature223> result =
            _allFeatures;

        if (!string.Equals(
                category,
                "All categories",
                StringComparison.Ordinal))
        {
            result = result.Where(
                feature =>
                    string.Equals(
                        feature.Category,
                        category,
                        StringComparison.Ordinal));
        }

        if (!string.Equals(
                status,
                "All statuses",
                StringComparison.Ordinal))
        {
            result = result.Where(
                feature =>
                    string.Equals(
                        feature.Status,
                        status,
                        StringComparison.Ordinal));
        }

        if (!string.IsNullOrWhiteSpace(search))
        {
            result = result.Where(
                feature =>
                    feature.Title.Contains(
                        search,
                        StringComparison.OrdinalIgnoreCase) ||
                    feature.Category.Contains(
                        search,
                        StringComparison.OrdinalIgnoreCase) ||
                    feature.IdText.Contains(
                        search,
                        StringComparison.OrdinalIgnoreCase));
        }

        List<Feature223> visible =
            result.ToList();

        FeatureList.ItemsSource = visible;

        VisibleCountText.Text =
            $"{visible.Count} visible";

        if (visible.Count > 0 &&
            FeatureList.SelectedItem is null)
        {
            FeatureList.SelectedIndex = 0;
        }
    }
}
