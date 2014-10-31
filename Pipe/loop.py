import time
import sys

def printstream(x):
    sys.stdout.flush()
    print x

while(1):
    printstream("x")
    time.sleep(0.1)
    