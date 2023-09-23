#WHAT IS OPENCV 
"""
OpenCV is a library of programming functions mainly aimed at real-time computer vision. Originally developed by Intel, 
it was later supported by Willow Garage then Itseez. The library is cross-platform and free for use under the open-source Apache 2 License.
"""
# USAGE
# python detect_drowsiness.py --shape-predictor shape_predictor_68_face_landmarks.dat
# python detect_drowsiness.py --shape-predictor shape_predictor_68_face_landmarks.dat --alarm alarm.wav

# import the necessary packages

"""
WHAT IS SCIPY:
    
SciPy is a free and open-source Python library used for scientific computing and technical computing. 
SciPy contains modules for optimization, linear algebra, integration, interpolation, special functions,
FFT, signal and image processing, ODE solvers and other tasks common in science and engineering

"""
#USING SPATIAL DISTANCE TO CALCULATE DISTANCE BETWEEN MOUTH NOSE EARS EYES
from scipy.spatial import distance as dist
#https://docs.scipy.org/doc/scipy/reference/tutorial/spatial.html
#https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html
#scipy.spatial.distance.cdist
#scipy.spatial.distance.cdist(XA, XB, metric='euclidean', *args, **kwargs)
#Compute distance between each pair of the two collections of inputs.

from imutils.video import VideoStream
#IMUTILS
"""
A series of convenience functions to make basic image processing functions such as translation, rotation, 
resizing, skeletonization, displaying Matplotlib images, sorting contours, detecting edges, and much more easier
 with OpenCV and both Python 2.7 and Python 3.
"""
#TO READ INPUT VIDEO FRAME BY FRAME

from imutils import face_utils


#face_utils:
"""
detect facial landmarks to help us label and extract face regions, including:

Mouth, Right eyebrow, Left eyebrow, Right eye, Left eye, Nose, Jaw
"""


from threading import Thread

#Threading
"""
Python threading allows you to have different parts of your program run concurrently and can simplify your design.
"""

import numpy as np
import playsound

import imutils
import time
import dlib

#dlib:
"""
A toolkit for making real world machine learning and data analysis applications
it uses Histogram of Oriented Gradients for object detection
"""



import cv2

def sound_alarm(path):# to play alarm sound where the file is located hence giving path
	# play an alarm sound
	playsound.playsound(path)

def eye_aspect_ratio(eye):
	# compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
    """
    here eye has given numbers n we are confusing that instead of starting with 1 started with 0
                1    2   
    i.e is 0             3  (think in eye shape)
                5    4
                
                hence 1,5 n 2,4 are vertical distance and 0,3 are horizontal distance
    """
    
    
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])

	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])

	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)  it will decide whether our eye is opened or closed based on this only alert will get sound

	# return the eye aspect ratio
	return ear
 
# construct the argument parse and parse the arguments
#argument parsing is used to give path for each datafile
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
	help="path to facial landmark predictor")
ap.add_argument("-a", "--alarm", type=str, default="",
	help="path alarm .WAV file")
ap.add_argument("-w", "--webcam", type=int, default=0,
	help="index of webcam on system")
args = vars(ap.parse_args())
 
# define two constants, one for the eye aspect ratio to indicate
# blink and then a second constant for the number of consecutive
# frames the eye must be below the threshold for to set off the
# alarm
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 48

# initialize the frame counter as well as a boolean used to
# indicate if the alarm is going off
COUNTER = 0
ALARM_ON = False

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

# grab the indexes of the facial landmarks for the left and
# right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# start the video stream thread
print("[INFO] starting video stream thread...")
vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)


#cv.putText(	img, text, org, fontFace, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]]	)
"""

img			Image.
text			Text string to be drawn.
org			Bottom-left corner of the text string in the image.
fontFace		Font type, see HersheyFonts.
fontScale		Font scale factor that is multiplied by the font-specific base size.
color			Text color.
thickness		Thickness of the lines used to draw a text.
lineType		Line type. See LineTypes
bottomLeftOrigin	When true, the image data origin is at the bottom-left corner. Otherwise, it is at the top-left corner.

"""






# loop over frames from the video stream
while True:
	# grab the frame from the threaded video file stream, resize
	# it, and convert it to grayscale
	# channels)
	frame = vs.read()
	frame = imutils.resize(frame, width=450)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	# detect faces in the grayscale frame
	rects = detector(gray, 0)

	# loop over the face detections
	for rect in rects:
		# determine the facial landmarks for the face region, then
		# convert the facial landmark (x, y)-coordinates to a NumPy
		# array
		shape = predictor(gray, rect)
		shape = face_utils.shape_to_np(shape)

		# extract the left and right eye coordinates, then use the
		# coordinates to compute the eye aspect ratio for both eyes
		leftEye = shape[lStart:lEnd]
		rightEye = shape[rStart:rEnd]
		leftEAR = eye_aspect_ratio(leftEye)
		rightEAR = eye_aspect_ratio(rightEye)

		# average the eye aspect ratio together for both eyes
		ear = (leftEAR + rightEAR) / 2.0

		# compute the convex hull for the left and right eye, then
		# visualize each of the eyes
		leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)
		cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

		# check to see if the eye aspect ratio is below the blink
		# threshold, and if so, increment the blink frame counter
		if ear < EYE_AR_THRESH:
			COUNTER += 1

			# if the eyes were closed for a sufficient number of
			# then sound the alarm
			if COUNTER >= EYE_AR_CONSEC_FRAMES:
				# if the alarm is not on, turn it on
				if not ALARM_ON:
					ALARM_ON = True

					# check to see if an alarm file was supplied,
					# and if so, start a thread to have the alarm
					# sound played in the background
					if args["alarm"] != "":
						t = Thread(target=sound_alarm,
							args=(args["alarm"],))
						t.deamon = True
						t.start()

				# draw an alarm on the frame
				cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
					cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

		# otherwise, the eye aspect ratio is not below the blink
		# threshold, so reset the counter and alarm
		else:
			COUNTER = 0
			ALARM_ON = False

		# draw the computed eye aspect ratio on the frame to help
		# with debugging and setting the correct eye aspect ratio
		# thresholds and frame counters
		cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
			cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
 
	# show the frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()