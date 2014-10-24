import numpy as np
import time
import multiprocessing
import requests
import json
import cv2
import algo

import socket
import sys
from thread import *
from PIL import Image
import io

# def capture_image():
#     c = cv2.VideoCapture(0)
#     c.set(3,800)
#     c.set(4,600)
#     _,f = c.read()
#     c.release()
#     return f

def clientthread(conn):

    data = ""

    #infinite loop so that function do not terminate and thread do not end.
    while True:
         
        #Receiving from client
        data += conn.recv(1024)
        reply = '.'
        if not data: 
            break
     
        conn.sendall(reply)
        
        if data.strip()[-3:] == "FAG":
            print "RECEIVED FULL"
            data = data.strip()[:-3]
            nparr = np.fromstring(data, np.uint8)
            img = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)
            text = algo.process_image(img)
            data = ""
            conn.sendall(text+"-")
     
    #came out of loop
    conn.close()

def image_grabber(ns):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('', 8000))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    s.listen(10)
    print 'Socket now listening'
    while(1):
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        
        start_new_thread(clientthread ,(conn,))

    s.close()

if __name__ == '__main__':
    print "SERVER"

    # Mp Manager
    manager = multiprocessing.Manager()
    ns = manager.Namespace()
    ns.img = None

    # Mp
    p1 = multiprocessing.Process(target=image_grabber, args=(ns,))
    p1.start()

    while(1):
        time.sleep(0.1)

    p1.join()