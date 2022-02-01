#! /usr/bin/python

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import pyttsx3
import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence

#Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"
#Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"

# Init the audio TTS converter
engine = pyttsx3.init()
engine.setProperty("rate", 140)
engine.setProperty('voice', 'english_rp+f3')

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())

# initialize the video stream and allow the camera sensor to warm up
# Set the ser to the followng
# src = 0 : for the build in single web cam, could be your laptop webcam
# src = 2 : I had to set it to 2 inorder to use the USB webcam attached to my laptop
vs = VideoStream(src=0,framerate=10).start()
#vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# start the FPS counter
fps = FPS().start()

counter=0
speech=False
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

	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
		name = "Unknown" #if face is not recognized, then print Unknown

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
                        if counter < 10:
                            counter = counter + 1
                        elif currentname != name:
				currentname = name
				print(currentname)
                                speech=True

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

	# quit when 'q' key is pressed
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()

        if speech:
            engine.say("Welcome back")
            engine.say(currentname)
            engine.runAndWait()
            time.sleep(1.0)
            engine.say("for futher identification, please state your surname")
            engine.runAndWait()
            r = sr.Recognizer()
            with sr.Microphone() as source:
                audio_data = r.record(source, duration=5)
                print("Recognizing...")
                text = r.recognize_google(audio_data)
                print(text)
            engine.say("Thank you. Security check complete")
            engine.runAndWait()
            engine.say("would you like to repeat the same order as last time?")
            engine.runAndWait()
            with sr.Microphone() as source:
                audio_data = r.record(source, duration=5)
                print("Recognizing...")
                text = r.recognize_google(audio_data)
                print(text)
            engine.say("Thanks. I see that you ordered a sandwich with fries, and a white coffee.")
            engine.say("I'll go ahead and order that for you now.")
            engine.say("Your total bill will be seven dollars and thirty five cents.")
            engine.say("Shall I charge that to your stored credit card?")
            engine.runAndWait()
            with sr.Microphone() as source:
                audio_data = r.record(source, duration=5)
                print("Recognizing...")
                text = r.recognize_google(audio_data)
                print(text)
            engine.say("Great. You have earned a hundred loyalty points today with this transaction.")
            engine.say("Thank you and have a great day.")
            engine.runAndWait()
            del(r)
            speech=False

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
