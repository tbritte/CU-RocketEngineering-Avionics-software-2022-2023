import serial
from time import sleep
from sense_hat import SenseHat
import datetime

def numtobin(num,bytesize):                    # Function to convert float variables to binary numbers
    num = abs(num)                    # Only prints absolute value of number at the moment to avoid bit issues
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
    for i in range(1, bytesize*4+1):                           # Convert decimal part of number to binary
        if numdec - 2**-i > 0:
            bit = '1'
            numdec -= 2**-i
        else:
            bit = '0'
        decstr = decstr + bit
    wholebin = str(bin(whole)[2:].rjust(bytesize*4,'0'))     # Convert whole part of number to binary
    numbin = wholebin + decstr
    return numbin

def checksum(checkbytes):
    checkbyt = '00000000'                             # checksum is the byte addition of pressure and curalt
    bits = 8                                          # Both bin numbers are split into 1 byte segments, then those bytes added together
    split = [checkbytes[i:i + bits] for i in range(0, len(checkbytes), bits)]
    for i in range(0, len(checkbytes), bits):
        checkbyt = bin(int(checkbyt, 2) + int(split[int(i/bits)],2))[2:].rjust(8,'0')
    checkbyt = str(checkbyt)
    if len(checkbyt) > 8:
        checkbyt = checkbyt[(len(checkbyt)-8):]
    return checkbyt

orange = (245, 102, 0)
purple = (82, 45, 128)

sense.show_message("CRE",text_colour=orange,back_colour=purple)     # Function displays "CRE" on LED screen on start
sleep(0.15)

date = datetime.datetime.now().strftime("%H%M%S%f")[0:10]

ser = serial.Serial("/dev/ttyUSB0",baudrate=57600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=0)
sense.clear()

syncstr = 'CRE'
system = 1
MFC1 = 0
MFC2 = 0

status = 5
gpslat = 34.683437
gpslon = 82.837364
gpsalt = 725

pressure = sense.get_pressure() # measured in mbar/hPa

alt = (288.15/-0.0065 * (((pressure/1013.25)**0.1903)-1))*3.28

t = 0

print("Running.")

while t is 0:
    for event in sense.stick.get_events():  # Trigger to manually end flight mode
        if event.action == "pressed":       # Activate by pressing joystick
            t = 3
        else:
            sleep(0.01)
    curalt = 3.28*(288.15/-0.0065 * (((pressure/1013.25)**0.1903)-1)) - alt
    acceleration = sense.get_accelerometer_raw()
    az = -acceleration['x'] # 'x' is a line running from usb ports to sd card, long-ways on the pi
    ay = acceleration['y'] # 'y' is a line running from GPIO to hdmi port, short-ways on the pi
    ax = acceleration['z'] # 'z' is a line running up and down on the pi, perpendicular to the board
    accel = math.sqrt(ax**2 + ay**2 + az**2)
    orient = sense.get_orientation_radians()
    opit = orient['pitch'] # pitch orientation (0-90, 180-270, rotation around y-axis)
    orol = orient['roll'] # roll orientation (0-360, rotation around x-axis)
    oyaw = orient['yaw'] # yaw orientation (0-360, rotation around z-axis)
    gyro = sense.get_gyroscope_raw()
    vrol = gyro['x'] # roll velocity, radial velocity around x-axis
    vpit = gyro['y'] # pitch velocity, radial velocity around y-axis
    vyaw = gyro['z'] # yaw velocity, radial velocity around z-axis
    pressure = sense.get_pressure() # measured in mbar/hPa
    temp = sense.get_temperature() # measured in celsius, gets residual heat from the CPU
    humidity = sense.get_humidity() # measured in %

    telem_data = [bin(ord(c))[2:].rjust(8,'0') for c in syncstr]
    sync3 = bin(system)[2:].rjust(8,'0')
    telem_data.append(sync3)
    
    numbin = bin(MFC1)[2:].rjust(16,'0')
    telem_data.append(numbin)
    numbin = bin(MFC2)[2:].rjust(16,'0')
    telem_data.append(numbin)
    MFC1 += 1
    if MFC1 == 65536:
        MFC2 += 1
        MFC1 = 0
    if MFC2 == 65536:
        MFC2 = 0
        MFC1 = 0
    
    data = [curalt, az, ay, ax, vyaw, vpit, vrol, oyaw, opit, orol, temp, appred, humidity, gpslat, gpslon, gpsalt]
    for c in range(0,len(data)):
        numbin = numtobin(data[c],4)
        telem_data.append(numbin)
        
    curdate = datetime.datetime.now().strftime("%H%M%S%f")[0:10]
    curdate = int(curdate)
    numbin = bin(curdate)[2:].rjust(32,'0')
    telem_data.append(numbin)
    
    numbin = bin(status)[2:].rjust(16,'0')
    telem_data.append(numbin)
    
    precheck = ''.join(telem_data)
    checkbytes = precheck[64:248]
    numbin = checksum(checkbytes)
    telem_data.append(numbin)
    
    telemstr = ''.join(telem_data)
    #print(telemstr)
    ser.write(telemstr)
    sleep(0.1)

sense.show_message("END",text_colour=orange,back_colour=purple)




# TM FORMATTING:
# sync0 sync1 sync2 --> 'C' 'R' 'E' in bin
# sync3 --> '1' or '2' for whatever system is in use
# MFC1 MFC2 --> 0-32767, counts up by 1 every time
# altitude az ay ax gz gy gx mz my mx temp appred humidity --> all sensor data, use oyaw/vyaw instead of gz/mz, all values 4 bytes each
# GPS latitude longitude altitude --> use placeholder numbers, 4 bytes each
# curtime --> current time as HH:MM:SS.sss expressed as integer, i.e. 09:37:56.345 = 093756345
# Status --> placeholder for now, 2 byte integer
# checksum --> sum of bytes 8-30