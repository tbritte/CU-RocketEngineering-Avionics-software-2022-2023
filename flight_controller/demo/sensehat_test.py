from sense_hat import SenseHat
from time import sleep
import math

sense = SenseHat()
sense.clear()                     # clear sense hat


o = (245, 102, 0)
p = (82, 45, 128)

sense.show_message("YEAHHH",text_colour=o,back_colour=p)    # Displays some text

sleep(0.5)

paw = [
    p, p, p, o, o, p, p, p,
    o, o, p, o, o, p, o, o,
    o, o, p, o, p, o, o, o,
    o, p, p, p, p, o, o, p,
    p, o, o, o, o, p, p, o,
    o, o, o, o, o, p, o, o,
    o, o, o, o, o, p, o, o,
    o, o, o, o, o, p, p, p,
    ]
sense.set_pixels(paw)            # a paw should be displayed on the LED screen

t = 201
while t is 201:                 # Idles here until trigger activates flight mode
    for event in sense.stick.get_events():  # Currently waits for joystick to be pressed
        if event.action == "pressed":
            t = 0
        else:
            print("waiting")
            sleep(0.01)

sense.clear()
sense.set_imu_config(True, True, True)

while t == 0:
    for event in sense.stick.get_events():  # Trigger to exit
        if event.action == "pressed":       # Activate by pressing joystick
            t = 3
        else:
            sleep(0.01)
    pressure = sense.get_pressure()         # hPa
    temp = sense.get_temperature()          # C, will not be accurate due to pi heat
    humidity = sense.get_humidity()         # % humidity

    acceleration = sense.get_accelerometer_raw()
    ax = acceleration['x']                  # gees
    ay = acceleration['y']
    az = acceleration['z']
    XY = math.sqrt(ax*ax + ay*ay)
    accel = math.sqrt(XY*XY + az*az)
    orient = sense.get_orientation()
    oy = orient['pitch']
    ox = orient['roll']
    oz = orient['yaw']
    gyro = sense.get_gyroscope_raw()
    gx = gyro['x'] # roll velocity
    gy = gyro['y'] # pitch velocity
    gz = gyro['z'] # yaw velocity
    print("Pressure is {0}".format(pressure))
    print("Temperature is {0}".format(temp))
    sleep(0.25)
