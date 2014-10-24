import numpy as np
import time
import multiprocessing
import requests
import json
import cv2

import socket
import sys
from PIL import Image
import pickle
import cStringIO
import io

# def capture_image():
#     c = cv2.VideoCapture(0)
#     c.set(3,800)
#     c.set(4,600)
#     _,f = c.read()
#     c.release()
#     return f

HOST = 'localhost'
#HOST = '54.179.156.179'

def image_grabber(ns):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, 8000))

    school_img = cv2.imread('school.jpg')

    recv_buffer = ""
    image_processed = 1

    while(1):
        if ns.img != None:

            # Image has finished processing
            if image_processed == 1:
                image_processed = 0

                buf = cv2.imencode( '.jpg', ns.img )[1].tostring()
                buf+="FAG"
                client_socket.send(buf)
            
            # Check buffer
            recv_buffer = client_socket.recv(1024)
            delim = recv_buffer.strip()[-1:]
            if delim == "-":
                ns.text = recv_buffer.replace('.','').replace('-','')
                image_processed = 1
                recv_buffer = ""


    client_socket.close()

if __name__ == '__main__':
    print "CLIENT"

    # Mp Manager
    manager = multiprocessing.Manager()
    ns = manager.Namespace()
    ns.img = None
    ns.text = None

    # Camera
    c = cv2.VideoCapture(0)
    c.set(3,1280)
    c.set(4,720)

    # Mp
    p1 = multiprocessing.Process(target=image_grabber, args=(ns,))
    p1.start()

    while(1):
        _,f = c.read()
        ns.img = f
        time.sleep(0.1)
        print ns.text

    p1.join()
    c.release()