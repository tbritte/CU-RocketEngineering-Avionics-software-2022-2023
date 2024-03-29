import RPi.GPIO as GPIO
import time
from threading import Thread

DATA_PIN_TO_SRAD2 = 23
CLOCK_PIN_TO_SRAD2 = 24

DATA_PIN_FROM_SRAD2 = 8
CLOCK_PIN_FROM_SRAD2 = 7

class BuddyCommSystem:
    def __init__(self):
        self.writer = BuddyCommWriterThread()
        self.reader = BuddyCommReaderThread()

        self.writer.start()
        self.reader.start()

    def get_messages(self):
        return self.reader.messages

    def has_sent(self, num):
        return self.writer.has_sent(num)

    def send(self, num):
        self.writer.send(num)


class BuddyComm:
    """
    Handles communication with SRAD 2
    """

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # Setting up all the pins
        GPIO.setup(DATA_PIN_TO_SRAD2, GPIO.OUT)
        GPIO.setup(CLOCK_PIN_TO_SRAD2, GPIO.OUT)

        GPIO.setup(DATA_PIN_FROM_SRAD2, GPIO.IN)
        GPIO.setup(CLOCK_PIN_FROM_SRAD2, GPIO.IN)

        self.sents = []

    def get_has_sent(self, val):
        return val in self.sents

    def send(self, num):
        """
        nums:
        00 - apogee
        01 - disarm
        10 - turn on gopro 2
        11 - turn on gopro 3
        """
        print("Sending " + str(num) + " to SRAD2")
        if num not in self.sents:
            self.sents.append(num)  # Keeping track of which nums have been sent at least once

        # Sending the number
        for i in range(2):
            if num & 0b10:  # Checking if the first bit is a 1
                GPIO.output(DATA_PIN_TO_SRAD2, GPIO.HIGH)
            else:
                GPIO.output(DATA_PIN_TO_SRAD2, GPIO.LOW)
            num = num << 1  # Shifting the number to the left by 1 bit
            time.sleep(.01)
            GPIO.output(CLOCK_PIN_TO_SRAD2, GPIO.HIGH)
            time.sleep(0.25)
            GPIO.output(CLOCK_PIN_TO_SRAD2, GPIO.LOW)
            time.sleep(0.25)

        # End signal
        GPIO.output(DATA_PIN_TO_SRAD2, GPIO.LOW)
        GPIO.output(CLOCK_PIN_TO_SRAD2, GPIO.LOW)

    @staticmethod
    def receive():
        """
        Returns the number received, should be ran in a seperate thread
        """
        try:
            # Receiving the number
            # If the clock pin is high, then the data pin will be the number received
            # Looking for two bits of data
            time_of_getting_first_bit = 0
            num = 0
            for i in range(2):
                while GPIO.input(CLOCK_PIN_FROM_SRAD2) == GPIO.LOW:  # Waiting for the clock pin to go high
                    pass
                # print("(Buddy Comm) clock is high waiting .1 seconds to see if it stays high")
                time.sleep(.1)
                if GPIO.input(CLOCK_PIN_FROM_SRAD2) == GPIO.LOW:
                    # print("\n(Buddy Comm) clock went low too quickly\n")
                    return -1
                if GPIO.input(DATA_PIN_FROM_SRAD2) == GPIO.HIGH:  # Checking if the data pin is high
                    num = num | 0b1  # Setting the last bit to 1
                if i == 0:
                    time_of_getting_first_bit = time.time()
                if i == 1:
                    if time.time() - time_of_getting_first_bit > 1:
                        print("Too much time between bits")
                        time.sleep(.5)
                        return -1
                    if time.time() - time_of_getting_first_bit < .2:
                        # print("(Buddy Comm) TIME BETWEEN BITS: ", time.time() - time_of_getting_first_bit)
                        # print("(Buddy Comm) Too little time between bits")
                        time.sleep(.5)
                        return -1
                    pass
                num = num << 1  # Shifting the number to the left by 1 bit
                while GPIO.input(CLOCK_PIN_FROM_SRAD2) == GPIO.HIGH:  # Waiting for the clock pin to go low
                    pass
                print("clock is low")
            return num >> 1  # Shifting the number to the right by 1 bit to get rid of the extra bit
        except Exception as e:
            print("Buddy Read Error: " + str(e))
            return -1


# custom thread
class BuddyCommReaderThread(Thread):
    # constructor
    def __init__(self):
        # execute the base constructor
        Thread.__init__(self)
        self.messages = []

    def get_oldest_message(self):
        """
        Gets the oldest message in the queue
        Removes it from the queue
        """
        if len(self.messages) > 0:
            return self.messages.pop(0)
        else:
            return -1

    # function executed in a new thread
    def run(self):
        my_buddy_comm = BuddyComm()
        while True:
            val = my_buddy_comm.receive()
            if val != -1:
                self.messages.append(val)
            time.sleep(.1)


# Thread for writing to SRAD2
class BuddyCommWriterThread(Thread):
    # constructor
    def __init__(self):
        # execute the base constructor
        Thread.__init__(self)
        self.my_buddy_comm = BuddyComm()
        self.send_queue = []

    def has_sent(self, num):
        return self.my_buddy_comm.get_has_sent(num)

    def send(self, val):
        self.send_queue.append(val)

    # function executed in a new thread
    def run(self):
        while True:
            if len(self.send_queue) > 0:
                self.my_buddy_comm.send(self.send_queue.pop(0))
            time.sleep(.1)
