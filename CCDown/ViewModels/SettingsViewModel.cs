using CommunityToolkit.Mvvm.ComponentModel;

namespace CCDown.ViewModels;

public partial class SettingsViewModel : ViewModelBase
{
    [ObservableProperty] private string _greeting = "This is Settings";
}