using ModernUIDesign.Core;
using ModernUIDesign.MVVM.Model;
using System;
using System.Collections.ObjectModel;
using System.IO.Ports;

namespace ModernUIDesign.MVVM.ViewModel
{
    class TelemetryViewModel : ObservableObject
    {

        private TelemetryModel _TMModel;
        private TMData _tmdata;
        private string _comboboxdefaultmessage, _selectedcomport;
        private bool _canstart, _canend;

        private ObservableCollection<string> _comports;

        private ObservableCollection<DataPoint> _altitudedata;
        private ObservableCollection<DataPoint> _zaccelerationdata, _yaccelerationdata, _xaccelerationdata;
        private ObservableCollection<DataPoint> _zgyroscopedata, _ygyroscopedata, _xgyroscopedata;
        private ObservableCollection<DataPoint> _zmagnetometerdata, _ymagnetometerdata, _xmagnetometerdata;



        #region Getters and Setters

        #region General

        /// <summary>
        /// Object for the TM model
        /// </summary>
        public TelemetryModel telemetryModel
        {
            get => _TMModel;
            set
            {
                _TMModel = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Bool indicating if the user can start the TM link
        /// </summary>
        public bool CanStart
        {
            get { return _canstart; }
            set
            {
                _canstart = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Bool indicating if the user can end the TM link
        /// </summary>
        public bool CanEnd
        {
            get { return _canend; }
            set
            {
                _canend = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Default message of the combo box to select a COM port 
        /// Message is: Select a COM port, I think
        /// </summary>
        public string ComboBoxDefaultMessage
        {
            get { return _comboboxdefaultmessage; }
            set
            {
                _comboboxdefaultmessage = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// String containing the name of the selected COM port to assign
        /// to the COM port object
        /// </summary>
        public string SelectedCOMPort
        {
            get { return _selectedcomport; }
            set
            {
                _selectedcomport = value;
                OnPropertyChanged();
                if (SelectedCOMPort != null)
                {
                    _TMModel.SetCOMPortName(SelectedCOMPort);
                }
                StartDownlinkCommand.RaiseCanExecuteChanged();
            }
        }

        /// <summary>
        /// String collection containing the names of all the COM ports
        /// found
        /// </summary>
        public ObservableCollection<string> COMPorts
        {
            get { return _comports; }
            set
            {
                _comports = value;
                OnPropertyChanged();
            }
        }

        #endregion


        #region TM Data

        #region Collections
        /// <summary>
        /// Data for the altitude graph
        /// </summary>
        public ObservableCollection<DataPoint> AltitudeData
        {
            get => _altitudedata;
            set
            {
                _altitudedata = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Z Acceleration data for graph
        /// </summary>
        public ObservableCollection<DataPoint> ZAccelerationData
        {
            get => _zaccelerationdata;
            set
            {
                _zaccelerationdata = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Y acceleration data for graph
        /// </summary>
        public ObservableCollection<DataPoint> YAccelerationData
        {
            get => _yaccelerationdata;
            set
            {
                _yaccelerationdata = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// X acceleration data for graph
        /// </summary>
        public ObservableCollection<DataPoint> XAccelerationData
        {
            get => _xaccelerationdata;
            set
            {
                _xaccelerationdata = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Z gyroscope data for graph
        /// </summary>
        public ObservableCollection<DataPoint> ZGyroscopeData
        {
            get => _zgyroscopedata;
            set
            {
                _zgyroscopedata = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Y gyroscope data for graph
        /// </summary>
        public ObservableCollection<DataPoint> YGyroscopeData
        {
            get => _ygyroscopedata;
            set
            {
                _ygyroscopedata = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// X gyroscope data for graph
        /// </summary>
        public ObservableCollection<DataPoint> XGyroscopeData
        {
            get => _xgyroscopedata;
            set
            {
                _xgyroscopedata = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Z magnetometer data for graph
        /// </summary>
        public ObservableCollection<DataPoint> ZMagnetometerData
        {
            get => _zmagnetometerdata;
            set
            {
                _zmagnetometerdata = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Y magnetometer data for graph
        /// </summary>
        public ObservableCollection<DataPoint> YMagnetometerData
        {
            get => _ymagnetometerdata;
            set
            {
                _ymagnetometerdata = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// X magnetometer data for graph
        /// </summary>
        public ObservableCollection<DataPoint> XMagnetometerData
        {
            get => _xmagnetometerdata;
            set
            {
                _xmagnetometerdata = value;
                OnPropertyChanged();
            }
        }

        #endregion

        #region System Data

        private float _alt, _validmessagepercentage, _xaccel, _yaccel, _zaccel, _xgyro, _ygyro, _zgyro, _xmag, _ymag, _zmag, _temp, _humid, _predictionapogee;
        private float _latitude, _longitude, _gpsaltitude, _apogee;
        private ushort _mfc1, _mfc2;
        private string _datavalidpanelcover;
        private DateTime? LaunchTime;

        /// <summary>
        /// String that holds the hexcode for what the background of the 
        /// TM panel should be - red if invalid, green for valid
        /// </summary>
        public string DataValidPanelColor
        {
            get => _datavalidpanelcover;
            set
            {
                _datavalidpanelcover = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Major frame counter 1
        /// </summary>
        public ushort MFC1
        {
            get => _mfc1;
            set
            {
                _mfc1 = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Major frame counter 2
        /// </summary>
        public ushort MFC2
        {
            get => _mfc2;
            set
            {
                _mfc2 = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Current altitude recorded by the flight computer
        /// </summary>
        public float Altitude
        {
            get => _alt;
            set
            {
                _alt = value;
                OnPropertyChanged();
                //ChangeAltitudeTestCommand.RaiseCanExecuteChanged();
            }
        }

        /// <summary>
        /// Apogee altitude of the flight
        /// </summary>
        public float Apogee
        {
            get => _apogee;
            set
            {
                _apogee = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Percentage of messages being received that are valid 
        /// What percentage of messages are failing the checksum
        /// </summary>
        public float ValidmsgPercentage
        {
            get => _validmessagepercentage;
            set
            {
                _validmessagepercentage = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Acceleration in the X axis as recorded by the flight computer
        /// </summary>
        public float XAcceleration
        {
            get => _xaccel;
            set
            {
                _xaccel = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Acceleration in the Y axis as recorded by the flight computer
        /// </summary>
        public float YAcceleration
        {
            get => _yaccel;
            set
            {
                _yaccel = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Acceleration in the Z axis as recorded by the flight computer
        /// </summary>
        public float ZAcceleration
        {
            get => _zaccel;
            set
            {
                _zaccel = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Rotational acceleration in the X axis
        /// </summary>
        public float XGyroscope
        {
            get => _xgyro;
            set
            {
                _xgyro = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Rotational acceleration in the Y axis
        /// </summary>
        public float YGyroscope
        {
            get => _ygyro;
            set
            {
                _ygyro = value;
                OnPropertyChanged();
            }
        }

        /// <summary>
        /// Rotational acceleration in the Z axis
        /// </summary>
        public float ZGyroscope
        {
            get => _zgyro;
            set
            {
                _zgyro = value;
                OnPropertyChanged();
            }
        }

        public float XMagnetometer
        {
            get => _xmag;
            set
            {
                _xmag = value;
                OnPropertyChanged();
            }
        }
        public float YMagnetometer
        {
            get => _ymag;
            set
            {
                _ymag = value;
                OnPropertyChanged();
            }
        }
        public float ZMagnetometer
        {
            get => _zmag;
            set
            {
                _zmag = value;
                OnPropertyChanged();
            }
        }

        public float Temperature
        {
            get => _temp;
            set
            {
                _temp = value;
                OnPropertyChanged();
            }
        }

        public float Humidity
        {
            get => _humid;
            set
            {
                _humid = value;
                OnPropertyChanged();
            }
        }

        public float PredictedApogee
        {
            get => _predictionapogee;
            set
            {
                _predictionapogee = value;
                OnPropertyChanged();
            }
        }

        public float Latitude
        {
            get => _latitude;
            set
            {
                _latitude = value;
                OnPropertyChanged();
            }
        }

        public float Longitude
        {
            get => _longitude;
            set
            {
                _longitude = value;
                OnPropertyChanged();
            }
        }

        public float GPSAltitude
        {
            get => _gpsaltitude;
            set
            {
                _gpsaltitude = value;
                OnPropertyChanged();
            }
        }

        private TimeSpan _timesincelaunch;

        public TimeSpan MissionTime
        {
            get => _timesincelaunch;
            set
            {
                _timesincelaunch = value;
                OnPropertyChanged();
            }
        }


        #endregion

        #endregion


        #endregion

        #region View Commands

        public ViewCommand StartDownlinkCommand { get; set; }
        public ViewCommand StopDownlinkCommand { get; set; }
        public ViewCommand ResetDownlinkCommand { get; set; }
        public ViewCommand RefreshCOMPortsCommand { get; set; }

        #endregion


        // red: #FF8080
        // green: #93FFB3

        public TelemetryViewModel()
        {
            #region View Command Instantiation

            StartDownlinkCommand = new ViewCommand(StartDownlink, CanStartDownlink);
            StopDownlinkCommand = new ViewCommand(StopDownlink, CanStopDownlink);
            ResetDownlinkCommand = new ViewCommand(ResetDownlink, CanResetDownlink);
            RefreshCOMPortsCommand = new ViewCommand(RefreshCOMPorts, CanRefreshCOMports);

            #endregion


            DataValidPanelColor = "#93FFB3";
            LaunchTime = null;
        }

        public void DetectCOMPorts()
        {
            // Looks for COM Ports on start up
            _TMModel.RetryCOMPortDetection();
            ComboBoxDefaultMessage = "Select COM Port";
        }


        public void SetTMModel(TelemetryModel telemetryModel, TMData TMData)
        {
            _TMModel = telemetryModel;

            _tmdata = TMData;


            #region Event Handlers

            _tmdata.UpdateTelemetryViewEvent += _tmmessage_UpdateTelemetryView;

            _tmdata.UpdateTMViewInvalidDataUpdateEvent += _tmmessage_UpdateTMViewInvalidDataUpdateEvent;

            _TMModel.UpdateAvailableCOMPorts += _TMModel_UpdateAvailbleCOMPorts;

            _TMModel.UpdateButtonAccess += _TMModel_UpdateButtonAccess;

            #endregion

            #region Collections and Lists

            COMPorts = new ObservableCollection<string>();

            AltitudeData = new ObservableCollection<DataPoint>();

            ZAccelerationData = new ObservableCollection<DataPoint>();
            YAccelerationData = new ObservableCollection<DataPoint>();
            XAccelerationData = new ObservableCollection<DataPoint>();

            ZGyroscopeData = new ObservableCollection<DataPoint>();
            YGyroscopeData = new ObservableCollection<DataPoint>();
            XGyroscopeData = new ObservableCollection<DataPoint>();

            ZMagnetometerData = new ObservableCollection<DataPoint>();
            YMagnetometerData = new ObservableCollection<DataPoint>();
            XMagnetometerData = new ObservableCollection<DataPoint>();

            #endregion


            DetectCOMPorts();

            _TMModel.SetTMData(_tmdata);
        }






        #region View Commands


        /// <summary>
        /// Starts the TM downlink. Creates a new file and opens port
        /// </summary>
        /// <param name="obj"></param>
        public void StartDownlink(object obj)
        {
            // Opens the serial port and a new file
            _TMModel.StartTelemetryLink();

        }

        /// <summary>
        /// Can start link if a comport is selected and the CanStart bool is set to true
        /// </summary>
        /// <param name="arg"></param>
        /// <returns></returns>
        private bool CanStartDownlink(object arg)
        {
            return _TMModel.NameOfComPort != null && SelectedCOMPort != null && _TMModel.CanStart;
        }

        /// <summary>
        /// Stops the TM downlink by closing the port and finalizing saved data to the file
        /// </summary>
        /// <param name="obj"></param>
        private void StopDownlink(object obj)
        {
            // Closes the file and serial port
            _TMModel.StopDownlink();
        }

        private bool CanStopDownlink(object arg)
        {
            return _TMModel.CanEnd;
        }

        /// <summary>
        /// Resets all of the downlink values to zero
        /// </summary>
        /// <param name="obj"></param>
        private void ResetDownlink(object obj)
        {
            _TMModel.ResetTelemetryLink();
            MissionTime = TimeSpan.Zero;
            LaunchTime = null;
        }

        /// <summary>
        /// Can always reset the downlink, since it's just a "visual" change
        /// </summary>
        /// <param name="arg"></param>
        /// <returns></returns>
        private bool CanResetDownlink(object arg)
        {
            return true;
        }


        /// <summary>
        /// Refreshes the list of available COM ports for the user
        /// </summary>
        /// <param name="obj"></param>
        private void RefreshCOMPorts(object obj)
        {
            // Refreshes the available COM ports
            _TMModel.RetryCOMPortDetection();
            ComboBoxDefaultMessage = "Select COM Port";
        }

        /// <summary>
        /// Indicates whether or not the user can refresh the list of COM ports
        /// </summary>
        /// <param name="arg"></param>
        /// <returns>True if the user does not a have a live TM data stream</returns>
        private bool CanRefreshCOMports(object arg)
        {
            return !_TMModel.TMLinkActive;
        }



        #endregion


        #region Events

        /// <summary>
        /// Updates the telemetry view raw data and graphs
        /// </summary>
        /// <param name="utvea"></param>
        private void _tmmessage_UpdateTelemetryView(UpdateTelemetryViewEventArgs utvea)
        {
            // TODO: Add more data stuff, sorta

            Apogee = _tmdata.CurrentAltitude > Apogee ? _tmdata.CurrentAltitude : Apogee;
            Altitude = (float) _tmdata.CurrentAltitude;
            MFC1 = _tmdata.MFC1;
            MFC2 = _tmdata.MFC2;

            ValidmsgPercentage = (float) _tmdata.ValidMessagesPercentage;
            DataValidPanelColor = _tmdata.DataValid ? "#93FFB3" : "#FF8080";

            XAcceleration = (float) _tmdata.XAcceleration;
            YAcceleration = (float) _tmdata.YAcceleration;
            ZAcceleration = (float) _tmdata.ZAcceleration;

            XGyroscope = (float) _tmdata.XGyroscope;
            YGyroscope = (float) _tmdata.YGyroscope;
            ZGyroscope = (float) _tmdata.ZGyroscope;

            XMagnetometer = (float) _tmdata.XMagnetometer;
            YMagnetometer = (float) _tmdata.YMagnetometer;
            ZMagnetometer = (float) _tmdata.ZMagnetometer;

            Temperature = (float) _tmdata.Temperature;
            Humidity = (float) _tmdata.Humidity;
            PredictedApogee = (float) _tmdata.PredictedApogeeAltitude;


            AltitudeData.Add(new DataPoint(_tmdata.DataTime, _tmdata.CurrentAltitude));

            XAccelerationData.Add(new DataPoint(_tmdata.DataTime, _tmdata.XAcceleration));
            YAccelerationData.Add(new DataPoint(_tmdata.DataTime, _tmdata.YAcceleration));
            ZAccelerationData.Add(new DataPoint(_tmdata.DataTime, _tmdata.ZAcceleration));

            XGyroscopeData.Add(new DataPoint(_tmdata.DataTime, _tmdata.XGyroscope));
            YGyroscopeData.Add(new DataPoint(_tmdata.DataTime, _tmdata.YGyroscope));
            ZGyroscopeData.Add(new DataPoint(_tmdata.DataTime, _tmdata.ZGyroscope));

            XMagnetometerData.Add(new DataPoint(_tmdata.DataTime, _tmdata.XMagnetometer));
            YMagnetometerData.Add(new DataPoint(_tmdata.DataTime, _tmdata.YMagnetometer));
            ZMagnetometerData.Add(new DataPoint(_tmdata.DataTime, _tmdata.ZMagnetometer));

            Latitude = _tmdata.GPSLat;
            Longitude = _tmdata.GPSLong;
            GPSAltitude = _tmdata.GPSAlt;


            if (utvea.LaunchDetected)
            {
                if (LaunchTime == null)
                {
                    LaunchTime = _tmdata.DataTime;
                }
                else
                {
                    MissionTime = (TimeSpan) (_tmdata.DataTime - LaunchTime);
                }
            }
        }


        /// <summary>
        /// Updates the telemetry view when the data is invalid with the panel color and the valid message percentage
        /// Less resources than the full update
        /// </summary>
        /// <param name="iduea"></param>
        private void _tmmessage_UpdateTMViewInvalidDataUpdateEvent(UpdateTelemetryViewInvalidEventArgs iduea)
        {
            DataValidPanelColor = _tmdata.DataValid ? "#93FFB3" : "#FF8080";
            ValidmsgPercentage = (float) _tmdata.ValidMessagesPercentage;
        }



        /// <summary>
        /// Updates the available COM ports to the user
        /// </summary>
        private void _TMModel_UpdateAvailbleCOMPorts()
        {
            if (COMPorts.Count > 0)
            {
                COMPorts.Clear();
            }
            if (_TMModel.AvailableCOMPorts.Count == 0)
            {
                COMPorts.Add("No COM Ports Available");
            }
            else
            {
                foreach (SerialPort sp in _TMModel.AvailableCOMPorts)
                {
                    COMPorts.Add(sp.PortName);
                }
            }
        }


        /// <summary>
        /// Updates the TM view button availability to the user
        /// </summary>
        private void _TMModel_UpdateButtonAccess()
        {
            StartDownlinkCommand.RaiseCanExecuteChanged();
            StopDownlinkCommand.RaiseCanExecuteChanged();
            RefreshCOMPortsCommand.RaiseCanExecuteChanged();
        }





        #endregion



    }
}
