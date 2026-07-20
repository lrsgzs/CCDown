using Avalonia.Media;
using ClassIsland;

namespace CCDown;

public static class GlobalConstants
{
    public static string Tag => GitInfo.Tag;
    public static string Branch => GitInfo.Branch;
    public static string CommitHash => GitInfo.CommitHash[..7];
    public static string FullCommitHash => GitInfo.CommitHash;

    public static string CodeName => "NullPtr";
    public static string Version => Tag;
    public static string DisplayVersion => $"{Version} (Codename {CodeName})";
    public static string VersionLong => $"{Version}-{CodeName}-{CommitHash}({Branch})";

#if DEBUG
    public static bool IsDevelopment => true;
#else
    public static bool IsDevelopment => false;
#endif

    public static FontFamily FluentIconsFontFamily { get; } =
        new("avares://FileHelper4Desktop/Assets/Fonts/#FluentSystemIcons-Resizable");
}