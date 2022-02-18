#! /usr/bin/python

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import festival
import speech_recognition as sr
import os
import datetime
import sys

ALERT="hello"
CMD1="repeat"
CMD2="new"
CMD3="cash"
CMD4="credit"
CMD5="complete"
cmdlist = [CMD1,CMD2,CMD3,CMD4,CMD5]

if len(sys.argv) > 1:
	encodingname = str(sys.argv[1]) + "-encodings.pickle"
else:
	encodingname = "encodings.pickle"

#Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings/" + encodingname
print "Encoding file: "+ encodingsP

def identifyFace():
	# load the known faces and embeddings along with OpenCV's Haar
	# cascade for face detection
        print("Loading facial recognition app...")
	data = pickle.loads(open(encodingsP, "rb").read())

	# initialize the video stream and allow the camera sensor to warm up
	# Set the ser to the followng
	# src = 0 : for the build in single web cam, could be your laptop webcam
	# src = 2 : I had to set it to 2 inorder to use the USB webcam attached to my laptop
	vs = VideoStream(src=0,framerate=15).start()
	time.sleep(1.0)

	# start the FPS counter
	fps = FPS().start()

	counter=0
        currentname=name="unknown"
	# loop over frames from the video file stream
	while True:
		# grab the frame from the threaded video stream and resize it
		# to 500px (to speedup processing)
		frame = vs.read()
		frame = imutils.resize(frame, width=500)
		# Detect the fce boxes
		boxes = face_recognition.face_locations(frame)
		# compute the facial embeddings for each face bounding box
		encodings = face_recognition.face_encodings(frame, boxes)
		names = []
                matches = []

		# loop over the facial embeddings
		for encoding in encodings:
			# attempt to match each face in the input image to our known
			# encodings
			matches = face_recognition.compare_faces(data["encodings"],
								 encoding)

		# check to see if we have found a match
		if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
			name = max(counts, key=counts.get)

			#If someone in your dataset is identified, print their name on the screen
                        if currentname != name:
				currentname = name
                                print("Recognised face: " + currentname)
                                
		# update the list of names
		names.append(name)

		# loop over the recognized faces
		for ((top, right, bottom, left), name) in zip(boxes, names):
			# draw the predicted face name on the image - color is in BGR
			cv2.rectangle(frame, (left, top), (right, bottom),
				      (0, 255, 225), 2)
			y = top - 15 if top - 15 > 15 else top + 15
			cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
				    .8, (0, 255, 255), 2)

		# display the image to our screen
		cv2.imshow("Facial Recognition is Running", frame)
		key = cv2.waitKey(1) & 0xFF

		#Exit when face is recognised or time exceeded
		if counter > 5 and currentname != "unknown":
			break;
		elif counter > 10:
                        print("Failed to recognise face")
			break;
		counter = counter + 1

	# update the FPS counter
	fps.update()

	# stop the timer and display FPS information
	fps.stop()

	# do a bit of cleanup
	cv2.destroyAllWindows()
	vs.stop()
	return currentname


def listen4Alert():
    while True:
        r = sr.Recognizer()
        print("Listening...")
        with sr.Microphone() as source:
            audio_data = r.record(source, duration=2)
            try:
                text = r.recognize_google(audio_data)
            except:
                text = ""
            del(r)
            print("Detected voice input...")
            if text.find(ALERT)!=-1:
                print("Alert command recognised: " + ALERT)
                return True

def parseCMD():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio_data = r.record(source, duration=5)
        print("Recognizing...")
        try:
            text = r.recognize_google(audio_data)
        except:
            text = ""
        print(text)
        del(r)
        return text

def repeatCMD():
	return "Thanks. I see that last time you ordered a sandwich with fries, and a white coffee. If you would like to pay for that with the credit card we have on record, please say credit, otherwise please say other"

def newCMD():
	festival.sayText("What would you like to order?")
	str2=parseCMD()
	str3="Great. Your order of " + str2 + " is coming right up. Please drive to the cashier at booth 3 to pay. Next time we can keep your auto payment details on file so it's quicker to checkout."
	return str3

def creditCMD():
	return "Great. Thats been processed now. You have earned a hundred loyalty points today with this transaction. Please drive to the pickup point, your order will be with you momentarily."

def processCMD(txt):
    if txt.find(CMD1)!=-1:
	    return repeatCMD()
    elif txt.find(CMD2)!=-1:
	    return newCMD()
    elif txt.find(CMD3)!=-1:
	    return cashCMD()
    elif txt.find(CMD4)!=-1:
	    return creditCMD()
    elif txt.find(CMD5)!=-1:
	    return completeCMD()

while True:
    if listen4Alert()==True:
	    #First run facial security check to see if we know the person
	    festival.sayText("Hello. Please bear with me for a moment while we check our records")
	    name = identifyFace()
	    
	    if name == 'unknown':
		    festival.sayText('Thank you for waiting. It appears this is your first time ordering with us, please state your name so we can personalize this service for you')
		    name = parseCMD()
		    festival.sayText('Thank you')
		    festival.sayText(name)
		    festival.sayText('We have updated our records')
		    rsp = processCMD('new')
		    festival.sayText(rsp)
	    else:
		    festival.sayText('Welcome back')
		    festival.sayText(name)
		    festival.sayText('please select one of the following options, repeat or new order')
		    while True:
			    v = parseCMD()
			    if v not in cmdlist:
				    festival.sayText('Please select an action from the following list')
				    for v in cmdlist:
					    festival.sayText(v)
			    else:
				    break
		    rsp = processCMD(v)
		    festival.sayText(rsp)
                    while True:
                            v = parseCMD()
                            if v not in cmdlist:
                                    festival.sayText('Please select an action from the following list')
                                    for v in cmdlist:
                                            festival.sayText(v)
                            else:
                                    break
                    rsp = processCMD(v)
                    festival.sayText(rsp)
	    festival.sayText("Thanks for visiting today")
	    festival.sayText(name)
	    festival.sayText("and have a nice day")


