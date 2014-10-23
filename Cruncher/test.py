import requests
import numpy as np
import sys
import serial


device = sys.argv[1]
if device == "mac":
    import matplotlib.pyplot as plt
elif device == "pi":
    from easyNav_pi_dispatcher import DispatcherClient
    import smokesignal
else:
    print "No device type entered"
    sys.exit()



if __name__ == '__main__':
    print "HELLO"