using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using villagerlauncher.Models;
using villagerlauncher.Services;

namespace villagerlauncher.Pages;

public sealed partial class MasterFeaturesPage : Page
{
    private readonly IReadOnlyList<MasterFeature> _allFeatures;
    private readonly IReadOnlyList<MasterFeature> _publicFeatures;

    public MasterFeaturesPage()
    {
        InitializeComponent();

        MasterFeatureSnapshot snapshot = MasterFeatureCatalogService.Load();
        _allFeatures = snapshot.Features;
        _publicFeatures = _allFeatures
            .Where(feature => !feature.IsHidden)
            .ToList();

        LoadedCountText.Text =
            $"{snapshot.LoadedEntryCount:N0} / {MasterFeatureCatalogService.ExpectedEntryCount:N0} loaded";

        BatchCountText.Text =
            $"{snapshot.InstalledBatchCount} / 3 data batches installed";

        InstallProgress.Value = snapshot.LoadedEntryCount;

        var categories = new List<string> { "All categories" };
        categories.AddRange(
            _publicFeatures
                .Select(feature => feature.Category)
                .Distinct()
                .OrderBy(category => category));

        CategoryCombo.ItemsSource = categories;
        CategoryCombo.SelectedIndex = 0;

        BatchCombo.ItemsSource = new[]
        {
            "All batches",
            "Batch 1",
            "Batch 2",
            "Batch 3"
        };
        BatchCombo.SelectedIndex = 0;

        ApplyFilter();
    }

    private void SearchBox_TextChanged(object sender, TextChangedEventArgs e)
        => ApplyFilter();

    private void CategoryCombo_SelectionChanged(
        object sender,
        SelectionChangedEventArgs e)
        => ApplyFilter();

    private void BatchCombo_SelectionChanged(
        object sender,
        SelectionChangedEventArgs e)
        => ApplyFilter();

    private void ClearFilters_Click(object sender, RoutedEventArgs e)
    {
        SearchBox.Text = "";
        CategoryCombo.SelectedIndex = 0;
        BatchCombo.SelectedIndex = 0;
        ApplyFilter();
    }

    private void Random_Click(object sender, RoutedEventArgs e)
    {
        if (FeatureList.Items.Count == 0)
            return;

        int index = Random.Shared.Next(FeatureList.Items.Count);
        FeatureList.SelectedIndex = index;
        FeatureList.ScrollIntoView(FeatureList.SelectedItem);
    }

    private void FeatureList_SelectionChanged(
        object sender,
        SelectionChangedEventArgs e)
    {
        if (FeatureList.SelectedItem is not MasterFeature feature)
        {
            DetailIdText.Text = "";
            DetailTitleText.Text = "Select a feature";
            DetailCategoryText.Text = "";
            return;
        }

        DetailIdText.Text =
            $"{feature.MasterIdLabel} · {feature.SourceNumberLabel} · {feature.BatchLabel}";

        DetailTitleText.Text = feature.Title;
        DetailCategoryText.Text = feature.Category;
    }

    private void ApplyFilter()
    {
        string search = SearchBox?.Text?.Trim() ?? "";
        string category = CategoryCombo?.SelectedItem as string ?? "All categories";
        string batch = BatchCombo?.SelectedItem as string ?? "All batches";

        IEnumerable<MasterFeature> result = _publicFeatures;

        if (!string.Equals(category, "All categories", StringComparison.Ordinal))
        {
            result = result.Where(
                feature => string.Equals(
                    feature.Category,
                    category,
                    StringComparison.Ordinal));
        }

        if (batch.StartsWith("Batch ", StringComparison.Ordinal) &&
            int.TryParse(batch.AsSpan(6), out int batchNumber))
        {
            result = result.Where(feature => feature.Batch == batchNumber);
        }

        if (!string.IsNullOrWhiteSpace(search))
        {
            result = result.Where(feature =>
                feature.Title.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                feature.Category.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                feature.MasterIdLabel.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                feature.SourceNumberLabel.Contains(search, StringComparison.OrdinalIgnoreCase));
        }

        List<MasterFeature> list = result.ToList();
        FeatureList.ItemsSource = list;
        ResultCountText.Text = $"{list.Count:N0} visible";

        if (list.Count > 0 && FeatureList.SelectedItem is null)
            FeatureList.SelectedIndex = 0;
    }
}
