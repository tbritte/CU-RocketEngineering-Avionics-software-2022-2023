using ModernUIDesign.Core;
using ModernUIDesign.MVVM.Model;
using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Windows;

namespace ModernUIDesign.MVVM.ViewModel
{
    class HomeViewModel : ObservableObject
    {

        private TelemetryModel _TMModel;
        private TMData _tmdata;

        public TelemetryModel telemetryModel
        {
            get => _TMModel;
            set
            {
                _TMModel = value;
                OnPropertyChanged();
            }
        }


        #region QuickView

        /// <summary>
        /// The current altitude for the QV display
        /// </summary>
        public float CurrentAltitude_qv
        {
            get => _currentaltqv;
            set
            {
                _currentaltqv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Change in the altitude since last measurement for the QV display
        /// </summary>
        public float DeltaAltitude_qv
        {
            get => _deltaaltqv;
            set
            {
                _deltaaltqv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Max altitude received by the TM for the QV display
        /// </summary>
        public float ApogeeAltitude_qv
        {
            get => _apogeealtqv;
            set
            {

                _apogeealtqv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Predicted apogee as by the flight computer, for QV display
        /// </summary>
        public float PredictedApogeeAltitude_qv
        {
            get => _predictedapogeealtqv;
            set
            {
                _predictedapogeealtqv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Current X acceleration, for QV display
        /// </summary>
        public float XAcceleration_qv
        {
            get => _xaccelqv;
            set
            {

                _xaccelqv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Current Y accleration, for QV display
        /// </summary>
        public float YAcceleration_qv
        {
            get => _yaccelqv;
            set
            {
                _yaccelqv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Current Z acceleration, for QV display
        /// </summary>
        public float ZAcceleration_qv
        {
            get => _zaccelqv;
            set
            {

                _zaccelqv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Change in X acceleration since last packet, for QV display
        /// </summary>
        public float XDeltaAcceleration_qv
        {
            get => _xdeltaaccelqv;
            set
            {
                _xdeltaaccelqv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Change in Y acceleration since last packet, for QV display
        /// </summary>
        public float YDeltaAcceleration_qv
        {
            get => _ydeltaaccelqv;
            set
            {

                _ydeltaaccelqv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Change in Z acceleration since last packet, for QV display
        /// </summary>
        public float ZDeltaAcceleration_qv
        {
            get => _zdeltaaccelqv;
            set
            {
                _zdeltaaccelqv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Current Latitude, for QV display
        /// </summary>
        public float GPSLatitude_qv
        {
            get => _gpslatitude_qv;
            set
            {

                _gpslatitude_qv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Current longitude, for QV display
        /// </summary>
        public float GPSLongitude_qv
        {
            get => _gpslongitude_qv;
            set
            {
                _gpslongitude_qv = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Current altitude, for QV display
        /// </summary>
        public float GPSAltitude_qv
        {
            get => _gpsaltitude_qv;
            set
            {

                _gpsaltitude_qv = value;
                OnPropertyChanged();
            }
        }

        // I forgot what I was going to do with these, maybe for tracking, but it's fine

        public float LaunchLatitude
        {
            get => _launchlatitude;
            set
            {
                _launchlatitude = value;
                OnPropertyChanged();
            }
        }

        public float LaunchLongitude
        {
            get => _launchlongitude;
            set
            {

                _launchlongitude = value;
                OnPropertyChanged();
            }
        }

        public float LaunchAltitude
        {
            get => _launchaltitude;
            set
            {
                _launchaltitude = value;
                OnPropertyChanged();
            }
        }

        public ObservableCollection<DataPoint> AltitudeData
        {
            get { return _altitudedata; }
            set
            {
                _altitudedata = value;
                OnPropertyChanged();
            }
        }

        private float _currentaltqv, _deltaaltqv, _apogeealtqv, _predictedapogeealtqv, _xaccelqv, _yaccelqv, _zaccelqv, _xdeltaaccelqv, _ydeltaaccelqv, _zdeltaaccelqv;
        private float _gpslatitude_qv, _gpslongitude_qv, _gpsaltitude_qv, _launchlatitude, _launchlongitude, _launchaltitude;
        private ObservableCollection<DataPoint> _altitudedata;

        #endregion



        #region Control Panel

        private ObservableCollection<bool> _indicatorlights;
        private string _message;

        public ObservableCollection<bool> IndicatorLights
        {
            get => _indicatorlights;
            set
            {
                _indicatorlights = value;
                OnPropertyChanged();
            }
        }

        public string Message
        {
            get => _message;
            set
            {
                _message = value;
                OnPropertyChanged();
                SendMessageCommand.RaiseCanExecuteChanged();
            }
        }

        #endregion


        public ViewCommand SendMessageCommand { get; set; }


        public HomeViewModel()
        {

            IndicatorLights = new ObservableCollection<bool>();

            // Init lights
            bool flip = false;
            for (int i = 0; i < 16; i++)
            {
                IndicatorLights.Add(flip);
                flip = !flip;
            }


            AltitudeData = new ObservableCollection<DataPoint>();

            // Init all to 0
            CurrentAltitude_qv = 0;
            ApogeeAltitude_qv = 0;
            PredictedApogeeAltitude_qv = 0;
            XAcceleration_qv = 0;
            YAcceleration_qv = 0;
            ZAcceleration_qv = 0;

            GPSAltitude_qv = 0;
            GPSLatitude_qv = 0;
            GPSLongitude_qv = 0;

        }

        /// <summary>
        /// Sets the telemetry model to the same telemetry object as the telemetry model
        /// One model updates two displays
        /// </summary>
        /// <param name="telemetryModel"></param>
        public void SetTMModel(TelemetryModel telemetryModel, TMData TMData)
        {
            _TMModel = telemetryModel;

            _tmdata = TMData;

            #region Event Handlers

            //_TMModel.FakeDataTestUpdateUI += _TMModelChangeTheAltitude;

            _tmdata.UpdateHomeViewEvent += _tmmessage_UpdateHomewViewDisplay;

            _TMModel.UpdateIndicatorLights1 += _TMModel_UpdateIndicatorLights;

            #endregion

            SendMessageCommand = new ViewCommand(SendMessage, CanSendMessage);

        }

        /// <summary>
        /// Sends a message to the COM Port to be sent over RF to the rocket
        /// </summary>
        /// <param name="obj"></param>
        private void SendMessage(object obj)
        {
            _TMModel.SendMessage(Message);
        }

        /// <summary>
        /// Indicates if the user can send a message
        /// </summary>
        /// <param name="arg"></param>
        /// <returns>True if the user has typed something in the message box, false otherwise</returns>
        private bool CanSendMessage(object arg)
        {
            return Message != null && Message.Length != 0 && Message.Length <= 4;
        }



        /// <summary>
        /// Updates the Quickview display from the telemetry model object. Updates all values and graphs.
        /// Does not update indicator lights
        /// </summary>
        /// <param name="uqvea">The object being passed that stores all of the event args</param>
        private void _tmmessage_UpdateHomewViewDisplay(UpdateHomeViewEventArgs uqvea)
        {
            DeltaAltitude_qv = _tmdata.CurrentAltitude - CurrentAltitude_qv;
            ApogeeAltitude_qv = _tmdata.CurrentAltitude > ApogeeAltitude_qv ? CurrentAltitude_qv : ApogeeAltitude_qv;
            CurrentAltitude_qv = (float) _tmdata.CurrentAltitude;

            XDeltaAcceleration_qv = (float) _tmdata.XAcceleration - XAcceleration_qv;
            YDeltaAcceleration_qv = (float) _tmdata.YAcceleration - YAcceleration_qv;
            ZDeltaAcceleration_qv = (float) _tmdata.ZAcceleration - ZAcceleration_qv;
            XAcceleration_qv = (float) _tmdata.XAcceleration;
            YAcceleration_qv = (float) _tmdata.YAcceleration;
            ZAcceleration_qv = (float) _tmdata.ZAcceleration;

            PredictedApogeeAltitude_qv = (float) _tmdata.PredictedApogeeAltitude;

            AltitudeData.Add(new DataPoint(uqvea.DataTime, _tmdata.CurrentAltitude));

            GPSLatitude_qv = _tmdata.GPSLat;
            GPSLongitude_qv = _tmdata.GPSLong;
            GPSAltitude_qv = _tmdata.GPSAlt;

        }

        /// <summary>
        /// Updates the lights for the control panel UI object.
        /// </summary>
        private void _TMModel_UpdateIndicatorLights()
        {
            // Go to the UI thread
            _ = Application.Current.Dispatcher.BeginInvoke(new Action(() =>
            {
                // For each light that's changed status, change it and update its color
                // Idk why you have to cast them in that way, but you do
                foreach (int i in _tmdata.StatusMessages.Keys.Where(i => IndicatorLights[(int) i] != _tmdata.StatusMessages[i]))
                {
                    IndicatorLights[i] = _tmdata.StatusMessages[(uint) i];
                }
            }));
        }




        //private void _TMModelChangeTheAltitude()
        //{
        //    // Both event handlers are run
        //    //CurrentAltitude_qv = 53214;
        //}
    }
}
