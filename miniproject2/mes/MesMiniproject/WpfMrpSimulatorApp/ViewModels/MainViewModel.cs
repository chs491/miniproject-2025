using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WpfMrpSimulatorApp.ViewModels : ObservableObject
{
    internal class MainViewModel
    {
        private string _greeting;

    public MainViewModel()
    {
        Greeting = "MRP 공정관리!";
    }

    public string Greeting
    {
        get => _greeting;
        set => SettingsProperty(ref _greeting, value);
    }
}

