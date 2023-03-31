using System;

namespace ModernUIDesign.MVVM.Model
{
    public class UpdateTelemetryViewInvalidEventArgs : EventArgs
    {
        public UpdateTelemetryViewInvalidEventArgs(uint totalMessages, bool dataValid)
        {
            TotalMessages = totalMessages;
            DataValid = dataValid;
        }

        public uint TotalMessages { get; set; }
        public bool DataValid { get; set; }

    }
}
