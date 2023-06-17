# from sense_hat import SenseHat
from time import sleep
import time
import math
from math import cos
from math import sin
import datetime
from subprocess import call
from picamera import PiCamera
import numpy as np
from gpiozero import CPUTemperature
import serial
import array
import RPi.GPIO as GPIO
import threading
from multiprocessing import Pool
import pigpio

"""
Below are all the modules used that were originally made for SRAD 1
"""

# Sensors mounted on the PCB
from .sensors import sox
from .sensors import bmp180

# Using the same buddy_comm module as SRAD 1 for consistency
from .buddy_comm import BuddyCommSystem

buddy_comm = BuddyCommSystem()  # Used for receiving data operates in a separate thread

"""
Above are all the modules that came from SRAD 1's code base
"""

sense = SenseHat()
sense.clear()  # Sense hat needs to be cleared at the start of every run

cpu = CPUTemperature()
CPUtemp = cpu.temperature

GPIO.setmode(GPIO.BCM)
# Sense Hat uses GPIO 2, 3, 23, 24, 25, 8
buzzer = 27  # Buzzer connects to GPIO 4 (4 down from top left) and ground (3 down from top right)
cam2 = 17  # Servo connects to GPIO 17 (6 down from top left), ground (5 down from top left) and 5v source (top right)
cam3 = 11

# NOTE: THESE HAVE BEEN REPLACED BY THE BUDDY COMM MODULE
# dataWrite = 10
# clockWrite = 9
# dataRead = 22
# clockRead = 27

motorport = 4
# GPIO.setup(dataWrite, GPIO.OUT)
# GPIO.setup(clockWrite, GPIO.OUT)
# GPIO.setup(dataRead, GPIO.IN)
# GPIO.setup(clockRead, GPIO.IN)
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setup(cam2, GPIO.OUT)
GPIO.setup(cam3, GPIO.OUT)
GPIO.setup(clockRead, GPIO.IN)

motor = pigpio.pi()
motor.set_PWM_frequency(motorport, 1000)

date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
startdate = date  # Gathers the date the program starts, used to create files
inittime = round(time.time() * 1000)

Cd = 0.58  # Important values on aerodynamics of the rocket
mass = 1.75  # Values need to be as accurate as possible to ensure
area = 0.008622  # accurate apogee prediction
dt = 0.12
rhostart = 1.21
k = 0.5 * rhostart * Cd * area
# air density (rho) changes depending on altitude, start rho needs to be set to account for launch altitude
# rho at Spaceport America is approx 1.05
# rho in SC about 1.21-1.22
# Cd is drag coefficient, likely between 0.5-0.75
# mass is in kg, needs to be the mass of the rocket and empty motor (mass of rocket when fuel expelled)
# area is the cross sectional area, should just be a circle calculated by radius, measured in m^2
# dt is the time interval for calculations, 0.1s is about as fast as the program can get before slowing significantly

loc = "/home/pi/Desktop/FlightData/"  # Folder where files are saved
# Check desktop folder named "FlightData"
with open(loc + "Basic {}.txt".format(startdate), "w") as file:
    file.write("t Temperature CPUtemp Pressure Humidity Acceleration Altitude State\n")
with open(loc + "Complex {}.txt".format(startdate), "w") as file2:
    file2.write("t ax ay az opit orol oyaw vpit vrol vyaw State\n")
with open(loc + "Alt {}.txt".format(startdate), 'w') as file3:
    file3.write("time timedif curalt apaz curvel appred state\n")
file5 = open(loc + "Telemetry {}.txt".format(startdate), "w")

orange = (245, 102, 0)  # All colors being used for LED display
purple = (82, 45, 128)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
cyan = (0, 255, 255)
clear = (0, 0, 0)


def wait_screen():  # Code for paw print LED display
    o = (245, 102, 0)
    p = (82, 45, 128)
    paw = [
        p, p, p, o, o, p, p, p,  # 0000
        o, o, p, o, o, p, o, o,  # 0000  0000  0000
        o, o, p, o, p, o, o, o,  # 0000  00  000000
        o, p, p, p, p, o, o, p,  # 00        0000
        p, o, o, o, o, p, p, o,  # 00000000    00
        o, o, o, o, o, p, o, o,  # 0000000000  0000
        o, o, o, o, o, p, o, o,  # 0000000000  0000
        p, o, o, o, o, p, p, p,  # 00000000
    ]
    sense.set_pixels(paw)


def indicator(sensor):  # Function to format temp & altitude on LED display
    row = 8
    if sensor is temp:
        col = 6
        val = [0, 12.5, 25, 37.5, 50, 62.5, 75, 87.5]  # Temperature range, big problem if max value is reached
        color = [(255, 0, 0), (252, 79, 0), (242, 118, 0), (226, 151, 0), (202, 181, 0), (170, 208, 0), (125, 232, 0),
                 (0, 255, 0)]
    elif sensor is curalt:
        col = 2
        val = [-100, 250, 500, 750, 1000, 1250, 1500, 1750]
        #        val = [-100, 1, 2, 3, 4, 5, 6, 7]           # Altitude range, needs to be adjusted before flight
        color = [(0, 0, 255), (0, 85, 255), (0, 104, 255), (0, 108, 214), (0, 108, 152), (0, 106, 92), (0, 104, 42),
                 (0, 100, 0)]
    if sensor is accel:
        col = 7
        sensor = abs(sensor) - 1
        val = [-0.1, 0.25, 0.75, 1, 1.5, 2, 3, 4]  # Vertical acceleration range, only works vertically
        color = [(255, 255, 0), (255, 229, 0), (255, 202, 0), (255, 173, 0), (255, 144, 0), (255, 112, 0), (255, 75, 0),
                 (255, 0, 0)]
    for x in val:
        row = row - 1
        if sensor > x:
            sense.set_pixel(col, row, color[row])
        else:
            sense.set_pixel(col, row, clear)


def check_orient(dir):  # Function to format gyro on LED display
    if dir is orol:
        pos = 5
        for i in range(-4, 4):
            if dir >= (i * 0.7854) and dir < ((i + 1) * 0.7854):
                sense.set_pixel(pos, i + 4, yellow)
            else:
                sense.set_pixel(pos, i + 4, clear)
    elif dir is opit:
        pos = 4
        for i in range(-4, 4):
            # print(i*0.7854/2)
            if dir >= (i * 0.7854 / 2) and dir < ((i + 1) * 0.7854 / 2):
                sense.set_pixel(pos, i + 4, yellow)
            else:
                sense.set_pixel(pos, i + 4, clear)

    elif dir is oyaw:
        pos = 3
        for i in range(-4, 4):
            if dir >= (i * 0.7854) and dir < ((i + 1) * 0.7854):
                sense.set_pixel(pos, i + 4, yellow)
            else:
                sense.set_pixel(pos, i + 4, clear)
    # for i in range(0,8):
    #    if dir >= (i*0.7854) and dir < ((i+1)*0.7854):       # LEDs update depending on orientation, increments of 45 degrees
    #        sense.set_pixel(pos,i,yellow)                    # 45 degrees = 0.7854 rad
    #    else:
    #        sense.set_pixel(pos,i,clear)


def maxmin(var):  # Gathers max/min of variables for Flight Summary
    if var is accel:
        varloc = 0
    if var is temp:
        varloc = 1
    if var is pressure:
        varloc = 2
    if var is humidity:
        varloc = 3
    if var is curalt:
        varloc = 4
    if var is curvelft:
        varloc = 5
    if var is CPUtemp:
        varloc = 6
    if var > maxvar[varloc]:  # Max value calculations
        maxvar[varloc] = var
        maxtime[varloc] = datetime.datetime.now().strftime('%H:%M:%S.%f')
    if var < minvar[varloc]:  # Min value calculations
        minvar[varloc] = var
        mintime[varloc] = datetime.datetime.now().strftime('%H:%M:%S.%f')


def predapgee(startalt, startvel):  # Apogee prediction algorithm   (OUTDATED)
    arr = np.empty((0, 5), int)
    aptime = 0
    rho = rhostart * (0.9 ** (startalt / 1000))  # Current air density, needs to be calculated at higher altitudes
    Fd = 0.5 * rho * Cd * (area * startvel ** 2)  # Drag force, or how much force is exerted by air resistance
    curacc = (-Fd - (mass * 9.8)) / mass  # Total acceleration, drag force + gravity acting downwards
    curvel = startvel + curacc * dt  # New velocity
    curalt = startalt + curvel * dt + 0.5 * curacc * (
                dt ** 2)  # The predicted altitude, or the altitude of the rocket in 'dt' seconds

    arr = np.append(arr, np.array([[curalt, curvel, curacc, Fd, rho]]),
                    axis=0)  # An array to plot results, redundant unless needed for debugging

    lastalt = startalt
    lastvel = curvel

    while curalt > lastalt:  # For every time this function is run, the program plots a flight path based on current altitude and velocity
        lastalt = curalt  # Apogee is predicted when the algorithm detects a drop in altitude in the flight path
        lastvel = curvel
        rho = rhostart * (0.9 ** (lastalt / 1000))
        Fd = 0.5 * rho * Cd * (area * lastvel ** 2)
        curacc = (-Fd - (mass * 9.8)) / mass
        curvel = lastvel + curacc * dt
        curalt = lastalt + curvel * dt + 0.5 * curacc * (dt ** 2)
        arr = np.append(arr, np.array([[curalt, curvel, curacc, Fd, rho]]), axis=0)
        aptime = aptime + dt
    appred = lastalt * 3.28
    return appred, aptime


def numtobin(num):  # Function to convert float variables to binary numbers
    num = abs(num)  # Only prints absolute value of number at the moment to avoid bit issues
    if num % 1 < 0.0001:
        whole = num
        dec = 0
        deccheck = 0
    else:
        whole, dec = str(num).split(".")
        deccheck = 1
    whole = int(whole)
    numdec = num - whole
    decstr = ''
    for i in range(1, 17):  # Convert decimal part of number to binary
        if numdec - 2 ** -i > 0:
            bit = '1'
            numdec -= 2 ** -i
        else:
            bit = '0'
        decstr = decstr + bit
    wholebin = str(bin(whole)[2:].rjust(16, '0'))  # Convert whole part of number to binary
    numbin = wholebin + decstr
    return numbin


def checksum(num1, num2):  # Calculates the checksum byte
    num1 = numtobin(num1)
    num2 = numtobin(num2)
    checkbyt = '00000000'  # checksum is the byte addition of pressure and curalt
    bits = 8  # Both bin numbers are split into 1 byte segments, then those bytes added together
    split1 = [num1[i:i + bits] for i in range(0, len(num1), bits)]
    split2 = [num2[i:i + bits] for i in range(0, len(num2), bits)]
    for i in range(0, len(num1), bits):
        checkbyt = bin(int(checkbyt, 2) + int(split1[int(i / bits)], 2))[2:].rjust(8, '0')
    for i in range(0, len(num2), bits):
        checkbyt = bin(int(checkbyt, 2) + int(split2[int(i / bits)], 2))[2:].rjust(8, '0')
    checkbyt = str(checkbyt)
    if len(checkbyt) > 8:
        checkbyt = checkbyt[(len(checkbyt) - 8):]
    return checkbyt


def beepAlt():
    global deploy_alt
    for i in range(0, deploy_alt, 100):
        GPIO.output(buzzer, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(buzzer, GPIO.LOW)
        sleep(0.5)


"""
    GPIO.output(buzzer,GPIO.HIGH)
    sleep(0.5)
    GPIO.output(buzzer,GPIO.LOW)
    sleep(1)
    GPIO.output(buzzer,GPIO.HIGH)
    sleep(0.5)
    GPIO.output(buzzer,GPIO.LOW)
    sleep(1)
    GPIO.output(buzzer,GPIO.HIGH)
    sleep(0.5)
    GPIO.output(buzzer,GPIO.LOW)
"""
"""
WRITING FORMAT:
'00': Deploying/retracting payload
'01': Code is armed and recording
'10': GoPro2 is active
'11': GoPro3 is active
"""

# NOTE: Replaced by buddy_comm.send()
# def writeComm(num):
#     for i in range(2):
#         if num & 0b10:
#             GPIO.output(dataWrite, GPIO.HIGH)
#             print("high")
#         else:
#             GPIO.output(dataWrite, GPIO.LOW)
#             print("low")
#         num = num << 1
#         GPIO.output(clockWrite, GPIO.HIGH)
#         sleep(0.25)
#         GPIO.output(clockWrite, GPIO.LOW)
#         sleep(0.25)
#
#     GPIO.output(dataWrite, GPIO.LOW)
#     GPIO.output(clockWrite, GPIO.LOW)


"""
READING FORMAT:
'00': SRAD1has detected apogee
'01': Disarm SRAD2
'10': Turn on GoPro2
'11': Turn on GoPro3
"""


# def readComm():
#     global t
#     while True:
#         time_bit = 0
#         num = 0
#         for i in range(2):
#             while GPIO.input(clockRead) == GPIO.LOW:
#                 sleep(0.0001)
#             sleep(0.05)
#             if GPIO.input(dataRead) == GPIO.HIGH:
#                 num = num | 0b1
#             # if i == 0:
#             #     time_bit == time.time()
#             # if i == 1:
#             #     if time.time() - time_bit > 1:
#             #         sleep(0.5)
#             #         i = 3
#             num = num << 1
#             while GPIO.input(clockRead) == GPIO.HIGH:
#                 sleep(0.0001)
#         # print("got a bit: ", num)
#         readnum = num >> 1
#         print(readnum)
#         if readnum is 0:
#             print('deploy')
#             drogueconfirm = True
#         if readnum is 1:
#             print('disarm')
#             # t = 4
#         if readnum is 2:
#             print('gopro2')
#             armCam(2)
#         if readnum is 3:
#             print('gopro3')
#             armCam(3)


def handle_received_buddy_messages():
    global t, drogueconfirm
    if buddy_comm.check_num(0):
        # SRAD 1 thinks we have reached apogee
        print("SRAD 1 thinks we have reached apogee -- deploying drogue")
        drogueconfirm = True
    if buddy_comm.check_num(1):
        # Disarm message
        print("Disarm message received")
        t = 4
    if buddy_comm.check_num(2):
        # Need to turn on GoPro 2
        print("Turning on GoPro 2")
        armCam(2)
    if buddy_comm.check_num(3):
        # Need to turn on GoPro 3
        print("Turning on GoPro 3")
        armCam(3)




def armCam(camval):  # Used to arm cameras 2 and 3
    global cam2
    global cam3
    if camval is 2:
        pinval = cam2
    elif camval is 3:
        pinval = cam3
    else:
        return
    cam = GPIO.PWM(pinval, 50)
    cam.start(2.5)
    sleep(0.25)
    cam.ChangeDutyCycle(12)
    sleep(0.75)
    cam.ChangeDutyCycle(2)
    sleep(0.5)
    cam.stop()
    # buddyWrite.apply_async(writeComm, [camval]) OLD
    buddy_comm.send(camval)


sense.show_message("CRE", text_colour=orange, back_colour=purple)  # Function displays "CRE" on LED screen on start
sleep(0.15)
t = 0
GPIO.output(buzzer, GPIO.HIGH)
wait_screen()  # Display paw print
sleep(5)
GPIO.output(buzzer, GPIO.LOW)
telemcheck = 0
camcheck = 0

motor.set_servo_pulsewidth(motorport, 1500)

# while t is 201:                 # Idles here until trigger activates flight mode
#    for event in sense.stick.get_events():  # Currently waits for joystick to be pressed
#        if event.direction == "down" or event.direction == "right":
#            t = 0
#        elif event.direction == "left":           # Pressing the joystick left activates telemetry
#            telemcheck = 1                        # This feature is put in place in case telemetry is broken/not needed, otherwise the program could break
#            sense.clear(green)                    # The screen flashes green to confirm telemetry is active
#            sleep(0.2)
#        elif event.direction == "up":
#            camcheck = 1
#            sense.clear(cyan)
#            sleep(0.2)
#        else:
#            print("waiting")
#            sleep(0.01)
#    wait_screen()

sense.clear()  # Clear LED display and setup variables
sense.set_imu_config(True, True, True)
sleep(0.25)
trigtime = round(time.time() * 1000)
trigdate = datetime.datetime.now().strftime('%H:%M:%S')
startpressure = sense.get_pressure()  # All these values are used as starting values
starttemp = sense.get_temperature()  # They serve little purpose other than comparing launchsite conditions to the rest of the flight
starthumidity = sense.get_humidity()
starttime = round(time.time() * 1000)
curtime = round(time.time() * 1000)
curtimeap = curtime
apcheck = 0
state = 'launchpad'
timeint = 1000
curvel = 0
curvelft = 0
lastvel = 0
launchdate = 0
launchtime = 0
apdate = 0
apstart = 0
aptime = 0
descentdate = 0
descentstart = 0
descenttime = 0
landdate = 0
maxaccel = 0
minaccel = 0
maxvar = [1, starttemp, startpressure, starthumidity, 0, 0, CPUtemp]
minvar = [1, starttemp, startpressure, starthumidity, 0, 0, CPUtemp]
maxtime = [startdate, startdate, startdate, startdate, startdate, startdate, startdate]
mintime = [startdate, startdate, startdate, startdate, startdate, startdate, startdate]
alt = (288.15 / -0.0065 * (((startpressure / 1013.25) ** 0.1903) - 1))
appred = 0
curaltm = alt
curalt = curaltm * 3.28
aztrue = 1
looptime = round(time.time() * 1000)
strstart = 'CRE'  # Starting string for telemetry, used as sync bytes to confirm the telemetry is working
MFC1 = 0
MFC2 = 0
statebyt = 0
deploycheck = False  # deploycheck becomes True if the requirements to deploy the payload are met
retractcheck = False  # retractcheck becomes True if the requirements to retract the payload are met
drogueconfirm = False  # drogueconfirm checks for if SRAD1 deploys the drogue chute
sradoneap = False
pdtime = 0
prtime = 0
i = 0
deploy_alt = 1000  # Main chute deployment altitude
retractstart = round(time.time() * 1000)
deploystart = round(time.time() * 1000)
if telemcheck == 1:  # Modem port via USB, disabled by default but enabled by pressing the joystick left in idle
    ser = serial.Serial("/dev/ttyUSB0", baudrate=57600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS, timeout=0)

# buddyRead = threading.Thread(target=readComm)
# buddyRead.start()
# buddyWrite = Pool(processes=1)
# buddyWrite.apply_async(writeComm, [1])
buddy_comm.send(1)
beep = Pool(processes=1)
beep.apply_async(beepAlt)

while t is 0:  # Flight mode loop, all important stuff done here
    for event in sense.stick.get_events():  # Trigger to manually end flight mode
        if event.action == "pressed":  # Activate by pressing joystick
            t = 3
        else:
            sleep(0.01)



    sense.set_pixel(0, 0, red)  # Gather all basic sensor data
    date = datetime.datetime.now().strftime('%H:%M:%S.%f')
    pressure = sense.get_pressure()  # measured in mbar/hPa
    temp = sense.get_temperature()  # measured in celsius, gets residual heat from the CPU
    humidity = sense.get_humidity()  # measured in %
    sense.set_pixel(0, 1, red)  # Gather complex accel/gyro data
    acceleration = sense.get_accelerometer_raw()
    az = -acceleration['x']  # 'x' is a line running from usb ports to sd card, long-ways on the pi
    ay = acceleration['y']  # 'y' is a line running from GPIO to hdmi port, short-ways on the pi
    ax = acceleration['z']  # 'z' is a line running up and down on the pi, perpendicular to the board
    accel = math.sqrt(ax ** 2 + ay ** 2 + az ** 2)
    orient = sense.get_orientation_radians()
    opit = orient['pitch']  # pitch orientation (0-90, 180-270, rotation around y-axis)
    orol = orient['roll']  # roll orientation (0-360, rotation around x-axis)
    oyaw = orient['yaw']  # yaw orientation (0-360, rotation around z-axis)
    gyro = sense.get_gyroscope_raw()
    vrol = gyro['x']  # roll velocity, radial velocity around x-axis
    vpit = gyro['y']  # pitch velocity, radial velocity around y-axis
    vyaw = gyro['z']  # yaw velocity, radial velocity around z-axis

    # axtrue = ax*(cos(oyaw)*cos(opit)) + ay*(cos(oyaw)*sin(opit)*sin(orol)-sin(oyaw)*cos(orol)) + az*(cos(oyaw)*sin(opit)*cos(orol)+sin(oyaw)*sin(opit))
    # aytrue = ax*(sin(oyaw)*cos(opit)) + ay*(sin(oyaw)*sin(opit)*sin(orol)+cos(oyaw)*cos(orol)) + az*(sin(oyaw)*sin(opit)*cos(orol)-cos(orol)*sin(opit))
    # aztrue = -ax*sin(opit) + ay*cos(opit)*sin(orol) + az*cos(opit)*cos(orol)

    # axtrue = round(axtrue, 2)
    # aytrue = round(aytrue, 2)
    # aztrue = round(aztrue, 2)

    azvect = az * sin(opit) + ay * cos(opit) * sin(orol) + ax * cos(opit) * cos(
        orol)  # True vertical acceleration, ignores rocket orientation
    # print(azvect)

    # print(accel)

    sense.set_pixel(0, 2, red)  # Calculate altitude/predict apogee
    lastalt = curaltm
    lastvel = curvel
    lasttime = looptime
    looptime = round(time.time() * 1000)
    timedif = (looptime - lasttime) / 1000
    if state is 'launchpad':
        alt = (288.15 / -0.0065 * (
                    ((pressure / 1013.25) ** 0.1903) - 1))  # Base altitude, or whatever altitude the rocket starts at
        curvel = 0  # Base altitude constantly adjusted at launchpad to prevent drift in readings
    curaltm = (288.15 / -0.0065 * (
                ((pressure / 1013.25) ** 0.1903) - 1)) - alt  # Current altitude relative to launchpad
    curalt = curaltm * 3.28
    apaz = (azvect - 1) * 9.81  # True vertical acceleration, removes normal force from accelerometer
    # if apaz < 0.01 or apaz > -0.01:
    #    apaz = 0
    curvel = apaz * timedif + lastvel  # Calculates the vertical velocity, converts to ft
    curvel = round(curvel, 2)
    curvelft = curvel * 3.28
    curvelft = round(curvelft, 2)
    if state is 'launchpad' or state is 'landed':  # Forces current velocity to 0 if the rocket is at a state where motion is not expected
        curvel = 0  # This will likely need some tweaking, the purpose is to prevent velocity readings from drifting when there's no motion (landing for example)
    # appred, apptime = predapgee(curaltm,curvel)                                      # Sends current altitude and velocity to predict apogee (OUTDATED)
    appred = ((mass / (2 * k)) * np.log((mass * 9.81 + k * (curvel ** 2)) / (
                mass * 9.81)) + curaltm) * 3.28  # Apogee prediction formula, pretty accurate

    velcheck = (curaltm - lastalt) * 3.28 / timedif

    sense.set_pixel(0, 3, red)  # Send telemetry, round all values

    # print(apaz)

    # Telemetry runs regardless of it being enabled, but data will only be transmitted if enabled
    # Telemetry data will be printed onto a text file in case it's disabled
    telem_data = [bin(ord(c))[2:].rjust(8, '0') for c in strstart]
    for c in range(0, 8):
        telem_data.append('0')
    numbin = bin(MFC1)[2:].rjust(8, '0')  # Counters to determine how many loops have passed
    telem_data.insert(3, numbin)  # A total of 65535 loops can be run in the program
    telem_data.pop(4)  # This is almost 2 hours of runtime
    numbin = bin(MFC2)[2:].rjust(8,
                                 '0')  # This will only be maxxed if the rocket idles on the launchpad for over 100 minutes
    telem_data.insert(4, numbin)  # If maxxed out, the timer resets
    telem_data.pop(5)
    MFC1 += 1
    if MFC1 == 256:
        MFC2 += 1
        MFC1 = 0
    if MFC2 == 256:
        MFC2 = 0
        MFC1 = 0
    statestr = bin(statebyt)[2:].rjust(8,
                                       '0')  # Instead of the state string, a byte will be used to communicate rocket's state
    telem_data.insert(5, statestr)  # '0' for launchpad, '1' for launch, '2' for apogee, '3' for descent, '4' for landed
    telem_data.pop(6)
    data = [appred, accel, temp, pressure, curalt]  # Data that's being transmitted
    for c in range(0, 5):  # All of these variables are converted to 4-byte binary
        numbin = numtobin(data[c])
        telem_data.insert(c + 6, numbin)
        telem_data.pop(c + 7)
    telem_data.insert(11, checksum(curalt,
                                   pressure))  # checksum adds bytes of pressure and curalt to check if data is correct
    telemstr = ''.join(telem_data)  # This is the final string being transmitted
    with open(loc + "Telemetry {}.txt".format(startdate), "a") as file5:  # Print telemetry data to a file
        file5.write("{}".format(telemstr))
    if telemcheck == 1:
        ser.write(telemstr)
    # print(telem_data)

    accel = round(accel, 3)  # Rounding all variables, placed after the telemetry for precision
    temp = round(temp, 2)
    pressure = round(pressure, 3)
    humidity = round(humidity, 2)
    ax = round(ax, 3)
    ay = round(ay, 3)
    az = round(az, 3)
    vrol = round(vrol, 3)
    vpit = round(vpit, 3)
    vyaw = round(vyaw, 3)
    orol = round(orol, 2)
    opit = round(opit, 2)
    oyaw = round(oyaw, 2)
    curalt = round(curalt, 2)
    curvel = round(curvel, 3)
    appred = round(appred, 2)
    azvect = round(azvect, 2)
    apaz = round(apaz, 3)
    timedif = round(timedif, 5)
    sense.set_pixel(1, 7, clear)  # Clears transmission LED, can go anywhere

    # print(axtrue, aytrue, aztrue)

    sense.set_pixel(0, 4, red)  # Functions to update LED display

    check_orient(orol)  # check_orient() displays a single LED based on the orientation of each axis
    check_orient(opit)
    check_orient(oyaw)
    indicator(temp)  # indicator() displays its values on a range, filling a bar as the value increases
    indicator(curalt)
    indicator(accel)

    sense.set_pixel(0, 5, red)  # Update flight states
    if state is 'launchpad':  # Rocket on launchpad
        sense.set_pixel(1, 0, (0, 255, 255))
        timeint = 5000  # Printing interval on launchpad, set to 5 seconds
        padtime = (curtime - trigtime) / 1000  # Time rocket is on pad
        launchstart = curtime  # Time of launch, constantly updated until launch is detected
        statebyt = 0
        if az > 1.5:  # az needs to detect over 1.5 gees, only possible if the pi were to accelerate upwards
            state = 'launch'
            launchdate = datetime.datetime.now().strftime('%H:%M:%S')
            launchstart = round(time.time() * 1000)
            if camcheck is 1:
                camera = PiCamera()  # Camera begins recorded at the start of launch
                camera.rotation = 180
                camera.start_recording(loc + 'video{}.h264'.format(startdate))  # Uncomment if cam used
    if state is 'launch':  # Climbing altitude
        sense.set_pixel(1, 1, (0, 255, 255))
        timeint = 125  # Printing interval during flight, set to 0.25 seconds
        launchtime = (curtime - launchstart) / 1000  # Time in 'launch' state
        statebyt = 1
        if curaltm < lastalt:  # Check if altitude drops
            apcheck = apcheck + 1
        else:
            apcheck = 0
        if apcheck > 5:  # Needs 5 consecutive drops in altitude to switch states
            state = 'apogee'
            apdate = datetime.datetime.now().strftime('%H:%M:%S')  # Time apogee is hit
            apstart = round(time.time() * 1000)
            # drogueconfirm = True
    if state is 'apogee':  # Beginning descent, drogue deployed
        sense.set_pixel(1, 2, (0, 255, 255))
        aptime = (curtime - apstart) / 1000  # Time between drogue deployment and main deployment
        statebyt = 2
        if drogueconfirm is False and curalt <= 2500 and curalt > 1000 and i is 0:
            drogueconfirm = True
        if i is 0 and drogueconfirm is True and abs(velcheck) <= 124:  # Preliminary deployment code
            deploycheck = True
        if i is 2 and deploytimer > 15500:  # Prerequisites to retract the payload, has to be in descent state and extended for at least 10 seconds
            retractcheck = True
        print(i, drogueconfirm, curalt, abs(velcheck))
        # if drogueconfirm is False and curalt <=2500 and curalt > 2000 and i is 0:
        #    drogueconfirm = True
        if curalt <= deploy_alt and curtime - apstart > 20000:  # Altitude at which main chute deploys
            state = 'descent'
            startimer = round(time.time() * 1000)  # Descent timer
            curtimer = round(time.time() * 1000)
            descentdate = datetime.datetime.now().strftime('%H:%M:%S')  # Time main chute deploys
            descentstart = round(time.time() * 1000)
    if state is 'descent':  # Main chute deployed
        sense.set_pixel(1, 3, (0, 255, 255))
        descenttime = (curtime - descentstart) / 1000  # Time between main chute and landing
        statebyt = 3
        if curalt < 100 and azvect < 1.1:  # Altitude needs to be less than 100ft above launchsite and standard vertical acceleration sustained
            # print(curtimer-startimer)
            if curtimer - startimer > 20000:  # 20 second timer placed in case of false positive, IREC descent at least 20 seconds after main chute
                state = 'landed'  # It's likely the sensors will think the landing has been reached prior to the actual touchdown
                landdate = datetime.datetime.now().strftime(
                    '%H:%M:%S')  # The timer means that if any vertical force acts upon the rocket (touchdown will do this),
                startimer = round(
                    time.time() * 1000)  # the timer will reset to ensure the rocket is landed and not slowly descending, steady descent means near 0 acceleration, same as landed
                curtimer = round(time.time() * 1000)
                print(curtimer - startimer)
            else:
                curtimer = round(time.time() * 1000)
        else:
            startimer = round(time.time() * 1000)  # Timer resets if azvect > 1.1 or curalt > 100
            curtimer = round(time.time() * 1000)
    if state is 'landed':  # Touchdown
        sense.set_pixel(1, 4, (0, 255, 255))
        curtimer = round(time.time() * 1000)  # No timestamps here, landing will always last for 15 seconds
        statebyt = 4  # Once in landed state, the program moves to completion and can't be brought back to flight mode
        timeint = 1000  # Printing interval once landed, set to 1 second
        if curtimer - startimer > 15000:  # Idling for 15 seconds in this state ends the program
            t = 1

    sense.set_pixel(0, 6, red)  # Code to print to text files on regular intervals
    curtime = round(time.time() * 1000)
    if curtime - starttime >= timeint:  # Checks if time passed is greater than set interval
        starttime = curtime
        sense.set_pixel(1, 7, blue)
        with open(loc + "Basic {}.txt".format(startdate), "a") as file:  # Raw sensor data, altitude, and current state
            file.write(
                "{0} {1} {2} {3} {4} {5} {6} {7}\n".format(date, temp, CPUtemp, pressure, humidity, accel, curalt,
                                                           state))
        with open(loc + "Complex {}.txt".format(startdate),
                  "a") as file2:  # 9-axis accelerometer data, state, and velocity
            file2.write(
                "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10}\n".format(date, ax, ay, az, opit, orol, oyaw, vpit, vrol,
                                                                        vyaw, state))
    if state is not 'launchpad' and state is not 'landed':
        with open(loc + "Alt {}.txt".format(startdate), "a") as file3:  # Data used in apogee prediction
            file3.write("{0} {1} {2} {3} {4} {5} {6}\n".format(date, timedif, curalt, apaz, curvelft, appred, state))

    sense.set_pixel(0, 7, red)  # Update max/mins of values for Flight Summary
    maxmin(accel)
    maxmin(temp)
    maxmin(pressure)
    maxmin(humidity)
    maxmin(curalt)
    maxmin(curvelft)

    # Checking CPU temp for if we need any heatsinks or cooling, must stay below 80C
    CPUtemp = cpu.temperature
    maxmin(CPUtemp)

    if drogueconfirm is True:  # State changes to 'apogee' if the SRAD1 deploys the drogue before SRAD2 detects apogee
        if state is 'launch':
            sradoneap = True  # How the program knows if state change was due to SRAD1, for post-flight analysis
        state = 'apogee'

    if deploycheck is True:  # Code to deploy payload
        if i == 0:
            print("deploy")
            i = 1
            drogueconfirm = False
            # buddyWrite.apply_async(writeComm, [0])
            buddy_comm.send(0)

            pdtime = datetime.datetime.now().strftime('%H:%M:%S')
        print(deploytimer, "deploy")
        sense.set_pixel(1, 6, (255, 255, 255))  # Pixel near bottom left lights white when payload is deployed
        if deploytimer > 5000 and deploytimer < 5500:
            print("Deploying")
            motor.set_servo_pulsewidth(motorport, 1400)
        if deploytimer > 5500:
            deploycheck = False
            i = 2
    elif retractcheck is True:  # Code to retract payload
        if i == 2:
            # print("retract")
            prtime = datetime.datetime.now().strftime('%H:%M:%S')
            i = 1
        print(retracttimer, "retracting")
        motor.set_servo_pulsewidth(motorport, 1600)
        if retracttimer > 500:
            retractcheck = False
            # buddyWrite.apply_async(writeComm, [0])
            buddy_comm.send(0)
            i = 3
            sense.set_pixel(1, 6, (0, 0, 0))  # light turns off upon retraction
    else:
        motor.set_servo_pulsewidth(motorport, 1500)
        if i == 0:
            deploystart = round(time.time() * 1000)
        if i == 2:
            retractstart = round(time.time() * 1000)
    deploytimer = round(time.time() * 1000) - deploystart
    retracttimer = round(time.time() * 1000) - retractstart
    # print(retracttimer)
    # print(motor.get_servo_pulsewidth(motorport))
    for x in range(0, 8):  # Clear column 1 on LED display
        sense.set_pixel(0, x, clear)

    if curtime - launchstart > 600000:  # Timer to end program if it runs for too long, set to 10 mins
        t = 2  # Only 10 minutes after launch ends the program, time on launchpad isn't accounted for
        # The rocket could sit on the launchpad forever and record data
    # print(oyaw*180/3.1415)

    # Final roundings and calculations
alt = alt * 3.28  # Base altitude
alt = round(alt, 2)
starttemp = round(starttemp, 2)  # Starting temperature
starthumidity = round(starthumidity, 2)  # Starting humidity
startpressure = round(startpressure, 3)  # Starting pressure
curtime = round(time.time() * 1000)
progtime = (curtime - inittime) / 1000  # Time spent in entire program
looptime = (curtime - trigtime) / 1000  # Time spent in flight mode
endtime = datetime.datetime.now().strftime('%H:%M:%S')  # Time of program end
if camcheck is 1:
    camera.stop_recording()  # Camera stops recording once program begins to end
    sense.clear(cyan)
    sleep(0.2)

# Loop started
# Basic data gathered
# Complex data gathered
# Altitude calculated
# Telemetry sent & values rounded
# Indicators updated
# Rocket state checked
# Data record checked

file4 = open(loc + "Flight Summary {}.txt".format(startdate), "w")  # All stuff to be written onto Flight Summary file
file4.write("Flight summary {}\n\n".format(startdate))  # Displays the date/time the program started to help identify it
file4.write("Program runtime: {}s\n".format(progtime))  # Total time the program ran, from start to now
file4.write("Trigger time: {}\n".format(trigdate))  # Time the program ended idle mode, entered flight mode
file4.write("Flight mode runtime: {}s\n".format(
    looptime))  # Time the program was in flight mode, from time on launchpad to landing
file4.write("Time on launchpad: {}s\n".format(padtime))  # Time rocket spent on the launchpad
file4.write("Temperature at launchpad: {}C.\n".format(starttemp))  # Recorded temperature at the launchpad
file4.write("Humidity at launchpad: {}%.\n".format(starthumidity))  # Recorded humidity at the launchpad
file4.write("Pressure at launchpad: {}hPa.\n".format(startpressure))  # Recorded pressure at the launchpad
file4.write("Rocket launched from altitude of approx {}ft.\n".format(
    alt))  # Suspected altitude at the launchpad, likely not true altitude due to weather
file4.write("Launch time: {}\n".format(launchdate))  # Time of launch
file4.write("Time of ascent: {}s\n".format(launchtime))  # Time rocket spent in 'launch' state
if sradoneap is True:
    file4.write(
        "Apogee detected by SRAD 1 first.\n")  # Writes if SRAD1 detects apogee and deploys the drogue before SRAD2 detects apogee
else:
    file4.write("Apogee detected by SRAD 2 first.\n")  # Writes if SRAD2 detects apogee before SRAD1 does
file4.write("Time at apogee: {}\n".format(apdate))  # Time rocket switched to 'apogee' state
file4.write("Payload deploy time: {}\n".format(pdtime))  # Time payload deployed (occurs after drogue is deployed)
file4.write("Payload retract time: {}\n".format(
    prtime))  # Time payload retracted (occurs when altitude is less than 5000ft and 12s have passed since deployment)
file4.write("Time with droge deployed: {}s\n".format(aptime))  # Time rocket spent in 'apogee' state
file4.write("Time main chute deployed: {}\n".format(descentdate))  # Time rocket switched to 'descent' state
file4.write("Time of descent: {}s\n".format(descenttime))  # Time rocket spent in 'descent' state
file4.write("Touchdown time: {}\n".format(landdate))  # Time rocket switched to 'landed' state
file4.write("Program end: {}\n\n".format(
    endtime))  # Time that the rocket exited flight mode, will always be a set time after touchdown time
file4.write("Acceleration:   max: {0}g at {1}\n".format(maxvar[0], maxtime[0]))
file4.write("                 min: {0}g at {1}\n".format(minvar[0], mintime[0]))  # Max/min acceleration on all axes
file4.write("Temperature:    max: {0}C at {1}\n".format(maxvar[1], maxtime[1]))
file4.write(
    "                 min: {0}C at {1}\n".format(minvar[1], mintime[1]))  # Max/min temperature inside the rocket
file4.write("Pressure:       max: {0}hPa at {1}\n".format(maxvar[2], maxtime[2]))
file4.write("                 min: {0}hPa at {1}\n".format(minvar[2], mintime[2]))  # Max/min pressure inside the rocket
file4.write("Humidity:       max: {0}% at {1}\n".format(maxvar[3], maxtime[3]))
file4.write("                 min: {0}% at {1}\n".format(minvar[3], mintime[3]))  # Max/min humidity inside the rocket
file4.write("Altitude:       max: {0}ft at {1}\n".format(maxvar[4], maxtime[4]))  # Max altitude, the apogee
file4.write("Velocity:       max: {0}ft/s at {1}\n".format(maxvar[5], maxtime[5]))  # Max calculated velocity
file4.write("CPU Temp:       max: {0}C at {1}\n".format(maxvar[6], maxtime[6]))
file4.write("                 min: {0}C at {1}\n".format(minvar[6], mintime[
    6]))  # Max/min CPU temperature, needs to be examined for any need of ventilation
file4.write("\n1g is normal acceleration. 1013.25hPa is standard pressure at sea level.\n")
file4.write("Humidity is normally above 50% in Clemson, 10-40% at Spaceport America.\n")
file4.write("Humidity indoors is typically about 40%.\n")
file4.write("Temperature of the pi indoors is typically 25-30C (77-86F).\n\n")
file4.write("Note: CPU temperature must stay below 85C. If max temperature is above 80C, cooling is needed urgently.\n")
file4.write("Note: Typical CPU temperature when indoors is 40-50C.\n")
file4.write(
    "Note: Recorded temperature is not the true air temperature. Residual heat from the pi raises the readings by a few degeres.\n")
file4.write(
    "Note: Calculated altitude at launchpad may not be true altitude relative to sea level. Altitude is calculated from pressure, so weather can cause it to be over 100ft off.\n")
file4.write(
    "Note: Recorded acceleration might not be true acceleration. Normal force from the rocket is not included in these readings.\n")
if t is 1:  # Prints to Flight Summary file how the program ended
    file4.write(
        "\nSuccessful flight code run.\n")  # Flight mode ran successfully, all states activated and program sat in 'landed' state for set amount of time
elif t is 2:
    file4.write(
        "\nFlight mode engaged for more than 10 minutes. Program was aborted.\n")  # Flight timer ran out and ended the program manually
elif t is 3:
    file4.write(
        "\nFlight code aborted manually.\n")  # Program ended by user, either by pressing the joystick or sending an abort signal
elif t is 4:
    file4.write("\nSRAD2 was disarmed via telemetry.\n")
else:
    file4.write("\nUnexpected closure of program. Needs troubleshooting.\n")

sense.clear()  # Clears sensor and closes all files
file.close()
file2.close()
file3.close()
file4.close()
file5.close()
GPIO.cleanup()
print("end")

sense.set_pixel(0, 0, green)

sleep(1)  # Shuts down the pi at the end of the program to preserve files before battery loss
# call("sudo shutdown -h now",shell=True)                     # uncomment before flight
