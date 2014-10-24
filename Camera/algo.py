import cv2
import numpy as np
from pytesseract import image_to_string
from PIL import Image
import time
import locations

def get_text(frame):
    arr = np.array(frame)
    img = Image.fromarray(arr)

    orig_text = image_to_string(img)
    print "ORIG: " + orig_text

    final = locations.match_location(orig_text)
    return final

def getthresholdedimg(hsv):
    blue = cv2.inRange(hsv,np.array((100,63,10)),np.array((120,255,255)))
    both = cv2.add(blue,blue)
    return both

def get_corners(point_arr):

    # Center point
    center=[0,0];
    for point in point_arr:
        center[0] += point[0];
        center[1] += point[1];

    center[0] *= (1. / len(point_arr))
    center[1] *= (1. / len(point_arr))

    top = []
    bot = []
    for point in point_arr:
        if point[1] < center[1]:
            top.append(point)
        else:
            bot.append(point)

    tl = top[1] if (top[0][0] > top[1][0]) else top[0]
    tr = top[0] if (top[0][0] > top[1][0]) else top[1]
    bl = bot[1] if (bot[0][0] > bot[1][0]) else bot[0]
    br = bot[0] if (bot[0][0] > bot[1][0]) else bot[1]

    return { "tl":tl, "tr":tr, "bl":bl, "br":br, "center":center }

def process_image(frame):
    f = frame
    #f = cv2.flip(f,1)
    f_copy = np.copy(f)
    blur = cv2.medianBlur(f,5)
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    both = getthresholdedimg(hsv)
    erode = cv2.erode(both,None,iterations = 3)
    dilate = cv2.dilate(erode,None,iterations = 10)

    # Mask Dilations
    dilate_bitwised = cv2.bitwise_and(f,f, mask= dilate)
    erode_bitwised = cv2.bitwise_and(f,f, mask= erode)

    # Texts
    texts = ""

    # Image Contour
    ctr,heir = cv2.findContours(dilate,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(f, ctr, -1, (0,255,0), 3)
    for cnt in ctr:

        print "ENTER"

        # Bounding Rect
        x,y,w,h = cv2.boundingRect(cnt)
        cx,cy = x+w/2, y+h/2
        cv2.rectangle(f,(x,y),(x+w,y+h),[255,0,0],2)

        # Check area/param
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt,True)
        if area < 800:
            continue
        print area



        # Approx Quad
        approx = cv2.approxPolyDP(cnt,0.05*cv2.arcLength(cnt,True),True)
        print len(approx)
        if not cv2.isContourConvex(approx) or len(approx) < 4 :
            continue
        #print approx[1][0]
        point_arr = [approx[0][0],approx[1][0],approx[2][0],approx[3][0]]
        #print "--"
        cv2.drawContours(f, approx, -1, (0,255,0), 3)

        # Cut
        height, width = 600,800
        try:
            defined_corners = get_corners(point_arr)
        except:
            continue
        src = np.array([defined_corners["tl"],defined_corners["tr"],defined_corners["bl"],defined_corners["br"]],np.float32)
        dst = np.array([[0,0],[width,0],[0,height],[width,height]],np.float32)
        M = cv2.getPerspectiveTransform(src,dst)
        dst = cv2.warpPerspective(f_copy,M,(width,height))

        #cv2.imshow("bitwise",dst)
        #cv2.imshow("x",f)
        #time.sleep(5)
        texts += (get_text(dst) + ",")

    return texts
