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

# Filter
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

# Smooth
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

# Graph class
class GraphClass:

    # constr
    def __init__(self):
        # plotarr
        self.maxLen=200
        x = np.linspace(0, self.maxLen, self.maxLen)
        y = np.linspace(-2.5, 2.5, self.maxLen)
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

# Data class
class DataClass:

    # constr
    def __init__(self, raw, kal, smth, ang, vel, dist, ms, total):

        self.raw_arr = raw[:]
        self.kal_arr = kal[:]
        self.smth_arr = smth[:]
        self.ang_arr = ang[:]
        self.vel_arr = vel[:]
        self.dist_arr = dist[:]
        self.ms_arr = ms[:]
        self.total = total

# Crunch class
class CrunchClass:

    # constr
    def __init__(self):
        self.data_arr = []
        self.ms_arr = []
        self.ang_arr = []
        self.moving_avg = deque([1]*5)

        # Hack stab mechanism
        self.stab_count = 0
        self.stop = 0

    def integrate(self, arr, m_arr):
        sum_arr = []
        int_sum = 0
        for i in xrange(0, len(arr)):
            int_sum +=  abs(arr[i] * (m_arr[i]))
            sum_arr.append(int_sum)
        return sum_arr

    def sumArr(self, arr):
        total = 0
        for i in xrange(0, len(arr)):
            total += arr[i]
        return total

    def sumAbs(self, arr):
        total = 0
        for i in xrange(0, len(arr)):
            total += abs(arr[i])
        return total

    def process(self):

        r_arr = self.data_arr[:]
        m_arr = self.ms_arr[:]
        a_arr = self.ang_arr[:]

        self.clear_all()

        # Stage to add in extra data
        expand_rarr = []
        for i, item in enumerate(r_arr):
            if i < (len(r_arr)-1):
                curr = r_arr[i]
                next = r_arr[i+1]
                avg = (curr+next)/2
                expand_rarr.append(curr)
                expand_rarr.append(avg)
        r_arr = expand_rarr
        expand_marr = []
        for i, item in enumerate(m_arr):
            expand_marr.append(item)
            expand_marr.append(item)
        m_arr = expand_marr

        if len(r_arr) > 3:

            #print "DATA MORE THAN 10"
            #print get_time()

            avg = self.sumAbs(r_arr)
            # v_arr = self.integrate(r_arr, m_arr)
            # d_arr = self.integrate(v_arr, m_arr)
            # avg = self.sumAbs(d_arr)

            # """
            # KalmanFilter
            # """
            # measurement_standard_deviation = np.std(r_arr)
            # process_variance = 1e-3
            # estimated_measurement_variance = measurement_standard_deviation ** 2
            # kalman_filter = KalmanFilter(process_variance, estimated_measurement_variance)
            # posteri_estimate_graph = []
            # for iteration in xrange(0, len(r_arr)):
            #     kalman_filter.input_latest_noisy_measurement(r_arr[iteration])
            #     posteri_estimate_graph.append(kalman_filter.get_latest_estimated_measurement())

            # """
            # Smoothing
            # """
            # Smoother = SmoothClass()
            # smoothed_arr = Smoother.smooth( np.array(r_arr) ,3,'blackman')

            # """
            # Integral
            # """
            # vel_smoothed_arr = self.integrate(smoothed_arr, m_arr)
            # dist_smoothed_arr = self.integrate(vel_smoothed_arr, m_arr)

            # vel_kal_arr = self.integrate(posteri_estimate_graph, m_arr)
            # dist_kal_arr = self.integrate(vel_kal_arr, m_arr)

            # total_smoothed = self.sumArr(dist_smoothed_arr)*5
            # total_kal = self.sumArr(dist_kal_arr)*5
            # avg = (total_smoothed+total_kal)/2


            """
            Avg
            """

            print "------------"
            print "AVG: "+str(avg)
            print "------------"

            # If below threshold reject
            if avg < 0.3:
                return None

            # Within Range:
            if avg < 0.8:
                avg = 0.8
            elif avg > 2.0:
                avg = 2.0
            elif avg > 1.2:
                avg = 1.2

            # Moving Average
            if len(self.moving_avg) < 5:
                self.moving_avg.append(avg)
            else:
                self.moving_avg.pop()
                self.moving_avg.appendleft(avg)

            print self.moving_avg
            avg = np.average(self.moving_avg)


            print "--"
            print a_arr[0]
            print a_arr[-1]
            print avg
            print "--"

             

            # moving average - turns different bucket 0.35

            # below 0.15 reject?

            # unnatural step

            # If strafing - Tell Cruncer

            # magnetic


            """
            Dataset
            """
            #print "PROCESSED"
            #print get_time()

            return DataClass(raw=[], kal=[], smth=[], ang=a_arr, vel=[], dist=[], ms=m_arr, total=avg)

            #return DataClass(raw=r_arr, kal=posteri_estimate_graph, smth=smoothed_arr, ang=a_arr, vel=vel_smoothed_arr, dist=dist_smoothed_arr, ms=m_arr, total=avg)

        else:
            #print "DISCARD"
            return None

    def add(self, data, ms, ang):

        data-=1.08
        print data

        self.data_arr.append(data)
        self.ms_arr.append(ms)
        self.ang_arr.append(ang)

        if(len(self.data_arr) > 200):
            print "RESET"
            self.clear_all();

    def clear_all(self):

        self.data_arr = []
        self.ms_arr = []
        self.ang_arr = []

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


def run_graph(ns):

    if ns.device == "pi":
        return

    graph = GraphClass()

    while(1):
        time.sleep(0.1)
        graph.set_angle(ns.yaw)
        if ns.ping_graph == 1:
            ns.ping_graph = 0;
            graph.set_g3(ns.total,ns.yaw)
            graph.set_g1(ns.raw_arr, "r")
            graph.set_g1(ns.smth_arr, "g")
            graph.set_g1(ns.vel_arr, "b")

    serial.close()


def run_requests(ns):

    mode = 0
    if ns.device == "pi":
        mode = 1
    elif ns.device == "mac":
        mode = 0

    requests = RequestClass(local_mode=0)

    while(1):
        time.sleep(1)
        data = requests.post_heartbeat_location(ns.x, ns.y, 0, ns.yaw)


# Angle class
class SmokeEvent:

    # constr
    def __init__(self):
        self.dispatcherClient = DispatcherClient(port=9003)
        self.attachEvents()
        self.dispatcherClient.start()

        self.angle = 0
        self.mag = 0
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
            self.mag = float(item["mag"])
            self.on_ground = float(item["on_ground"])
            self.av = 1

def run_angle(ns):

    if ns.device == "mac":
        return

    smoke_event = SmokeEvent()

    while(1):

        # If no event available
        if smoke_event.available() != 1:
            continue

        # Angle
        angle = smoke_event.angle
        shifted_angle = angle - 60 + 180

        if shifted_angle > 360:
            shifted_angle = shifted_angle - 360
        elif shifted_angle < 0:
            shifted_angle = 360 + shifted_angle

        ns.yaw = shifted_angle

        # Mag/Ground
        ns.on_ground = smoke_event.on_ground
        ns.mag = smoke_event.mag
        ns.ping_smoke = 1

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

        if starting_event.available() == 1:
            ns.startx = starting_event.x
            ns.starty = starting_event.y
            ns.ping_start = 1


if __name__ == '__main__':

    # Mp Manager
    manager = multiprocessing.Manager()
    ns = manager.Namespace()

    # Graph Data
    ns.raw_arr = []
    ns.kal_arr = []
    ns.smth_arr = []
    ns.vel_arr = []
    ns.dist_arr = []
    ns.ang_arr = []
    ns.ms_arr = []
    ns.x = 0
    ns.y = 0
    ns.yaw = 0
    ns.total = 0
    ns.ping_graph = 0

    # Start position
    ns.device = device
    ns.startx = 0
    ns.starty = 0
    ns.ping_start = 0

    # Smoke stuff
    ns.mag = 0
    ns.on_ground = 1
    ns.ping_smoke = 0

    # Crunch, Position and Starting classes
    crunch = CrunchClass()
    position = PositionClass(0, 0, 0)

    # Mp
    p1 = multiprocessing.Process(target=run_graph, args=(ns,))
    p1.start()
    p2 = multiprocessing.Process(target=run_requests, args=(ns,))
    p2.start()
    p3 = multiprocessing.Process(target=run_angle, args=(ns,))
    p3.start()
    p4 = multiprocessing.Process(target=run_starting, args=(ns,))
    p4.start()

    # Serial Loop
    while(1):

        # Check for change in start pos
        if ns.ping_start == 1:
            print "Starting data received: " + str(ns.startx) + " " + str(ns.starty)
            ns.ping_start = 0
            position.set_init(ns.startx, ns.starty, ns.yaw)

        # If no new data, continue
        curr_time = get_time()
        if ns.ping_smoke != 1:
            continue

        # New data is available
        if(ns.on_ground == 0):
            crunch.add(ns.mag, get_time() - curr_time, ns.yaw)
        else:
            data_obj = crunch.process()
            if data_obj != None:
                ns.raw_arr = data_obj.raw_arr
                ns.kal_arr = data_obj.kal_arr
                ns.smth_arr = data_obj.smth_arr
                ns.vel_arr = data_obj.vel_arr
                ns.dist_arr = data_obj.dist_arr
                ns.ang_arr = data_obj.ang_arr
                ns.ms_arr = data_obj.ms_arr
                ns.total = data_obj.total
                ns.ping_graph = 1

                position.set_pos(data_obj.total, ns.yaw)
                position.print_all()
                ns.x = position.x
                ns.y = position.y
        ns.ping_smoke = 0

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    print 'after', ns
