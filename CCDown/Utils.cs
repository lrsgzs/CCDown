using System.Globalization;
using System.Text;

namespace FileHelper4Desktop;

public static class Utils
{
    private static string GetPath(params string[] strings)
    {
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
        var appName = System.Reflection.Assembly.GetExecutingAssembly().GetName().Name ?? "FileHelper4Desktop";
        
        return Path.Combine([appData, appName, ..strings]);
    }

    public static string GetFilePath(params string[] strings)
    {
        var path = GetPath(strings);

        var directory = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory)) Directory.CreateDirectory(directory);

        return path;
    }

    public static string GetDirectoryPath(params string[] strings)
    {
        var path = GetPath(strings);

        if (!string.IsNullOrEmpty(path) && !Directory.Exists(path)) Directory.CreateDirectory(path);

        return path;
    }

    public static long GetTimestamp()
    {
        var timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        return timestamp;
    }
    
    public static int BitwiseNotNewDate()
    {
        var timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
        var bytes = BitConverter.GetBytes(timestamp);
        var int32 = BitConverter.ToInt32(bytes, 0);
        return ~int32;
    }
    
    public static string RandomDigits15()
    {
        var random = Random.Shared.NextDouble();
        var formatted = random.ToString("F15", CultureInfo.InvariantCulture);
        var digits = formatted.Substring(2, 15);
        return digits;
    }
    
    public static string ToQueryString(this IDictionary<string, string?> parameters)
    {
        var sb = new StringBuilder();
        foreach (var kv in parameters)
        {
            if (string.IsNullOrEmpty(kv.Value)) continue; // 跳过空值
            if (sb.Length > 0) sb.Append('&');
            sb.Append(Uri.EscapeDataString(kv.Key));
            sb.Append('=');
            sb.Append(Uri.EscapeDataString(kv.Value));
        }
        return sb.Length > 0 ? "?" + sb.ToString() : string.Empty;
    }
    
    public static string ObjectToQueryString<T>(T obj)
    {
        var properties = typeof(T).GetProperties();
        var kvPairs = new List<KeyValuePair<string, string?>>();
        foreach (var prop in properties)
        {
            var value = prop.GetValue(obj)?.ToString();
            if (!string.IsNullOrEmpty(value))
            {
                kvPairs.Add(new KeyValuePair<string, string?>(prop.Name, value));
            }
        }
        return kvPairs.ToDictionary().ToQueryString();
    }
    
    public static string FormatBytes(string bytesStr)
    {
        if (!long.TryParse(bytesStr, out var bytes))
            return bytesStr;

        string[] units = ["B", "KB", "MB", "GB"];
        double size = bytes;
        var unitIndex = 0;

        while (size >= 1024 && unitIndex < units.Length - 1)
        {
            size /= 1024;
            unitIndex++;
        }

        return $"{size:0.##}{units[unitIndex]}";
    }
}