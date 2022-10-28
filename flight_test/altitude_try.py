import pandas as pd
from flight_status import FlightStatus

fs = FlightStatus()
data = pd.read_csv("altitudes.csv")
altitudes = data["Altitude"].to_list()
for i, a in enumerate(altitudes):
    fs.add_altitude(a)
    if a > 64:
        apog = fs.check_apogee()
        print(i, a, apog)
        if apog:
            break

