using System;
using System.Collections.Concurrent;
using System.IO;
using System.Text;
using System.Windows;

namespace ModernUIDesign.MVVM.Model
{
    public class TMData
    {
        // Updates the home view with data from the TM message
        public delegate void UpdateHomeViewEventHandler(UpdateHomeViewEventArgs uqvea);
        public event UpdateHomeViewEventHandler UpdateHomeViewEvent;

        // Update the TM view with data from the TM message
        public delegate void UpdateTelemetryViewEventHandler(UpdateTelemetryViewEventArgs utvea);
        public event UpdateTelemetryViewEventHandler UpdateTelemetryViewEvent;

        // Update the TM view with invalid message/indicators
        public delegate void TMViewInvalidDataUpdateEventHandler(UpdateTelemetryViewInvalidEventArgs iduea);
        public event TMViewInvalidDataUpdateEventHandler UpdateTMViewInvalidDataUpdateEvent;

        private StreamWriter _streamWriter;
        private StringBuilder _stringBuilder;

        string startstringtime;

        public TMData()
        {
            _stringBuilder = new StringBuilder();

            // Init to -1000, so we can transmit TM without GPS lock
            // and not set the launchpad coordinates by accident
            GPSLat = -1000;
            GPSLong = -1000;

        }


        #region TM Message Data

        private float _alt;
        private float _apogeealt;
        private float _prediction;
        private float _xaccel;
        private float _yaccel;
        private float _zaccel;
        private float _gpslat;
        private float _gpslong;
        private float _gpsalt;


        public ConcurrentDictionary<uint, bool> StatusMessages;
        public bool DataValid { get; set; }
        public ushort MFC1 { get; set; }
        public ushort MFC2 { get; set; }
        public uint GoodM { get; set; }
        public uint TotalM { get; set; }
        public float ValidMessagesPercentage { get; set; }
        public float CurrentAltitude
        {
            get => _alt;
            set
            {
                _alt = value;
            }
        }
        public float ApogeeAltitude
        {
            get => _apogeealt;
            set
            {
                _apogeealt = value;
            }
        }
        public float PredictedApogeeAltitude
        {
            get => _prediction;
            set
            {
                _prediction = value;
            }
        }
        public float XAcceleration
        {
            get => _xaccel;
            set
            {

                _xaccel = value;
            }
        }
        public float YAcceleration
        {
            get => _yaccel;
            set
            {
                _yaccel = value;
            }
        }
        public float ZAcceleration
        {
            get => _zaccel;
            set
            {
                _zaccel = value;
            }
        }
        public float GPSLat
        {
            get => _gpslat;
            set
            {
                _gpslat = value;
            }
        }
        public float GPSLong
        {
            get => _gpslong;
            set
            {
                _gpslong = value;
            }
        }
        public float GPSAlt
        {
            get => _gpsalt;
            set
            {
                _gpsalt = value;
            }
        }
        public float XGyroscope { get; set; }
        public float YGyroscope { get; set; }
        public float ZGyroscope { get; set; }
        public float XMagnetometer { get; set; }
        public float YMagnetometer { get; set; }
        public float ZMagnetometer { get; set; }
        public float Temperature { get; set; }
        public float Humidity { get; set; }
        public ushort Heading { get; set; }
        public DateTime DataTime { get; set; } // What actually gets sent to the vm

        #endregion


        #region Events

        /// <summary>
        /// Updates the telemetry view of the GUI with the data from the message
        /// </summary>
        /// <param name="LaunchDetected"></param>
        public void UpdateTMView(bool LaunchDetected)
        {
            // Go to UI thread and update the TM view with data
            _ = Application.Current.Dispatcher.BeginInvoke(new Action(() =>
            {
                UpdateTelemetryViewEvent?.Invoke(new UpdateTelemetryViewEventArgs(LaunchDetected));
            }));
        }


        /// <summary>
        /// Updates the home view of the GUI with the data from the message
        /// </summary>
        public void UpdateHomeView()
        {
            // Go to UI and update home view
            _ = Application.Current.Dispatcher.BeginInvoke(new Action(() =>
            {
                UpdateHomeViewEvent?.Invoke(new UpdateHomeViewEventArgs(DataTime));
            }));
        }

        /// <summary>
        /// Updates the telemetry view with an invalid message
        /// </summary>
        public void UpdateTMViewInvalid()
        {
            // Go to UI and update TM view with invalid data
            _ = Application.Current.Dispatcher.BeginInvoke(new Action(() =>
            {
                UpdateTMViewInvalidDataUpdateEvent?.Invoke(new UpdateTelemetryViewInvalidEventArgs(TotalM, DataValid));
            }));
        }

        #endregion


        #region Data File Setup and Writing

        /// <summary>
        /// Sets up the data file for the telemetry data
        /// </summary>
        public void SetupDataFile()
        {
            startstringtime = DateTime.Now.ToString("M_d_yyyy HH_mm_ss"); ;

            _streamWriter = new StreamWriter(startstringtime + "_curocket.csv", true);
            // Maybe we could set up a save file dialog here, but let's get it working first


            WriteFileHeader();
        }

        /// <summary>
        /// Writes the telemetry data to the data file
        /// </summary>
        /// <param name="statuscheckdata"></param>
        public void WriteToDataFile(ushort statuscheckdata)
        {
            // Append, write, and then flush to data file
            _ = _stringBuilder.AppendLine($"{MFC1},{MFC2},{CurrentAltitude},{XAcceleration},{YAcceleration},{ZAcceleration},{XGyroscope}," +
                        $"{YGyroscope},{ZGyroscope},{XMagnetometer},{YMagnetometer},{ZMagnetometer}," +
                        $"{Temperature},{Humidity},{PredictedApogeeAltitude},{GPSLat},{GPSLong},{GPSAlt},{DataTime},{statuscheckdata}");
            _streamWriter.Write(_stringBuilder);
            _stringBuilder.Clear();
            _streamWriter.Flush();
        }


        /// <summary>
        /// Writes the telemetry data file header
        /// </summary>
        private void WriteFileHeader()
        {
            // Clear if anything in
            _ = _stringBuilder.Clear();
            // Write header and then clear
            _ = _stringBuilder.Append(startstringtime + "\nTM1:\nMFC1:,MFC2:,Altitude:,X Acceleration:,Y Acceleration:,Z Acceleration:,X Gyroscope:,Y Gyroscope:,Z Gyroscope:,X Magnetometer:,Y Magnetometer:,Z Magnetometer:,Temperature:,Predicted Apogee:,Humidity:,Latitude:,Longitude:,Altitude (GPS),Time:,Status:\n");
            _streamWriter.WriteLine(_stringBuilder);
            _ = _stringBuilder.Clear();
            // Writes to the file
            _streamWriter.Flush();
        }

        /// <summary>
        /// Closes the data file
        /// </summary>
        public void CloseDataFile()
        {
            // Write any remaining data
            if (_stringBuilder.Length > 0)
            {
                _streamWriter.WriteLine(_stringBuilder);
                _ = _stringBuilder.Clear();
            }
            // Dispose streamwriter
            _streamWriter.Dispose();
        }

        #endregion
    }
}
