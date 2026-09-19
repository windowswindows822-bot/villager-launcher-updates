
using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.UI.Xaml.Controls;
using villagerlauncher.Data;
using villagerlauncher.Models;

namespace villagerlauncher.Pages;

public sealed partial class IdeasPage : Page
{
    private readonly IReadOnlyList<DesignIdea> _allIdeas = DesignIdeaCatalog.All;

    public IdeasPage()
    {
        InitializeComponent();

        var categories = new List<string> { "All categories" };
        categories.AddRange(
            _allIdeas
                .Select(idea => idea.Category)
                .Distinct()
                .OrderBy(category => category));

        CategoryCombo.ItemsSource = categories;
        CategoryCombo.SelectedIndex = 0;

        ApplyFilter();
    }

    private void SearchBox_TextChanged(
        object sender,
        TextChangedEventArgs e)
    {
        ApplyFilter();
    }

    private void CategoryCombo_SelectionChanged(
        object sender,
        SelectionChangedEventArgs e)
    {
        ApplyFilter();
    }

    private void ApplyFilter()
    {
        string search = SearchBox?.Text?.Trim() ?? "";
        string category = CategoryCombo?.SelectedItem as string ?? "All categories";

        IEnumerable<DesignIdea> filtered = _allIdeas;

        if (!string.Equals(category, "All categories", StringComparison.Ordinal))
        {
            filtered = filtered.Where(
                idea => string.Equals(
                    idea.Category,
                    category,
                    StringComparison.Ordinal));
        }

        if (!string.IsNullOrWhiteSpace(search))
        {
            filtered = filtered.Where(
                idea =>
                    idea.Title.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                    idea.Description.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                    idea.Category.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                    idea.NumberText.Contains(search, StringComparison.OrdinalIgnoreCase));
        }

        List<DesignIdea> result = filtered.ToList();

        IdeasList.ItemsSource = result;
        IdeaCountText.Text = $"{result.Count} idea{(result.Count == 1 ? "" : "s")}";
    }
}
