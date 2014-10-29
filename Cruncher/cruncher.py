# Imports
import serial
import numpy as np
import time
import multiprocessing
import requests
import json
import math
import sys
from collections import deque

# Device Types
device = sys.argv[1]
if device == "mac":
    import matplotlib.pyplot as plt
elif device == "pi":
    from easyNav_pi_dispatcher import DispatcherClient
    import smokesignal
else:
    print "No device type entered"
    sys.exit()


def get_time():
    millis = int(round(time.time() * 1000))
    return millis

# Request class
class RequestClass:

    # constr
    def __init__(self, local_mode = 1):
        self.remote = "http://192.249.57.162:1337/"
        self.local =  "http://localhost:1337/"
        self.local_mode = local_mode

    def get_heartbeat(self):
        r = requests.get(self.local + "heartbeat")
        return r.json()

    def post_heartbeat_location(self, x, y, z, ang):

        payload = { "x": x*100, "y": y*100, "z": z, "orientation": ang/180.*np.pi }
        if self.local_mode == 1:
            r = requests.post(self.local + "heartbeat/location", data=payload, timeout=2)
        r = requests.post(self.remote + "heartbeat/location", data=payload, timeout=2)
        return r.json()

    def post_heartbeat_sonar(self, name, distance):
        payload = { "distance" : distance }
        if self.local_mode == 1:
            r = requests.post(self.local + "heartbeat/sonar/" + name, data=payload, timeout=2)
        r = requests.post(self.remote + "heartbeat/sonar/" + name, data=payload, timeout=2)
        return r.json()

    def get_sem(self):
        if self.local_mode == 1:
            r = requests.get(self.local + "heartbeat2/sm/")
        r = requests.get(self.remote + "heartbeat2/sm/")
        return r.json()

    def set_sem(self, val):
        payload = { "val" : val }
        if self.local_mode == 1:
            r = requests.post(self.local + "heartbeat2/sm/", data=payload, timeout=2)
        r = requests.post(self.remote + "heartbeat2/sm/", data=payload, timeout=2)
        return r.json()

# Position class
class PositionClass:

    # constr
    def __init__(self, x, y, ang):
        self.x = x
        self.y = y
        self.ang = ang

    def set_init(self, x, y, ang):
        print "Starting Position Updated: " + str(x) + "," + str(y) 
        self.x = x
        self.y = y
        self.ang = ang

    def set_pos(self, distance, ang):

        new_xval = distance*np.sin(ang/180.*np.pi)
        new_yval = distance*np.cos(ang/180.*np.pi)

        self.y = new_yval + self.y
        self.x = new_xval + self.x
        self.ang = ang

    def print_all(self):
        print "X: " + str(self.x) + " Y: " + str(self.y) + " ANG: " + str(self.ang)


def run_requests(ns):

    mode = 0
    if ns.device == "pi":
        mode = 1
    elif ns.device == "mac":
        mode = 0

    requests = RequestClass(local_mode=0)

    while(1):
        time.sleep(1)

        try:
            data = requests.get_sem()
            time.sleep(0.1)
            if int(data["val"]) == 1:
                ns.startx = int(data["x"])/100
                ns.starty = int(data["y"])/100
                ns.ping_start = 1
                requests.set_sem(0)
                time.sleep(0.1)

            data = requests.post_heartbeat_location(ns.x, ns.y, 0, ns.yaw)
        except:
            print "NETWORK ERROR"

# Angle class
class DataEvent:

    # constr
    def __init__(self):
        self.dispatcherClient = DispatcherClient(port=9003)
        self.attachEvents()
        self.dispatcherClient.start()

        self.angle = 0
        self.distance = 0
        self.av = 0

    def available(self):
        if self.av == 1:
            self.av = 0
            return 1
        else:
            return 0

    def attachEvents(self):
        smokesignal.clear()
        @smokesignal.on("angle")
        def onAngle(args):
            item = eval(args.get('payload'))
            self.angle = float(item["angle"])
            self.distance = float(item["distance"])
            self.av = 1

def run_data(ns):

    if ns.device == "mac":
        return

    data_event = DataEvent()

    while(1):

        time.sleep(0.1)

        # If no event available
        if data_event.available() != 1:
            continue

        # Angle
        angle = data_event.angle
        shifted_angle = angle - 60 + 90
        if shifted_angle > 360:
            shifted_angle = shifted_angle - 360
        elif shifted_angle < 0:
            shifted_angle = 360 + shifted_angle
        ns.yaw = shifted_angle

        # Mag/Ground
        conv_distance = data_event.distance/100
        if conv_distance > 1.2:
            conv_distance = 1.2
        elif (conv_distance < 0.5) and (conv_distance > 0.3):
            conv_distance = 0.5
        else:
            continue
        ns.distance = conv_distance

        # Ping it
        ns.ping_data = 1

# Angle class
class StartingEvent:

    # constr
    def __init__(self):
        self.dispatcherClient = DispatcherClient(port=9003)
        self.attachEvents()
        self.dispatcherClient.start()

        self.x = 0
        self.y = 0
        self.av = 0

    def available(self):
        if self.av == 1:
            self.av = 0
            return 1
        else:
            return 0

    def attachEvents(self):
        smokesignal.clear()
        print "attached"
        @smokesignal.on("starting")
        def onStarting(args):
            item = eval(args.get('payload'))
            self.x = float(item["x"])/100
            self.y = float(item["y"])/100
            self.av = 1

def run_starting(ns):

    if ns.device == "mac":
        return

    starting_event = StartingEvent()

    while(1):

        time.sleep(0.1)

        if starting_event.available() == 1:
            ns.startx = starting_event.x
            ns.starty = starting_event.y
            ns.ping_start = 1


if __name__ == '__main__':

    # Mp Manager
    manager = multiprocessing.Manager()
    ns = manager.Namespace()

    # Start position
    ns.device = device
    ns.startx = 0
    ns.starty = 0
    ns.ping_start = 0

    # Data Event
    ns.yaw = 0
    ns.distance = 1
    ns.ping_data = 0

    # Position class
    position = PositionClass(0, 0, 0)

    # Mp
    p2 = multiprocessing.Process(target=run_requests, args=(ns,))
    p2.start()
    p3 = multiprocessing.Process(target=run_data, args=(ns,))
    p3.start()
    p4 = multiprocessing.Process(target=run_starting, args=(ns,))
    p4.start()

    # Serial Loop
    while(1):

        # CPU usage
        time.sleep(0.1)

        # Check for change in start pos
        if ns.ping_start == 1:
            print "Starting data received: " + str(ns.startx) + " " + str(ns.starty)
            ns.ping_start = 0
            position.set_init(ns.startx, ns.starty, ns.yaw)

        # If no new data, continue
        if ns.ping_data != 1:
            continue

        # New data is available
        position.set_pos(ns.distance, ns.yaw)
        position.print_all()
        ns.x = position.x
        ns.y = position.y
        ns.ping_data = 0

    p2.join()
    p3.join()
    p4.join()
    print 'after', ns
