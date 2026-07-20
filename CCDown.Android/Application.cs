using Android.Runtime;
using Avalonia;
using Avalonia.Android;
using Avalonia.Media;

namespace CCDown.Android
{
    [Application]
    public class Application : AvaloniaAndroidApplication<App>
    {
        protected Application(nint javaReference, JniHandleOwnership transfer) : base(javaReference, transfer)
        {
        }

        protected override AppBuilder CustomizeAppBuilder(AppBuilder builder)
        {
            return base.CustomizeAppBuilder(builder)
                .With(new FontManagerOptions
                {
                    DefaultFamilyName = "avares://CCDown/Assets/Fonts/HarmonyOS_Sans_SC/#HarmonyOS Sans SC",
                    FontFallbacks =
                    [
                        new FontFallback
                        {
                            FontFamily =
                                new FontFamily(
                                    "avares://CCDown/Assets/Fonts/HarmonyOS_Sans_SC/#HarmonyOS Sans SC")
                        }
                    ]
                });;
        }
    }
}