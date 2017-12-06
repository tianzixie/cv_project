# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# code modified from https://www.pyimagesearch.com/2014/12/15/real-time-barcode-detection-video-python-opencv
# import cv2,numpy
import numpy as np
import cv2
def detect(image,th):
	# convert the image to grayscale
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
	# compute the Scharr gradient magnitude representation of the images
	# in both the x and y direction
	gradX = cv2.Sobel(gray, ddepth = cv2.cv.CV_32F, dx = 1, dy = 0, ksize = -1)
	gradY = cv2.Sobel(gray, ddepth = cv2.cv.CV_32F, dx = 0, dy = 1, ksize = -1)
 
	# subtract the y-gradient from the x-gradient
	gradient = cv2.subtract(gradX, gradY)
	gradient = cv2.convertScaleAbs(gradient)
 
	# blur and threshold the image
	blurred = cv2.GaussianBlur(gradient, (9, 9),5)
	(low, threshold) = cv2.threshold(blurred, th, 255, cv2.THRESH_BINARY)
 
	# construct a closing kernel and apply it to the thresholded image
    	RECT = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
	closed = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, RECT)
 
	# perform a series of erosions and dilations
	closed = cv2.erode(closed, None, iterations = 4)
	closed = cv2.dilate(closed, None, iterations = 4)
 
	# find the contours in the thresholded image
	(cnts, low) = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
 
	# if no contours were found, return None
	if len(cnts) == 0:
		return None
	# otherwise, sort the contours by area and compute the rotated
	# bounding box of the largest contour
	c = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
	rect = cv2.minAreaRect(c)
	box = np.int0(cv2.cv.BoxPoints(rect))
 
	# return the bounding box of the barcode
	return box
# import the necessary packages
#from pyimagesearch import simple_barcode_detection
import argparse
 
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help = "path to the (optional) video file")
args = vars(ap.parse_args())
 
# if the video path was not supplied, grab the reference to the
# camera
if not args.get("video", False):
	camera = cv2.VideoCapture(0)
 
# otherwise, load the video
else:
	camera = cv2.VideoCapture(args["video"])

#initialize a,box1 for first time use
(grabbed, frame) = camera.read()
a = detect(frame,160)
box1 = detect(frame,160)
# keep looping over the frames
while True:
	# grab the current frame
	(grabbed, frame) = camera.read()
 
	# check to see if we have reached the end of the
	# video
	if not grabbed:
		break
 
	# detect the barcode in the image
	box = detect(frame,215)
	box1 = detect(frame,160)
	# if a barcode or QR code was found, draw a green bounding box on the frame
	cv2.drawContours(frame, [box], -1, (0, 255, 0), 2)
	# if a motion was found, draw a red bounding box on the frame
	if box1 is not None and a is not None:
		#"60","500" to minimize false detection of motion
		if abs(np.sum(box1-a))>60 and abs(np.sum(box1-a))<500:
    			cv2.drawContours(frame, [box1], -1, (0, 0, 255), 2)
    			#print type(box1),box1,np.sum(box1-a)    
	# show the frame
	cv2.imshow("Frame", frame)
    # record box1 for next compare with newer box1
	a=box1
	key = cv2.waitKey(1) & 0xFF
 
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break
 
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()