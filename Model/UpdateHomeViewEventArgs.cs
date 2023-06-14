using System;

namespace ModernUIDesign.MVVM.Model
{

    public class UpdateHomeViewEventArgs : EventArgs
    {


        public UpdateHomeViewEventArgs(DateTime dataTime)
        {
            DataTime = dataTime;
        }

        public DateTime DataTime { get; set; }
    }
}
