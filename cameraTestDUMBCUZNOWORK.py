from picamera import PiCamera
from sense_hat import SenseHat
import time
import datetime

camera = PiCamera()

sense = SenseHat()
running = True
recording = False

while running:
    time.sleep(.01)
    
    print("running:", running, "recording:", recording)
    for event in sense.stick.get_events():
        if event.action == "pressed":
            if event.direction == "up":
                print("up hit")
                if recording:
                    camera.stop_recording()
                    camera.stop_preview()
                    recording = False
                else:
                    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    camera.start_preview()
                    camera.start_recording("/home/pi/Desktop/"+date+ "recording.mp4")
                    recording = True
            elif event.direction == "down":
                print("down hit")
                if recording:
                    camera.stop_preview()
                    camera.stop_recording()
                    recording = False
                running = False