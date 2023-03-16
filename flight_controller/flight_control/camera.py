import os
import datetime
from picamera import PiCamera

class Camera():
    def __init__(self, save_dir:str="./video_recordings/") -> None:
        """Creates a new camera object

        Args:
            save_dir (str, optional): Directory to save the camera footage to. Defaults to "/home/pi/rocket_logs/".
        """
        self.camera = None
        self.setup_camera()  # Hopefully sets the camera to something other than None

        self.recording = False
        self.save_dir = save_dir
        
        os.makedirs(save_dir, exist_ok=True)

    def setup_camera(self):
        print("Initializing camera")
        try:
            self.camera = PiCamera()
            print("Success!!")
        except:
            print("Error initializing camera (Check if it's plugged in)")
            self.camera = None
    
    def start_recording(self):
        """Starts the camera recording and double checks that the camera is not already recording
        """
        if self.recording:
            print("Camera is already recording")
        else:
            if self.camera is None:
                self.setup_camera()
            if self.camera is not None:  # If the camera is still None, then it failed to initialize
                date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                self.camera.start_recording(os.path.join(self.save_dir, date + "recording.h264"))
                self.recording = True
    
    def stop_recording(self):
        """Stops the camera recording and double checks that the camera is recording
        """
        if self.recording and self.camera is not None:
            self.camera.stop_recording()
            self.recording = False
        else:
            print("Camera is not recording")
    
    def start_preview(self):
        """Previews the camera feed in a window
        """
        if self.camera is None:
            self.setup_camera()
        if self.camera is not None:  # If the camera is still None, then it failed to initialize
            self.camera.start_preview()

    def stop_preview(self):
        """Stops the camera preview
        """
        if self.camera is not None:
            self.camera.stop_preview()
    
    def terminate(self):
        self.stop_preview()
        self.stop_recording()
