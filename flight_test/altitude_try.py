import pandas as pd
from flight_status import FlightStatus

fs = FlightStatus()
data = pd.read_csv("altitudes.csv")
altitudes = data["Altitude"].to_list()
for i, a in enumerate(altitudes):
    fs.add_altitude(a)
    if i > 64:
        fs.new_telemetry({"altitude": a})
        print(i, a, fs.stage.name)

