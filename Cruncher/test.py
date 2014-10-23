# import requests
# import numpy as np
# import sys
# import serial


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

r_arr = [1.0,2.0,3.0,4.0,5.0,6.0]
expand_marr = []

for i, item in enumerate(r_arr):
    expand_marr.append(item)
    expand_marr.append(item)
r_arr = expand_marr

print r_arr