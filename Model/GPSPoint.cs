using System;

namespace ModernUIDesign.MVVM.Model
{
    public class GPSPoint
    {
        public GPSPoint(float latitude, float longitude, float altitude, DateTime dataTime)
        {
            Latitude = latitude;
            Longitude = longitude;
            Altitude = altitude;
            DataTime = dataTime;
        }

        public float Latitude { get; set; }
        public float Longitude { get; set; }
        public float Altitude { get; set; }
        public DateTime DataTime { get; set; }

    }
}
