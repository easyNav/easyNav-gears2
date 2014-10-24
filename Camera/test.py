import numpy as np
import time
import multiprocessing
import requests
import json
import cv2
import algo

c = cv2.VideoCapture(0)
c.set(3,1280)
c.set(4,720)

while(1):

    _,f = c.read()
    cv2.imshow('img',f)

    if cv2.waitKey(25) == 27:
        break


c.release()