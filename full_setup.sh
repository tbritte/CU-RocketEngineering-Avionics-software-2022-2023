# Downloads all the packages that are needed for the pi to run successfully
sudo apt-get install libatlas-base-dev  # Required for numpy to work on a Raspberry Pi

pip3 install setuptools
pip3 install numpy==1.23.5
pip3 install pandas

# Getting sensors
pip3 install Adafruit-BMP  # Altitude sensor
pip3 install adafruit-circuitpython-bno08x  # Alternative IMU

# Lis3mdl + lsm6ds33 IMU
pip3 install adafruit-circuitpython-lis3mdl
pip3 install adafruit-circuitpython-lsm6ds




