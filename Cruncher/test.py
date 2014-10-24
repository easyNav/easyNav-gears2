import requests
import numpy as np
import sys
# import sys
# import serial

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

        payload = { "x": x, "y": y, "z": z, "orientation": ang/180.*np.pi }
        if self.local_mode == 1:
            r = requests.post(self.local + "heartbeat/location", data=payload)
        r = requests.post(self.remote + "heartbeat/location", data=payload)
        return r.json()

    def post_heartbeat_sonar(self, name, distance):
        payload = { "distance" : distance }
        if self.local_mode == 1:
            r = requests.post(self.local + "heartbeat/sonar/" + name, data=payload)
        r = requests.post(self.remote + "heartbeat/sonar/" + name, data=payload)
        return r.json()

# device = sys.argv[1]
# if device == "mac":
#     import matplotlib.pyplot as plt
# elif device == "pi":
#     from easyNav_pi_dispatcher import DispatcherClient
#     import smokesignal
# else:
#     print "No device type entered"
#     sys.exit()



# if __name__ == '__main__':
#     print "HELLO"
