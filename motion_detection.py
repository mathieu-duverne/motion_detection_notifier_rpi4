import cv2
import time
import pygame
import telepot
from picamera2 import Picamera2
import numpy as np
from picamera2.encoders import H264Encoder

# telegram server
bot = telepot.Bot("7164183510:AAHS8nffj3okprElUjJUezGt4sp-3nYCghg")

# sound
pygame.mixer.init()
sound = pygame.mixer.Sound("sound/vue.mp3")
# Create an instance of the PiCamera2 object
cam = Picamera2()

#Parameters
fps=0
pos1 = (10, 300)
pos = (10, 30)
font=cv2.FONT_HERSHEY_COMPLEX
color=(0,0,255) #text color, OpenCV operates in BGR- RED
weight=3   #font-thickness
height=1.2


# Set the resolution of the camera preview
cam.preview_configuration.main.size = (600, 340)
cam.preview_configuration.main.format = "RGB888"
cam.preview_configuration.controls.FrameRate=30
cam.preview_configuration.align()
cam.configure("preview")
cam.start()

# movement detection
def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err

recording = False
prev_frame = None
# While loop to continuously capture frames from camera
while True:
    tStart=time.time()

    # Capture a frame from the camera
    frame=cam.capture_array()
    formatted_time = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time.time()))
    #Display FPS
    # cv2.putText(frame,str(round(fps))+' FPS',pos,font,height,color,weight)
    cv2.putText(frame,str(formatted_time),pos1,font, 0.9,color,weight)
    # Convert frame from BGR to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Display the original frame and grayscale frame
    # cv2.imshow('OriginalBGR', frame)
    if prev_frame is not None:
        error = mse(prev_frame, gray)
        if error > 30 and recording == False:
            sound.play()
            time.sleep(1)
            start_t = time.time()
            formatted_time = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time.time()))
            cam.capture_file(f"images/captured_image_{formatted_time}.jpg")
            f=open("images/" + f"captured_image_{formatted_time}.jpg", 'rb')
            bot.sendPhoto("6728539795", f)
            bot.sendMessage("6728539795", f"Movement Detected camera saving 10seconds {formatted_time}")
            recording = True
            print(f"Warning: MOVEMENT DETECTED at {formatted_time} saving each frame for 5 seconds")
    
    if recording:
        formatted_time = time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(time.time()))
        if (time.time() - start_t) > 5:
            print(f"End of saving {formatted_time}")
            recording = False
        cam.capture_file(f"images/captured_image_{formatted_time}.jpg")
    #cv2.imshow('Grayscale', gray)
    prev_frame = gray
    # Wait for 30 milliseconds for a key event (extract sigfigs) and exit if 'ESC' or 'q' is pressed
    key = cv2.waitKey(30) & 0xff
    #Checking keycode
    if key == 27:  # ESCAPE key
        break
    elif key == 113:  # q key
        break
    #calculate fps
    tEnd=time.time()
    # time between two epochs
    looptime=tEnd-tStart
    fps=1/looptime

# Release the camera and close all windows
cam.stop()
cv2.destroyAllWindows()
