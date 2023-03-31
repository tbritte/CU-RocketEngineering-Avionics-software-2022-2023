using ModernUIDesign.Core;
using ModernUIDesign.MVVM.Model;

namespace ModernUIDesign.MVVM.ViewModel
{
    class MainViewModel : ObservableObject
    {

        public RelayCommand HomeViewCommand { get; set; }
        public RelayCommand TelemetryViewCommand { get; set; }

        public HomeViewModel HomeVM { get; set; }
        public TelemetryViewModel TelemetryVM { get; set; }
        public TelemetryModel TelemetryModelTM { get; set; }
        public TMData TMData { get; set; }


        private object _currentView;

        public object CurrentView
        {
            get { return _currentView; }
            set
            {
                _currentView = value;
                OnPropertyChanged();
            }
        }


        public MainViewModel()
        {

            HomeVM = new HomeViewModel();

            TelemetryModelTM = new TelemetryModel();
            TelemetryVM = new TelemetryViewModel();
            TMData = new TMData();

            CurrentView = HomeVM;

            HomeViewCommand = new RelayCommand(o =>
            {
                CurrentView = HomeVM;
            });

            TelemetryViewCommand = new RelayCommand(o =>
            {
                CurrentView = TelemetryVM;
            });

            HomeVM.SetTMModel(TelemetryModelTM, TMData);
            TelemetryVM.SetTMModel(TelemetryModelTM, TMData);

        }
    }
}
