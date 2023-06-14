# Code to activate SRAD 1
cd /home/curocket/CU-RocketEngineering-Avionics-software-2022-2023/flight_controller

# Because it is executed with sudo, the packages must be installed at root
sudo -u curocket python3 -m flight_control.flight_controller.py