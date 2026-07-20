using CommunityToolkit.Mvvm.ComponentModel;

namespace CCDown.ViewModels;

public partial class HomeViewModel : ViewModelBase
{
    [ObservableProperty] private string _greeting = "Welcome to Avalonia!";
}