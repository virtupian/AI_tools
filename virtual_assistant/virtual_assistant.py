import festival
import time
import speech_recognition as sr
import os
import datetime

ALERT="sunlight"
CMD1="time"
CMD2="menu"
CMD3="order"
CMD4="pay"
CMD5="completed"
CMD6="start"

def listen4Alert():
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio_data = r.record(source, duration=2)
            print("Listening...")
            try:
                text = r.recognize_google(audio_data)
            except:
                text = ""
            del(r)
            if text.find(ALERT)!=-1:
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

def timeCMD(txt):
    now = datetime.datetime.now()
    return "The current time is " + str(now.hour) + " hours and " + str(now.minute) + " minutes"

def menuCMD(txt):
    return "Today we are only serving hot drinks because our pizza oven is being cleaned. Would you like to order a coffee or a tea?"

def orderCMD(txt):
    if txt.find("coffee")!=-1:
        festival.sayText("great choice, coffee coming right up. Would you like me to charge that to your store credit card?")
    if txt.find("coffee")!=-1:
        festival.saytext("great choice, tea coming right up. Would you like me to charge that to your store credit card?")
    rsp = parseCMD()
    if rsp.find("yes")!=-1:
        return "Thank you. Transaction complete. You have been charged one dollar and fifty five cents"
    else:
        return "Ok, I'll need you to go to the cashier window to complete the order please. Thanks"


def processCMD(txt):
    if txt.find(CMD1)!=-1:
        return timeCMD(txt)
    elif txt.find(CMD2)!=-1:
        return menuCMD(txt)
    elif txt.find(CMD3)!=-1:
        return orderCMD(txt)
    elif txt.find(CMD4)!=-1:
        return payCMD(txt)
    elif txt.find(CMD5)!=-1:
        return completedCMD(txt)
    elif txt.find(CMD6)!=-1:
        return startCMD(txt)



while True:
    if listen4Alert()==True:
        festival.sayText('hello, how can I help you?')
        v = parseCMD()
        festival.sayText('you said')
        festival.sayText(v)
        rsp = processCMD(v)
        festival.sayText(rsp)
    if v == "exit":
        break;

