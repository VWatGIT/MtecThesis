# Python script to capture image from Pylon camera using pypylon
import numpy as np
from pypylon import pylon
import os
import scipy.io
import cv2



def capture_image(camera):
    # Camera needs to be initialized before and opened
    # Set the environment variable to enable the emulated camera
    #os.environ["PYLON_CAMEMU"] = "1"

    # Open the camera
    #camera.Open()

    # Start capturing a single image
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    # Retrieve the image (blocking call)
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    # Convert the image to a numpy array
    image_array = grabResult.GetArray()

    # Convert image array to the desired format (e.g., uint8 or uint16, based on your camera settings)
    image_array = np.array(image_array, dtype=np.uint8)

    # Demosaic the raw Bayer image to a full-color image
    image_array = cv2.cvtColor(image_array, cv2.COLOR_BAYER_BG2BGR)
    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR) # necessary?

    # Close the camera
    camera.StopGrabbing()
    #camera.Close()

    return image_array


if __name__ == "__main__":
    array = [1,3,4,2,-7,9,8]
    print(sorted(array))


''' Save the array to a .mat file
try:
    scipy.io.savemat('image_data.mat', {'image': image_array})
    #print("File saved successfully.")
except Exception as e:
    print(f"Error saving file: {e}")

#print(image_array.shape)
'''