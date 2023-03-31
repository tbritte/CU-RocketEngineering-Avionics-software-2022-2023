using DevExpress.Mvvm.Native;
using DevExpress.Spreadsheet;
using System;
using System.Collections.Concurrent;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Data;
using System.Device.Location;
using System.Globalization;
using System.IO.Ports;
using System.Linq;

namespace ModernUIDesign.MVVM.Model
{
    public class TelemetryModel
    {
        #region General

        //private Workbook _dataworkbook; Make everything an excel spreadsheet -> But we can do that later, let's start with a CSV file

        #region Index Constants For Message Parsing

        public const int ALTITUDEINDEX = 7;
        public const int ACCELERATIONXINDEX = 11;
        public const int ACCELERATIONYINDEX = 15;
        public const int ACCELERATIONZINDEX = 19;
        public const int GYROSCOPEXINDEX = 23;
        public const int GYROSCOPEYINDEX = 27;
        public const int GYROSCOPEZINDEX = 31;
        public const int MAGNETOMETERXINDEX = 35;
        public const int MAGNETOMETERYINDEX = 39;
        public const int MAGNETOMETERZINDEX = 43;
        public const int TEMPERATUREINDEX = 47;
        public const int PREDICTEDAPOGEEINDEX = 51;
        public const int HUMIDITYINDEX = 55;
        public const int GPSLATITUDEINDEX = 59;
        public const int GPSLONGITUDEINDEX = 63;
        public const int GPSALTITUDEINDEX = 67;

        #endregion

        public BackgroundWorker TelemetryDataCollector;
        public BackgroundWorker IndicatorLightUpdater;
        public BackgroundWorker ServoMotorMovementCalculator;

        private SerialPort TelemetryPort;
        private SerialPort ArduinoPort;
        private TMData _tmdata;
        private GPSTracker _gpstracker;

        private const int MESSAGESIZE = 80, SYNCSIZE = 3;
        private byte[] data, databuffer;
        // TODO: Adjust, possibly
        private const string ArduinoPortName = "COM3";

        public string StringStartTime { get; set; }

        private bool _canstart, _canend, _collectionactive;
        public bool CanStart
        {
            get { return _canstart; }
            set
            {
                _canstart = value;
                UpdateButtonAccess?.Invoke();
            }
        }
        public bool CanEnd
        {
            get { return _canend; }
            set
            {
                _canend = value;
                UpdateButtonAccess?.Invoke();
            }
        }
        public bool TMLinkActive
        {
            get { return _collectionactive; }
            set
            {
                _collectionactive = value;
                UpdateButtonAccess?.Invoke();
            }
        }

        public ObservableCollection<SerialPort> AvailableCOMPorts;
        public string NameOfComPort;

        public bool LaunchDetected { get; set; }
        public ulong TimeOfData { get; set; }

        public bool IsFirst { get; set; } = false;


        #endregion



        #region Events and Handlers

        public delegate void UpdateAvailableCOMPortsEventHandler();
        public event UpdateAvailableCOMPortsEventHandler UpdateAvailableCOMPorts;

        public delegate void UpdateButtonAccessEventHandler();
        public event UpdateButtonAccessEventHandler UpdateButtonAccess;

        public delegate void UpdateIndicatorLights1EventHandler();
        public event UpdateIndicatorLights1EventHandler UpdateIndicatorLights1;

        #endregion

        /// <summary>
        /// Telemetry Model Constructor
        /// </summary>
        public TelemetryModel()
        {
            AvailableCOMPorts = new ObservableCollection<SerialPort>();
            AvailableCOMPorts.CollectionChanged += AvailableCOMPorts_CollectionChanged;

            #region Background Workers

            IndicatorLightUpdater = new BackgroundWorker();
            IndicatorLightUpdater.DoWork += IndicatorLightUpdater_DoWork;

            ServoMotorMovementCalculator = new BackgroundWorker();
            ServoMotorMovementCalculator.DoWork += ServoMotorMovementCalculator_DoWork;
            ServoMotorMovementCalculator.RunWorkerCompleted += ServoMotorMovementCalculator_RunWorkerCompleted;

            TelemetryDataCollector = new BackgroundWorker();
            TelemetryDataCollector.DoWork += TelemetryDataCollector_DoWork;

            #endregion

            // TODO: uncomment
            // Port to the arduino
            //ArduinoPort = new SerialPort()
            //{
            //    PortName = ArduinoPortName,
            //    BaudRate = 9600,
            //    Parity = Parity.None,
            //    DataBits = 8,
            //    StopBits = StopBits.One
            //};

            // Port receiving rocket data
            TelemetryPort = new SerialPort()
            {
                BaudRate = 57600,
                Parity = Parity.None,
                DataBits = 8,
                StopBits = StopBits.One,
            };
            TelemetryPort.DataReceived += TelemetryPort_DataReceived;

            _gpstracker = new GPSTracker();


            CanStart = true;
            LaunchDetected = false;
        }

        ~TelemetryModel()
        {
            AvailableCOMPorts.Clear();
            TelemetryPort.Close();
            TelemetryPort.Dispose();
        }




        #region Data Receiving and Processing

        /// <summary>
        /// Runs whenever the serial port receives data, if the worker is not busy, if it is not being cancelled, and 
        /// there are enough Bytes for a message, then it runs the worker to parse the message
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void TelemetryPort_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            if (!TelemetryDataCollector.IsBusy && !TelemetryDataCollector.CancellationPending && TelemetryPort.BytesToRead >= MESSAGESIZE)
            {
                TelemetryDataCollector.RunWorkerAsync();
            }
        }



        /// <summary>
        /// Processes, parses, and validates the possible message being downlinked
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void TelemetryDataCollector_DoWork(object sender, DoWorkEventArgs e)
        {
            data = new byte[MESSAGESIZE];
            databuffer = new byte[MESSAGESIZE];
            int[] startingindexes = new int[MESSAGESIZE];
            bool syncacquired = false;
            byte checksum = 0;
            ushort statuscheck = 0, statuscount = 0;
            ushort statuscheckdata = 0;
            float Lat, Long; // For GPS stuff to convert from DDM to DD
            float degrees, minutes;

            // Read MESSAGESIZE Bytes into databuffer
            _ = TelemetryPort.Read(databuffer, 0, MESSAGESIZE);

            // Finds the indexes of all the elements in data buffer whose value is equal to 'C' and
            // puts them in the starting indexes array
            startingindexes = databuffer.Select((c, i) => c == 'C' ? i : -1).Where(i => i != -1).ToArray();

            // For each starting index, look for a set of sync bytes, if those syncs "extend over" a message,
            // then read in new data to figure out if valid
            foreach (int c in startingindexes)
            {
                // IF buffer is in sync
                if (c == 0 && databuffer[1] == 'R' && databuffer[2] == 'E')
                {
                    // Then just copy buffer over to data
                    data = databuffer;
                    syncacquired = true;
                    break;
                }
                // If not in sync, but the sync does not "extend over" the data read into the buffer
                else if (c <= (MESSAGESIZE - 3) && databuffer[c + 1] == 'R' && databuffer[c + 2] == 'E')
                {
                    // Then copy the first MESSAGESIZE - c of buffer into data -> This is the part of the message already in the buffer
                    Buffer.BlockCopy(databuffer, c, data, 0, MESSAGESIZE - c);

                    // Read into the data array the rest of the message, beginning at the index of MESSAGESIZE - c, and read c number of bytes
                    _ = TelemetryPort.Read(data, MESSAGESIZE - c, c);
                    syncacquired = true;
                    break;
                }
                // If the sync extends over what we've read in by 1 byte, in that C & R are present, but E is not
                else if (c == (MESSAGESIZE - 2) && databuffer[c + 1] == 'R')
                {
                    // Then read one byte into the 0th index of the buffer, this should bring the E in
                    _ = TelemetryPort.Read(databuffer, 0, 1);

                    // If that byte is an 'E'
                    if (databuffer[0] == 'E')
                    {
                        // Then we have a sync set. Copy over the C, R, & E from the buffer to data
                        data[0] = databuffer[c];
                        data[1] = databuffer[c + 1];
                        data[2] = databuffer[0];

                        // We just read in the sync, so read in the rest of the message into the data array. Offset by the sync size,
                        // and read the message size minus the sync size to just grab a message
                        _ = TelemetryPort.Read(data, SYNCSIZE, MESSAGESIZE - SYNCSIZE);
                        syncacquired = true;
                        break;
                    }
                }
                // If the sync extends over two bytes, in that we have a 'C', but we haven't read in the 'R' and 'E' yet
                else if (c == (MESSAGESIZE - 1))
                {
                    // Then we read two bytes in
                    _ = TelemetryPort.Read(databuffer, 0, 2);

                    // If the two bytes read in are R and E
                    if (databuffer[0] == 'R' && databuffer[1] == 'E')
                    {
                        // Then we have a valid sync set. Copy sync buffer into data
                        data[0] = databuffer[c];
                        data[1] = databuffer[0];
                        data[2] = databuffer[1];

                        // We just read in the sync, so read in the rest of the message into the data array. Offset by the sync size,
                        // and read the message size minus the sync size to just grab a message
                        _ = TelemetryPort.Read(data, SYNCSIZE, MESSAGESIZE - SYNCSIZE);
                        syncacquired = true;
                        break;

                    }
                }
            }

            // If we found a sync set/there is a message
            if (syncacquired)
            {
                checksum = 0;

                for (int i = 0; i < MESSAGESIZE - 1; i++)
                {
                    checksum ^= data[i];
                }

                // If contents are valid from checksum
                if (checksum == data[MESSAGESIZE - 1])
                {
                    // Then read and process message

                    _tmdata.GoodM++;
                    _tmdata.TotalM++;

                    _tmdata.DataValid = true;

                    _tmdata.MFC1 = (ushort) (((data[4] & 0xff) << 8) | (data[3] & 0xff));
                    _tmdata.MFC2 = (ushort) (((data[6] & 0xff) << 8) | (data[5] & 0xff));

                    // Need to set time first so that quick view can push to graph automatically
                    TimeOfData = (ulong) (((data[74] & 0xff) << 24) | ((data[73] & 0xff) << 16) | ((data[72] & 0xff) << 8) | (data[71] & 0xff));
                    try
                    {
                        _tmdata.DataTime = DateTime.ParseExact(_tmdata.DataTime.ToString("D9"), "HHmmssfff", CultureInfo.InvariantCulture);
                    }
                    catch (FormatException)
                    {
                        _tmdata.DataTime = DateTime.Now;
                    }

                    for (int messageindex = 7; messageindex < (MESSAGESIZE - 5); messageindex += 4)
                    {
                        switch (messageindex)
                        {
                            case ALTITUDEINDEX:
                                _tmdata.CurrentAltitude = BitConverter.ToSingle(data, messageindex);
                                // If current is more than apogee, current is now apogee
                                if (_tmdata.CurrentAltitude > _tmdata.ApogeeAltitude)
                                {
                                    _tmdata.ApogeeAltitude = _tmdata.CurrentAltitude;
                                }
                                break;
                            case ACCELERATIONXINDEX:
                                _tmdata.XAcceleration = BitConverter.ToSingle(data, messageindex);
                                break;
                            case ACCELERATIONYINDEX:
                                _tmdata.YAcceleration = BitConverter.ToSingle(data, messageindex);
                                break;
                            case ACCELERATIONZINDEX:
                                _tmdata.ZAcceleration = BitConverter.ToSingle(data, messageindex);
                                break;
                            case GYROSCOPEXINDEX:
                                _tmdata.XGyroscope = BitConverter.ToSingle(data, messageindex);
                                break;
                            case GYROSCOPEYINDEX:
                                _tmdata.YGyroscope = BitConverter.ToSingle(data, messageindex);
                                break;
                            case GYROSCOPEZINDEX:
                                _tmdata.ZGyroscope = BitConverter.ToSingle(data, messageindex);
                                break;
                            case MAGNETOMETERXINDEX:
                                _tmdata.XMagnetometer = BitConverter.ToSingle(data, messageindex);
                                break;
                            case MAGNETOMETERYINDEX:
                                _tmdata.YMagnetometer = BitConverter.ToSingle(data, messageindex);
                                break;
                            case MAGNETOMETERZINDEX:
                                _tmdata.ZMagnetometer = BitConverter.ToSingle(data, messageindex);
                                break;
                            case TEMPERATUREINDEX:
                                _tmdata.Temperature = BitConverter.ToSingle(data, messageindex);
                                break;
                            case PREDICTEDAPOGEEINDEX:
                                _tmdata.PredictedApogeeAltitude = BitConverter.ToSingle(data, messageindex);
                                break;
                            case HUMIDITYINDEX:
                                _tmdata.Humidity = BitConverter.ToSingle(data, messageindex);
                                break;
                            case GPSLATITUDEINDEX:
                                // convert from DDm to DD
                                Lat = BitConverter.ToSingle(data, messageindex);
                                degrees = (float) Math.Floor(Lat / 100.0);
                                minutes = (float) (Lat - degrees * 100.0);
                                _tmdata.GPSLat = (float) Math.Round((double) (degrees + minutes / 60.0), 5);
                                break;
                            case GPSLONGITUDEINDEX:
                                // convert from DDm to DD

                                Long = BitConverter.ToSingle(data, messageindex);
                                degrees = (float) Math.Floor(Long / 100.0);
                                minutes = (float) (Long - degrees * 100.0);
                                _tmdata.GPSLong = (float) Math.Round((double) (degrees + minutes / 60.0), 5);
                                break;
                            case GPSALTITUDEINDEX:
                                _tmdata.GPSAlt = BitConverter.ToSingle(data, messageindex);
                                break;
                            case 71:
                                // Data Time, see above
                                break;
                            default:
                                break;
                        }
                    }

                    _tmdata.Heading = (ushort) (((data[76] & 0xff) << 8) | (data[75] & 0xff));



                    statuscheck = statuscheckdata = (ushort) (((data[78] & 0xff) << 8) | (data[77] & 0xff));

                    // While we haven't progressed through all of the status vars
                    while (statuscount < 16)
                    {
                        // If the last bit in statuscheck is a 1, then set that status message to true
                        // If not, then put a false
                        _tmdata.StatusMessages[statuscount] = (statuscheck & 0x01) == 0x01;
                        // Move the statuscheck over by one bit
                        statuscheck >>= 1;
                        // inc the status count to move to the next status bit 
                        statuscount++;
                    }


                    if (_tmdata.StatusMessages[6])
                    {
                        LaunchDetected = true;
                    }

                    _tmdata.ValidMessagesPercentage = _tmdata.TotalM == 0 ? 100 : (float) ((float) _tmdata.GoodM / _tmdata.TotalM) * 100;

                    IndicatorLightUpdater.RunWorkerAsync();

                    // TODO: Uncomment
                    // init the launch pad coordinates on first transmission
                    //if (IsFirst && _tmdata.GPSLat != -1000 && _tmdata.GPSLong != -1000)
                    //{
                    //    _gpstracker.InitializeLaunchPad(_tmdata.GPSLat, _tmdata.GPSLong, _tmdata.GPSAlt);
                    //    IsFirst = false;
                    //}
                    // Calculate movement of servo motors
                    // ServoMotorMovementCalculator.RunWorkerAsync(new GeoCoordinate(_tmdata.GPSLat, _tmdata.GPSLong, _tmdata.CurrentAltitude));

                    // Recording data as of now, issue seems resolved
                    _tmdata.WriteToDataFile(statuscheckdata);

                    // Update the TM and home views from the message object
                    _tmdata.UpdateTMView(LaunchDetected);
                    _tmdata.UpdateHomeView();

                }
                // If message fails checksum
                else
                {
                    // Then message is corrupt
                    _tmdata.DataValid = false;
                    _tmdata.TotalM++;
                    _tmdata.ValidMessagesPercentage = (float) ((float) _tmdata.GoodM / _tmdata.TotalM) * 100;
                    // Update with updated totalm and data valid
                    _tmdata.UpdateTMViewInvalid();

                }
            }
        }




        /// <summary>
        /// Calls an event that updates the indicator lights for TM1
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void IndicatorLightUpdater_DoWork(object sender, DoWorkEventArgs e)
        {
            UpdateIndicatorLights1?.Invoke();
        }

        #endregion






        #region Servo Motor Movement

        /// <summary>
        /// Calculates how much and in what direction the stepper motors need to move at
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void ServoMotorMovementCalculator_DoWork(object sender, DoWorkEventArgs dwea)
        {
            _gpstracker.UpdateGPSTracking_ReactiveTracking((GeoCoordinate) dwea.Argument);
        }

        /// <summary>
        /// Sends the movements that need to be made to the arduino
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void ServoMotorMovementCalculator_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            // *Send to arduino*
            SendToArduino(_gpstracker.Deltatheta, _gpstracker.Deltaphi);
        }

        /// <summary>
        /// Sends the change in the angles to the arduino for the ground station tracking
        /// </summary>
        /// <param name="dtheta">The change in horizontal angle, theta</param>
        /// <param name="dphi">The change in vertical angle, phi</param>
        private void SendToArduino(float dtheta, float dphi)
        {
            char[] messagebytes = new char[4];
            char horizontalsignchar, verticalsignchar;

            if (dtheta < 0)
            {
                horizontalsignchar = (char) 1;
            }
            else
            {
                horizontalsignchar = (char) 0;
            }
            if (dphi < 0)
            {
                verticalsignchar = (char) 1;
            }
            else
            {
                verticalsignchar = (char) 0;
            }
            // The number of steps that the stepper motor needs to take
            char stepnumbervertical = (char) (int) (Math.Abs(dtheta) * 180 / Math.PI);
            char stepnumberhorizontal = (char) (int) (Math.Abs(dphi) * 180 / Math.PI); ;

            messagebytes[0] = horizontalsignchar;
            messagebytes[1] = stepnumbervertical;
            messagebytes[2] = verticalsignchar;
            messagebytes[3] = stepnumberhorizontal;

            // Write the data to the arduino port
            ArduinoPort.Write(messagebytes, 0, 4);
        }


        #endregion


        #region View Commands


        /// <summary>
        /// Sets up the TM data object for use 
        /// </summary>
        /// <param name="TMData">The TM data object</param>
        public void SetTMData(TMData TMData)
        {
            _tmdata = TMData;

            _tmdata.StatusMessages = new ConcurrentDictionary<uint, bool>();

            for (uint i = 0; i < 16; i++)
            {
                _tmdata.StatusMessages.TryAdd(i, false);
            }

            _tmdata.TotalM = _tmdata.GoodM = 0;

            // TODO: Change to coords from Peter
            _tmdata.GPSLat = 43.0823F;

            _tmdata.GPSLong = 77.3545F;

            _tmdata.GPSAlt = 501.97F;

            _tmdata.DataValid = true;

        }

        #region Start Stop and Reset Link

        /// <summary>
        /// Sets up the data file for data collection, as well as beginning data collection from the 
        /// COM port
        /// </summary>
        public void StartTelemetryLink()
        {

            // This occasionally says access denied
            try
            {
                TelemetryPort.Open();

                CanStart = false;
                CanEnd = true;

                // Set up the data file
                _tmdata.SetupDataFile();

                CanEnd = true;
                CanStart = false;
                TMLinkActive = true;

                //ArduinoPort.Open();
                //ArduinoPort.DiscardOutBuffer();
            }
            catch (UnauthorizedAccessException)
            {
                return;
            }

            TelemetryPort.DiscardInBuffer();


        }


        /// <summary>
        /// Closes the serial port and writes any unwritten data to the files, then closes the files
        /// </summary>
        public void StopDownlink()
        {

            TelemetryPort.Close();
            // Write any leftover data to the file and then dispose of the stream writer
            _tmdata.CloseDataFile();

            CanStart = true;
            CanEnd = false;
            TMLinkActive = false;
            IsFirst = true;

            //_timer.IsEnabled = false;
        }

        /// <summary>
        /// Resets every telemetry view value to zero
        /// </summary>
        public void ResetTelemetryLink()
        {
            _tmdata.DataTime = DateTime.Now;
            _tmdata.CurrentAltitude = _tmdata.ApogeeAltitude = _tmdata.PredictedApogeeAltitude = _tmdata.ZAcceleration = _tmdata.YAcceleration = 0;
            _tmdata.XAcceleration = _tmdata.ZGyroscope = _tmdata.YGyroscope = _tmdata.XGyroscope = 0;
            _tmdata.XMagnetometer = _tmdata.YMagnetometer = _tmdata.ZMagnetometer = 0;
            _tmdata.Temperature = _tmdata.GPSLat = _tmdata.GPSLong = _tmdata.GPSAlt = _tmdata.Humidity = _tmdata.TotalM = _tmdata.GoodM = 0;

            _tmdata.DataValid = true;
            LaunchDetected = false;


            _tmdata.UpdateTMView(LaunchDetected);
            _tmdata.UpdateHomeView();

            // TODO: Call event that clears observable collections

        }

        #endregion


        #region COM Port Selection

        /// <summary>
        /// Gets all of the possible serial ports and adds them to a list of serial port objects
        /// </summary>
        public void RetryCOMPortDetection()
        {
            // Gets all available port names as a string array
            string[] portNames = SerialPort.GetPortNames();
            if (AvailableCOMPorts.Count > 0)
            {
                AvailableCOMPorts.Clear();
            }
            // For every single port name, make a new serial port object with its name as the port name and add the serial port to the available COM ports list
            foreach (string port in portNames)
            {
                SerialPort serialport = new SerialPort()
                {
                    PortName = port
                };

                AvailableCOMPorts.Add(serialport);
            }
        }

        /// <summary>
        /// Sets the name of the selected serial port when the user selects one from the list
        /// </summary>
        /// <param name="comportname">The name of the com port selected by the user</param>
        public void SetCOMPortName(string comportname)
        {
            TelemetryPort.PortName = NameOfComPort = comportname;
            TelemetryPort.Close();
        }

        /// <summary>
        /// Run whenever the AvailableCOMPorts collection changes, if the collection is reset or something is added to it, then it is automatically 
        /// updated on the UI
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void AvailableCOMPorts_CollectionChanged(object sender, System.Collections.Specialized.NotifyCollectionChangedEventArgs e)
        {
            // If a serial port is added, then the update the list of available ports
            if (e.Action == System.Collections.Specialized.NotifyCollectionChangedAction.Add || e.Action == System.Collections.Specialized.NotifyCollectionChangedAction.Reset)
            {
                UpdateAvailableCOMPorts?.Invoke();
            }
        }


        #endregion


        /// <summary>
        /// Outputs a message to the serial port, sending it to the rocket
        /// </summary>
        /// <param name="_outboundmessage"></param>
        public void SendMessage(string _outboundmessage)
        {
            byte checksumout = 0;

            if (_outboundmessage.Length == 3)
            {
                _outboundmessage += " ";
            }
            // Build message
            string messageout = "CRE" + _outboundmessage;

            for (int i = 0; i < 7; i++)
            {
                checksumout ^= (byte) messageout[i];
            }

            // Send message
            if (TMLinkActive)
            {
                TelemetryPort.Write(messageout + checksumout);
            }
        }


        #endregion

    }
}
