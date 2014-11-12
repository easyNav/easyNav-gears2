import cv2
import numpy as np
from pytesseract import image_to_string
from PIL import Image
import time
import locations
import json
import difflib
from scipy import ndimage

def match_location(string):

    if string == "" or string == " ":
        return ""

    prev_percent = 0
    winner = ""
    winner_item = None

    dict_copy = list(locations.dicts)

    # Loop through
    for item in dict_copy:
        name = item["name"]
        curr_percent = difflib.SequenceMatcher(None, string, name).ratio()

        #print name + " " + str(curr_percent)

        if curr_percent > prev_percent:
            prev_percent = curr_percent
            winner = name
            winner_item = item
            winner_item["actual"] = string
            winner_item["percent"] = curr_percent
    
    # print "WINNER"
    # print winner_item
    # print "WINNER"

    if prev_percent < 0.4:
      return None

    return winner_item

def get_text(frame):
    arr = np.array(frame)
    img = Image.fromarray(arr)

    orig_text = image_to_string(img)

    final = match_location(orig_text)
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

def rotateImage(image, angle):
    return ndimage.rotate(image, angle)

def numeric_compare(x, y):
    if x["percent"] > y["percent"]:
        return 1
    elif x["percent"] == y["percent"]:
        return 0
    else:  #x < y
        return -1


def process_image(frame):

    print "*****************"

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
    match_arr = []

    # Image Contour
    ctr,heir = cv2.findContours(dilate,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(f, ctr, -1, (0,255,0), 3)
    for cnt in ctr:

        # Bounding Rect
        x,y,w,h = cv2.boundingRect(cnt)
        cx,cy = x+w/2, y+h/2
        cv2.rectangle(f,(x,y),(x+w,y+h),[255,0,0],2)

        # Check area/param
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt,True)
        if area < 800:
            continue

        # Approx Quad
        approx = cv2.approxPolyDP(cnt,0.05*cv2.arcLength(cnt,True),True)
        if not cv2.isContourConvex(approx) or len(approx) < 4 :
            continue
        point_arr = [approx[0][0],approx[1][0],approx[2][0],approx[3][0]]
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
        rotated_dst = rotateImage(dst,180)

        # Check text
        return_object1 = get_text(dst)
        return_object2 = get_text(rotated_dst)
        if return_object1 != None and return_object1 != "":
            return_object1_copy = dict(return_object1)
            match_arr.append(return_object1_copy)
        elif return_object2 != None and return_object2 != "":
            return_object2_copy = dict(return_object2)
            match_arr.append(return_object2_copy)
        print return_object1
        print return_object2

    # try:
    #     match_arr.sort(numeric_compare)
    # except Exception, e:
    #     print str(e)

    # TO CODE!! **********************************************
    # Rotate the image  just after the warp, and run get_text too and store in array
    # Loop through the array, and find the largest percentage one, set that as the end
    # AUTOCAP

    max_percent = 0
    final_item = []
    for item in match_arr:
        if (item["percent"] > max_percent) and (item["percent"] > 0.6):
            max_percent = item["percent"]
            final_item = [item]

    texts = json.dumps(final_item)
    cv2.putText(f,texts, (0,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255)
    cv2.imwrite("output.jpg",f)
    return texts
