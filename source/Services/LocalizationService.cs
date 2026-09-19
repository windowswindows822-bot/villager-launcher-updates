
using System;
using System.Collections.Generic;
using Microsoft.UI.Xaml;

namespace villagerlauncher.Services;

public static class LocalizationService
{
    private static readonly Dictionary<string, string> Arabic = new()
    {
        ["Home"] = "الرئيسية",
        ["Play"] = "تشغيل",
        ["Versions"] = "الإصدارات",
        ["Mods"] = "التعديلات",
        ["Modpacks"] = "حزم التعديلات",
        ["Worlds"] = "العوالم",
        ["Servers"] = "الخوادم",
        ["News"] = "الأخبار",
        ["Tools"] = "الأدوات",
        ["Settings"] = "الإعدادات",
        ["Update"] = "تحديث",
        ["Check for Updates"] = "التحقق من التحديثات",
        ["Install Update"] = "تثبيت التحديث",
        ["Play Minecraft"] = "تشغيل ماينكرافت",
        ["Repair All"] = "إصلاح الكل",
        ["Refresh"] = "تحديث",
        ["Save"] = "حفظ",
        ["Open Folder"] = "فتح المجلد",
        ["Language"] = "اللغة",
        ["Village Name"] = "اسم القرية",
        ["Minecraft Directory"] = "مجلد ماينكرافت",
        ["Java Executable"] = "ملف Java التنفيذي",
        ["Current Profile"] = "الملف الشخصي الحالي",
        ["Launcher Ready"] = "المشغل جاهز",
        ["Installed Versions"] = "الإصدارات المثبتة",
        ["Installed Mods"] = "التعديلات المثبتة",
        ["Saved Worlds"] = "العوالم المحفوظة",
        ["Diagnostics"] = "التشخيص",
        ["Export Log"] = "تصدير السجل"
    };

    public static bool IsArabic =>
        string.Equals(
            AppServices.Settings.Current.Language,
            "Arabic",
            StringComparison.OrdinalIgnoreCase);

    public static FlowDirection Flow =>
        IsArabic ? FlowDirection.RightToLeft : FlowDirection.LeftToRight;

    public static string T(string english) =>
        IsArabic && Arabic.TryGetValue(english, out var translated)
            ? translated
            : english;
}
