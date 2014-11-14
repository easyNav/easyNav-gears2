from ImageProcessingServer import ImageClient
import cv2

if __name__ == '__main__':

    # Get an iamge
    school_img = cv2.imread('school6.jpg')

    # Open connection to server
    image_client = ImageClient('54.169.105.67',8000)
    image_client.start()

    # Stream content and get response
    response = image_client.transmit(school_img)
    print response

    # Close connection to server
    image_client.stop()

