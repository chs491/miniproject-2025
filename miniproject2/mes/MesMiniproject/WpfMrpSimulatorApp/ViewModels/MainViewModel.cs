using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MahApps.Metro.Controls.Dialogs;
using System.Windows;

namespace WpfMrpSimulatorApp.ViewModels 
{
    public partial class MainViewModel : ObservableObject
    {
    // 다이얼로그 코디네이터 변수선언
    private readonly IDialogCoordinator dialogCoordinator;

    private string _greeting;

    public MainViewModel(IDialogCoordinator coordinator)
    {
        this.dialogCoordinator = coordinator;
        Greeting = "MRP 공정관리!";
    }

    public string Greeting
    {
        get => _greeting;
        set => SetProperty(ref _greeting, value);
    }
   

    [RelayCommand]
    public async Task AppExit()
    {
            // var result = MessageBox.Show("종료하시겠습니까?", "종료확인", MessageBoxButton.YesNo, MessageBoxImage.Question);
            var result = await this.dialogCoordinator.ShowMessageAsync(this, "종료확인", "종료하시겠습니까?", MessageDialogStyle.AffirmativeAndNegative);
        if (result == MessageDialogResult.Affirmative)
        {
            Application.Current.Shutdown();
        }
        else
        {
            return;
        }

    }
} }

