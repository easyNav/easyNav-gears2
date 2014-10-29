from ImageProcessingServer import ImageClient
import cv2

def capture_image():
    c = cv2.VideoCapture(0)
    c.set(3,800)
    c.set(4,600)
    _,f = c.read()
    c.release()
    return f

HOST = 'localhost'
#HOST = '54.169.47.204'

if __name__ == '__main__':

    # Get an iamge
    school_img = cv2.imread('school.jpg')

    # Open connection to server
    image_client = ImageClient('localhost',8000)
    image_client.start()

    # Stream content and get response
    while(1):
        response = image_client.transmit(capture_image())
        print response

    # Close connection to server
    image_client.stop()

