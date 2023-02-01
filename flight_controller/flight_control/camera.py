import os
import datetime
from picamera import PiCamera

class Camera():
    def __init__(self, save_dir:str="~/rocket_logs/") -> None:
        """Creates a new camera object

        Args:
            save_dir (str, optional): Directory to save the camera footage to. Defaults to "/home/pi/rocket_logs/".
        """
        self.camera = PiCamera()
        self.recording = False
        self.save_dir = save_dir
        
        os.mkdirs(save_dir, exist_ok=True)
    
    def start_recording(self):
        """Starts the camera recording and double checks that the camera is not already recording
        """
        if self.recording:
            print("Camera is already recording")
        else:
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.camera.start_recording(os.path.join(self.save_dir, date + "recording.h264"))
            self.recording = True
    
    def stop_recording(self):
        """Stops the camera recording and double checks that the camera is recording
        """
        if self.recording:
            self.camera.stop_recording()
            self.recording = False
        else:
            print("Camera is not recording")
    
    def start_preview(self):
        """Previews the camera feed in a window
        """
        self.camera.start_preview()
    
    def stop_preview(self):
        """Stops the camera preview
        """
        self.camera.stop_preview()
    
    def terminate(self):
        self.stop_preview()
        self.stop_recording()
