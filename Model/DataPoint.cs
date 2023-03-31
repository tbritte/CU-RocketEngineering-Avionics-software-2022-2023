using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ModernUIDesign.MVVM.Model
{
    public class DataPoint
    {
        public DataPoint(DateTime time, double value)
        {
            Time = time;
            Value = value;
        }

        public DateTime Time { get; set; }
        public double Value { get; set; }
    }


    public class GPSDataPoint
    {
        public GPSDataPoint(float gPSLatitude, float gPSLongitude)
        {
            Latitude = gPSLatitude;
            Longitude = gPSLongitude;
        }

        public float Latitude { get; set; }
        public float Longitude { get; set; }
    }


}
