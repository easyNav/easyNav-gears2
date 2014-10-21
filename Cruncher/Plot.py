
 
import sys, serial, argparse
import numpy as np
from time import sleep
from collections import deque
from scipy.signal import butter, lfilter, freqz

import time
import threading
 
import matplotlib.pyplot as plt 
import matplotlib.animation as animation


import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

import multiprocessing

def butter_lowpass(cutoff, fs, order=5):
  nyq = 0.5 * fs
  normal_cutoff = cutoff / nyq
  b, a = butter(order, normal_cutoff, btype='low', analog=False)
  return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
  b, a = butter_lowpass(cutoff, fs, order=order)
  y = lfilter(b, a, data)
  return y

"""
Written by RAAJ
"""

# Graph class
class GraphClass:

    # constr
    def __init__(self,ml):
        # plotarr
        self.maxLen=ml
        x = np.linspace(0, self.maxLen, self.maxLen)
        y = np.linspace(-10, 10, self.maxLen)
        plt.ion()
        self.fig = plt.figure(figsize=(14,7))

        g1 = self.fig.add_subplot(221, adjustable='box', aspect=10)
        self.g1_line_1, = g1.plot(x, y, 'r-', label='a')
        self.g1_line_2, = g1.plot(x, y, 'g-', label='a')
        self.g1_line_3, = g1.plot(x, y, 'b-', label='a')
        # self.g1_line.set_ydata([0,1,2,3,4,5,6,7,8,9])

        self.g2 = self.fig.add_subplot(222, adjustable='box', projection='polar', aspect=0.3)
        self.g2_line, = self.g2.plot(x, y, 'r-', label='a')
        self.g2_line.set_ydata([0])
        self.arrow = self.g2.arrow(-50/180.*np.pi, 0.5, 0, 1, alpha = 1.0, width = 0.055,
                 edgecolor = 'black', facecolor = 'green', lw = 3, zorder = 5)

        self.g3 = self.fig.add_subplot(212, adjustable='box', aspect=0.3)
        self.g3_line, = self.g3.plot(10, 10, 'r-', label='a', marker='o')
        # self.g3.arrow( 0, 0, 0.0, -0.2, fc="k", ec="k",
        #     head_width=1, head_length=2 )
        self.g3_line.set_ydata([0])
        self.g3_line.set_xdata([0])
        self.g3.set_ylim([-5,5])
        self.g3.set_xlim([-5,5])

        self.draw()

    # arrow
    def set_angle(self, angle):
        #print "Setting angle to: " + str(angle)
        self.arrow.remove()
        self.arrow = self.g2.arrow(angle/180.*np.pi, 0.5, 0, 1, alpha = 1.0, width = 0.055,
                 edgecolor = 'black', facecolor = 'green', lw = 3, zorder = 5)
        self.draw()

    # g3
    def set_g3(self, dist, ang):

        x_arr = self.g3_line.get_xdata()
        y_arr = self.g3_line.get_ydata()
        # dist = dist + y_arr[-1]

        new_xval = dist*np.sin(ang/180.*np.pi)
        new_yval = dist*np.cos(ang/180.*np.pi)

        new_yval = new_yval + y_arr[-1]
        new_xval = new_xval + x_arr[-1]

        x_arr.append(new_xval)
        y_arr.append(new_yval)
        self.g3_line.set_xdata(x_arr)
        self.g3_line.set_ydata(y_arr)
        self.draw()

    # g1
    def set_g1(self, arr, col):
        f_arr = [];
        for i in xrange(0,self.maxLen):
            f_arr.append(0);

        for m in xrange(0,len(arr)):
            f_arr[m] = arr[m]

        #print f_arr
        if col == "r":
            self.g1_line_1.set_ydata(f_arr)
        elif col == "g":
            self.g1_line_2.set_ydata(f_arr)
        elif col == "b":
            self.g1_line_3.set_ydata(f_arr)
        self.draw()

    # draw
    def draw(self):
        self.fig.canvas.draw()

    # add data
    def add():
        print "A"

class KalmanFilter(object):

    def __init__(self, process_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def input_latest_noisy_measurement(self, measurement):
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

    def get_latest_estimated_measurement(self):
        return self.posteri_estimate



class SmoothClass(object):

    def __init__(self):
        print "SmoothClass"


    def smooth(self, x, window_len=10, window='hanning'):
        """smooth the data using a window with requested size.
        
        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal 
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.
        
        input:
            x: the input signal 
            window_len: the dimension of the smoothing window
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.

        output:
            the smoothed signal
            
        example:

        import numpy as np    
        t = np.linspace(-2,2,0.1)
        x = np.sin(t)+np.random.randn(len(t))*0.1
        y = smooth(x)
        
        see also: 
        
        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter
     
        TODO: the window parameter could be the window itself if an array instead of a string   
        """
        if x.ndim != 1:
            raise ValueError, "smooth only accepts 1 dimension arrays."

        if x.size < window_len:
            raise ValueError, "Input vector needs to be bigger than window size."

        if window_len < 3:
            return x

        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

        s=np.r_[2*x[0]-x[window_len:1:-1], x, 2*x[-1]-x[-1:-window_len:-1]]
        #print(len(s))
        
        if window == 'flat': #moving average
            w = np.ones(window_len,'d')
        else:
            w = getattr(np, window)(window_len)
        y = np.convolve(w/w.sum(), s, mode='same')
        return y[window_len-1:-window_len+1]

    def gauss_kern(self, size, sizey=None):
        """ Returns a normalized 2D gauss kernel array for convolutions """
        size = int(size)
        if not sizey:
            sizey = size
        else:
            sizey = int(sizey)
        x, y = np.mgrid[-size:size+1, -sizey:sizey+1]
        g = np.exp(-(x**2/float(size) + y**2/float(sizey)))
        return g / g.sum()

    def blur_image(self, im, n, ny=None) :
        """ blurs the image by convolving with a gaussian kernel of typical
            size n. The optional keyword argument ny allows for a different
            size in the y direction.
        """
        g = gauss_kern(n, sizey=ny)
        improc = signal.convolve(im, g, mode='valid')
        return(improc)

# plot class
class AnalogPlot:

  # constr
  def __init__(self, strPort, maxLen):

    # open serial port
    self.ser = serial.Serial(strPort, 57600)

    # indexes
    self.accelx_index = 1
    self.accely_index = 2
    self.accelz_index = 3
    self.gyrox_index = 4
    self.gyroy_index = 5
    self.gyroz_index = 6
    self.compassx_index = 7
    self.compassy_index = 8
    self.compassz_index = 9

    # dataarr
    self.plot1_arr = deque([0.0]*maxLen)
    self.plot2_arr = deque([0.0]*maxLen)
    self.plot3_arr = deque([0.0]*maxLen)
    self.maxLen = maxLen

    self.stableCount = 0
    self.collect = 0
    self.arrFirst = 0

    # # plotarr
    # x = np.linspace(0, maxLen, maxLen)
    # y = np.linspace((60/-2), (60/2), maxLen)
    # plt.ion()
    # self.fig = plt.figure(figsize=(14,7))
    # ax = self.fig.add_subplot(1,1,1, adjustable='box', aspect=0.3)
    # self.plot1_line, = ax.plot(x, y, 'r-', label='a')
    # self.plot2_line, = ax.plot(x, y, 'g-', label='b')
    # self.plot3_line, = ax.plot(x, y, 'b-', label='c')

  def integrate(self, arr):
    sum_arr = []
    int_sum = 0
    for i in xrange(0, self.maxLen):
        int_sum +=  arr[i] * 0.04
        sum_arr.append(int_sum)
    return sum_arr

  def clearArr(self, arr):
    for i in xrange(0, self.maxLen):
        arr[i] =  0

  def sumArr(self, arr):
    total = 0
    for i in xrange(0, self.maxLen):
        total += arr[i]
    return total

  def update(self,ns):

    #areal,0.04,-0.02,-0.18

    #print "X"

    # (Read data)
    line = self.ser.readline()



    data_arr = line.split(",")
    if data_arr[0] != "#YPRMfssT=":
        return

    try:
        mag = float(data_arr[5])
        #accely = float(data_arr[2])
        time = float(data_arr[8])
    except:
        return

    #mag = mag - 1.08
    mag = mag + 0.15
    mag = mag * 9.81

    if (mag < 0) and (mag > -0.1):
      return
    elif (mag > 0) and (mag < 0.1):
      return
    elif mag == 0:
      return

    print mag


    ## (Add points)
    plot_data = [mag, time*0.001, 0]
    self.add(plot_data)
    #print plot_data

    ns.arr = self.plot1_arr
    ns.time_arr = self.plot2_arr

    ## (Kalman filter)
    # measurement_standard_deviation = np.std(self.plot1_arr)
    # process_variance = 1e-3
    # estimated_measurement_variance = measurement_standard_deviation ** 2  # 0.05 ** 2
    # kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)
    # posteri_estimate_graph = []
    # for iteration in xrange(0, self.maxLen):
    #     kalman_filter.input_latest_noisy_measurement(self.plot1_arr[iteration])
    #     posteri_estimate_graph.append(kalman_filter.get_latest_estimated_measurement())

    ## (Smoothing and integration)
    # smooth_accelx_arr = self.Smoother.smooth( np.array(self.plot1_arr) ,10,'blackman')
    # velx_plot = self.integrate(smooth_accelx_arr)
    # distx_plot = self.integrate(velx_plot)

    #print self.sumArr(distx_plot)


    # velx_plot = []
    # velc_sum = 0
    # for i in xrange(0, self.maxLen):
    #     velc_sum +=  smooth_accelx_arr[i] * 0.04
    #     velx_plot.append(velc_sum)
    # distx_plot = []
    # dist_sum = 0
    # for i in xrange(0, self.maxLen):
    #     dist_sum +=  velx_plot[i] * 0.04
    #     distx_plot.append(dist_sum)


    ## Plot
    #self.plot1_line.set_ydata(self.plot1_arr)
    # self.plot2_line.set_ydata(smooth_accelx_arr)

    #self.plot1_line.set_ydata(smooth_accelx_arr)
    #self.plot2_line.set_ydata(velx_plot)
    #self.plot3_line.set_ydata(distx_plot)
    #self.fig.canvas.draw()

  # add to buffer
  def addToBuf(self, buf, val):
    if len(buf) < self.maxLen:
      buf.append(val)
    else:
      buf.pop()
      buf.appendleft(val)
 
  # add data
  def add(self, data):
    assert(len(data) == 3)
    self.addToBuf(self.plot1_arr, data[0])
    self.addToBuf(self.plot2_arr, data[1])
    self.addToBuf(self.plot3_arr, data[2])

  # clean up
  def close(self):
    # close serial
    self.ser.flush()
    self.ser.close()  

def integrate(arr, m_arr):
  sum_arr = []
  int_sum = 0
  for i in xrange(0, len(arr)):
    int_sum +=  arr[i] * (m_arr[i])
    sum_arr.append(int_sum)
  return sum_arr

def sumArr(arr):
  total = 0
  for i in xrange(0, len(arr)):
    total += arr[i]
  return total

def run_graph(ns):
    graph = GraphClass(200)
    smoother = SmoothClass()

    while(1):
        #time.sleep(0.1)
        graph.set_angle(50)
        

        # Smoothing
        if len(ns.arr) > 10:


          #Lowpass
          filtered = butter_lowpass_filter(ns.arr,2, 30, 4)
          #print b

          #smooth_arr = smoother.smooth( np.array(ns.arr) ,10,'blackman')
          graph.set_g1(filtered, "r")
          #graph.set_g1(ns.arr, "b")

          vel_arr = integrate(filtered,ns.time_arr)
          dist_arr = integrate(vel_arr,ns.time_arr)


          sum_total = sumArr(dist_arr)
          print sum_total
          dist = sum_total * 0.025
          print dist

          # 12 = 0.3m
          # 40 = 1.0m
          # Distance = Val * 0.025

          graph.set_g1(vel_arr, "g")



        # if ns.ping == 1:
        #     ns.ping = 0;
        #     graph.set_g3(ns.total,ns.yaw)
        #     graph.set_g1(ns.raw_arr, "r")
        #     graph.set_g1(ns.smth_arr, "g")
        #     graph.set_g1(ns.vel_arr, "b")


# main() function
def main():
  # create parser
  # parser = argparse.ArgumentParser(description="LDR serial")
  # parser.add_argument('--port', dest='port', required=True) 
  # args = parser.parse_args()  
  # strPort = args.port

  strPort = "/dev/tty.usbserial-A600dRYL"

  # Mp Manager
  manager = multiprocessing.Manager()
  ns = manager.Namespace()
  ns.arr = []
  ns.time_arr = []

  p1 = multiprocessing.Process(target=run_graph, args=(ns,))
  p1.start()

  analogPlot = AnalogPlot(strPort, 200)
  while(1):
    #print "X"
    analogPlot.update(ns)

  analogPlot.close()

  p1.join()

  print('exiting.')
  
 
# call main
if __name__ == '__main__':
  main()