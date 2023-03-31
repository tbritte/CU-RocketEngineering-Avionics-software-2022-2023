using System;
using System.Device.Location;

namespace ModernUIDesign.MVVM.Model
{
    public class GPSTracker
    {
        #region dd
        // Jonathon's variables
        const float A = 50;
        float vert_B;
        float vert_C;
        float hor_B;
        float hor_C;
        const float init_lat = 50;
        const float init_lon = 50;
        float pass_lat;
        float pass_lon;
        float pass_height;

        #endregion



        #region Kyle's Changes

        private readonly GeoCoordinate GroundStation;

        private GeoCoordinate LaunchPad
        {
            get
            {
                return LaunchPad;
            }
            set
            {
                LaunchPad = value;

                distance_LaunchPadGroundStation = (float) LaunchPad.GetDistanceTo(GroundStation);
            }
        }

        private GeoCoordinate Rocket;

        private float DistanceRocketLaunchPad;
        private float DistanceRocketGroundStation;

        // Unused, but keep around
        private float distance_LaunchPadGroundStation;

        private float thetacurrent;
        private float phicurrent;

        private float thetaold;
        private float phiold;

        private float latitudedifference_LaunchPadGroundStation;

        public float Deltatheta { get; set; }
        public float Deltaphi { get; set; }


        #endregion

        /*
         * NOTE: TODO: GPS COORDINATES COME IN BY N AND W, if something is broken,then that might
         * be it
         */



        public GPSTracker()
        {
            GroundStation = new GeoCoordinate()
            {
                Latitude = 32.940021689741826,
                Longitude = -106.91999002434629,
                Altitude = 0,
            };

            thetaold = 0;
            phiold = 0;
        }

        /// <summary>
        /// Initializes the launchpad coordinates, and an initial set of rocket coordinates
        /// </summary>
        /// <param name="latitude">Latitude of launchpad, as given by first value GPS coordinate</param>
        /// <param name="longitude">Longitude of launchpad, as given by first value of GPS coordinate</param>
        /// <param name="altitude">Altitude of launchpad, as given by first value of GPS coordinate</param>
        public void InitializeLaunchPad(float latitude, float longitude, float altitude)
        {
            LaunchPad = new GeoCoordinate(latitude, longitude, altitude);
            Rocket = new GeoCoordinate(latitude, longitude, altitude);
            latitudedifference_LaunchPadGroundStation = (float) (LaunchPad.Latitude - GroundStation.Latitude);
        }


        /// <summary>
        /// Updates the tracking system and calculates the change in vertical movement, phi, as well as
        /// the change in horizontal movement, thetha
        /// </summary>
        /// <param name="coordinate">A GeoCoordinate class that stores the coordinates of the rocket 
        /// in the last packet</param>
        public void UpdateGPSTracking_ReactiveTracking(GeoCoordinate coordinate)
        {
            // For visual representation of angle meaning refer to
            // the avionics section of the IREC 2022 report
            // Link: https://drive.google.com/file/d/1Hmmw1bX-zu7gTqA-qENsbtp7dILmshIf/view?usp=sharing

            float theta_prime;
            float beta_prime, lambda_prime;
            float deltaaltitude;

            Rocket = coordinate;


            // Find the change in altitude
            deltaaltitude = (float) (Rocket.Altitude - GroundStation.Altitude);
            // Find distance between rocket and launch pad
            DistanceRocketLaunchPad = (float) Rocket.GetDistanceTo(LaunchPad);
            // Find distance between rocket and ground station
            DistanceRocketGroundStation = (float) Rocket.GetDistanceTo(GroundStation);



            // Find beta angle
            beta_prime = (float) Math.Atan2(Math.Abs(latitudedifference_LaunchPadGroundStation),
                Math.Abs(LaunchPad.Longitude - GroundStation.Longitude));
            // Find the lambda angle
            lambda_prime = (float) Math.Atan2(Math.Abs(LaunchPad.Latitude - Rocket.Latitude),
                Math.Abs(LaunchPad.Longitude - Rocket.Longitude));


            // Depending on where the launchpad and ground station are positioned, then we use a diffrent formula
            if (latitudedifference_LaunchPadGroundStation > 0)
            {
                theta_prime = (float) (Math.PI - beta_prime - lambda_prime);
            }
            else if (latitudedifference_LaunchPadGroundStation < 0)
            {
                theta_prime = (float) (Math.PI + beta_prime - lambda_prime);
            }
            // If there is no change
            else
            {
                // Then theta prime is just pi 
                theta_prime = (float) Math.PI;
            }


            // Find the new theta for the horizontal component
            thetacurrent = (float) Math.Asin(Math.Sin(theta_prime) / DistanceRocketGroundStation * DistanceRocketLaunchPad);

            Deltatheta = thetacurrent - thetaold;

            // Now to do the vertical element of the tracking
            phicurrent = (float) Math.Atan2(deltaaltitude, DistanceRocketGroundStation);

            Deltaphi = phicurrent - phiold;


            // Set the currents to the olds
            thetaold = thetacurrent;
            phiold = phicurrent;
        }





        #region Jonathon's


        private float GetVerticalAngle()
        {
            float angle;
            angle = (float) (Math.Pow(vert_B, 2) - (Math.Pow(A, 2) + Math.Pow(vert_C, 2)));
            angle /= -1 * A * vert_C;
            angle = (float) Math.Acos(angle);
            return angle;
        }

        private float GetHorizontalAngle()
        {
            float angle;
            angle = (float) (Math.Pow(hor_B, 2) - (Math.Pow(A, 2) + Math.Pow(hor_C, 2)));
            angle /= (-1 * A * hor_C);
            angle = (float) Math.Acos(angle);
            return angle;
        }

        public float UpdateVerticalTracking(float lat, float lon, float height)
        {
            updatevariables(lat, lon, height);


            // updates the vertical triangle
            GetVerticalDistanceB();
            GetVerticalDistanceC();



            float theta = GetVerticalAngle();

            return GetVerticalAngle();
        }

        public float UpdateHorizontalTracking(float lat, float lon, float height)
        {
            float angle;
            updatevariables(lat, lon, height);
            UpdateHorizontalB();
            UpdateHorizontalC();
            angle = GetHorizontalAngle();
            if (pass_lat < 0)
            {
                angle *= -1;
            }
            return angle;
        }


        // class methods 
        private void updatevariables(float lat, float lon, float height)
        {
            pass_height = height;
            pass_lon = init_lon - lon;
            pass_lat = init_lat - lat;

        }

        // update methods for vertical triangle
        private void GetVerticalDistanceB()
        {
            vert_B = pass_height;
        }


        private void GetVerticalDistanceC()
        {
            float hypotenuse;
            hypotenuse = (float) Math.Pow(vert_B, 2) + (float) Math.Pow(A, 2);
            hypotenuse = (float) Math.Sqrt(hypotenuse);
            vert_C = hypotenuse;
        }

        // updates methods for horizontal triangle
        private void UpdateHorizontalB()
        {
            float lon_holder = A + pass_lon;
            float hyp;
            hyp = (float) Math.Pow(lon_holder, 2) + (float) Math.Pow(pass_lat, 2);
            hyp = (float) Math.Sqrt(hyp);
            hor_B = hyp;
        }

        private void UpdateHorizontalC()
        {
            float hyp;
            hyp = (float) Math.Pow(pass_lat, 2) + (float) Math.Pow(pass_lon, 2);
            hyp = (float) Math.Sqrt(hyp);
            hor_C = hyp;
        }

        #endregion 
    }
}
