from ImageProcessingServer import ImageServer
import cv2
import time
import algo

def process_image1(flags, img):
    return algo.process_image(img)

# Sample code
if __name__ == '__main__':

    # Create instance of image server and attach processes to them
    image_server = ImageServer()

    # Launch a server instances
    image_server.launch_process(port=8000, func=process_image1)

    while(1):
        time.sleep(1)
    image_server.end_all()