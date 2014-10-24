import requests
import numpy as np
import sys
# import sys
# import serial

x = float(sys.argv[1])
y = float(sys.argv[2])
ang = float(sys.argv[3])

remote = "http://192.249.57.162:1337/"
payload = { "x": x, "y": y, "z": 0, "orientation": ang/180.*np.pi }
r = requests.post(remote + "heartbeat/location", data=payload)
print r.json()


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
