import sys
import site
import subprocess
import os

x = site.getsitepackages()[0]
string = "sudo cp printflush.py "+x
print subprocess.Popen(string, shell=True, stdout=subprocess.PIPE).stdout.read()
