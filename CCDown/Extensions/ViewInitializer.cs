using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Interactivity;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using CommunityToolkit.Mvvm.ComponentModel;
using CCDown.Controls;

namespace CCDown.Extensions;

public partial class ViewInitializer : AvaloniaObject
{
    public static readonly AttachedProperty<ViewState?> StateProperty =
        AvaloniaProperty.RegisterAttached<ViewInitializer, Control, ViewState?>("State");
    public static void SetState(Control obj, ViewState? value) => obj.SetValue(StateProperty, value);
    public static ViewState? GetState(Control obj) => obj.GetValue(StateProperty);
    
    public static void InitializeView(Control control)
    {
        var state = new ViewState();
        SetState(control, state);
        
        TextOptions.SetTextRenderingMode(control, TextRenderingMode.Antialias);
        RenderOptions.SetBitmapInterpolationMode(control, BitmapInterpolationMode.HighQuality);
        RenderOptions.SetEdgeMode(control, EdgeMode.Antialias);

        control.Loaded += OnLoaded;
        return;
        
        void OnLoaded(object? sender, RoutedEventArgs e)
        {
            if (state.IsAdornerAdded) return;

            var layer = AdornerLayer.GetAdornerLayer(control);
            var appToastAdorner = state.AppToastAdorner = new AppToastAdorner(control);
            layer?.Children.Add(appToastAdorner);
            AdornerLayer.SetAdornedElement(appToastAdorner, control);

            if (GlobalConstants.IsDevelopment)
            {
                var adorner = new DevelopmentBuildAdorner();
                layer?.Children.Add(adorner);
                AdornerLayer.SetAdornedElement(adorner, control);
            }

            state.IsAdornerAdded = true;
        }
    }
    
    public partial class ViewState : ObservableObject
    {
        [ObservableProperty] private bool _isAdornerAdded;
        [ObservableProperty] private AppToastAdorner? _appToastAdorner;
    }
}