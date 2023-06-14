using System;


namespace ModernUIDesign.MVVM.Model
{
    public class UpdateTelemetryViewEventArgs : EventArgs
    {

        public UpdateTelemetryViewEventArgs(bool _launchdetected)
        {
            LaunchDetected = _launchdetected;
        }


        public bool LaunchDetected { get; set; }

    }
}
