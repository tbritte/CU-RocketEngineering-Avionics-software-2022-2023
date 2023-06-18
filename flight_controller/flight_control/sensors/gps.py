from .sensor import Sensor
import serial
import time

class GPS(Sensor):
    def __init__(self):
        self.sensor_name = "GPS"
        self.gps = None
        super().__init__(self.sensor_name)


    def setup(self):
        try:
            self.gps = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0)
            self.gps_buffer = ""
            self.functional = True
            print("     GPS setup successful")
        except serial.SerialException:
            print("     GPS not found, check wiring")
            self.gps = None
            return
        except FileNotFoundError:
            print("     GPS not found, check wiring")
            self.gps = None
            return
        except Exception as e:
            print("     GPS not found, check wiring unknown error below")
            print(e)
            self.gps = None
            return


    def find_gpgga_in_buffer(self):
        """
        Finds the GPGGA message in the buffer and returns the index of the start of the message
        If it can't find the message, it returns None
        Gives the most recent complete (has a '\n') GPGGA message in the buffer
        :return: Index of the start of the GPGGA message or None
        """
        for i in range(len(self.gps_buffer)):
            spot = len(self.gps_buffer) - i - 6
            # looking for the start of the GPGGA message
            if self.gps_buffer[spot:spot + 6] == "$GPGGA":
                # print("Found GPGGA message:", spot)
                # Checking if there is a newline after the message
                for j in range(spot, len(self.gps_buffer)):
                    if self.gps_buffer[j] == "\n":
                        # print("Found newline after GPGGA message:", j)
                        return spot

    def get_new_data(self):
        # print("Getting GPS data...")
        try:
            self.gps_buffer += self.gps.readline().decode("utf-8")
            if len(self.gps_buffer) > 10000:  # 10000 character limit on buffer, it's arbitrary
                self.gps_buffer = self.gps_buffer[-10000:]
        except UnicodeDecodeError:
            pass
        except:
            pass

        # print("GPSvim  Buffer: " + self.gps_buffer)

        #  Looking through the newest date in the buffer for the GPGGA message
        #  This is the message that contains the GPS data

        spot = self.find_gpgga_in_buffer()

        if spot is not None:
            message = ""
            # Iterating from spot till newline and putting that in the message
            for i in range(spot, len(self.gps_buffer)):
                if self.gps_buffer[i] == "\n":
                    break
                message += self.gps_buffer[i]

            parts = message.split(",")
            try:
                try:
                    utc_time = parts[1]  # hhmmss.sss format (UTC)
                    longitude = float(parts[4])
                    latitude = float(parts[2])
                    alt = float(parts[9])
                    quality = parts[6]
                    sat_num = parts[7]

                    # Using the good data
                    real_data = [longitude, latitude, alt, quality, sat_num, utc_time]
                    return real_data

                except ValueError:
                    # Occurs when the GPS is not getting a signal
                    # Updating the old_time if that is there
                    # if len(utc_time) > 2:
                    #     self.old_gps_data[5] = utc_time
                    pass

            except IndexError:
                print("    Index Error, parts were: " + str(parts), "\n    Data was: " + str(message))
                print("Next line would be: " + self.gps.readline().decode("utf-8"))
                pass
            except TypeError:
                print("    Type Error, parts were: " + str(parts), "\n    Data was: " + str(message))
                print("Next line would be: " + self.gps.readline().decode("utf-8"))
                pass
            except Exception as e:
                print("    Exception: " + str(e))
                print("    parts were: " + str(parts), "\n    Data was: " + str(message))
                print("Next line would be: " + self.gps.readline().decode("utf-8"))
                pass