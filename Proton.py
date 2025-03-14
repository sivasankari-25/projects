import datetime
import os
import sys
import time
import traceback
import webbrowser as we
from datetime import date
from os import listdir
from os.path import isfile, join
from threading import Thread

import pyttsx3
import pywhatkit
import pyautogui
import requests
import speech_recognition as sr
from pynput.keyboard import Key, Controller

import Gesture_Controller
# import Gesture_Controller_Gloved as Gesture_Controller
import app

# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init('sapi5')
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# ----------------Variables------------------------
file_exp_status = False
files =[]
path = ''
is_awake = True  #Bot status

# ------------------Functions----------------------
def reply(audio):
    app.ChatBot.addAppMsg(audio)

    print(audio)
    engine.say(audio)
    engine.runAndWait()


def wish():
    hour = int(datetime.datetime.now().hour)

    if hour>=0 and hour<12:
        reply("Good Morning!")
    elif hour>=12 and hour<18:
        reply("Good Afternoon!")   
    else:
        reply("Good Evening!")  
        
    reply("I am Proton, how may I help you?")

# Set Microphone parameters
with sr.Microphone() as source:
        r.energy_threshold = 500 
        r.dynamic_energy_threshold = False

# Audio to String
def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.8
        voice_data = ''
        audio = r.listen(source, phrase_time_limit=5)

        try:
            voice_data = r.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry my Service is down. Plz check your Internet connection')
        except sr.UnknownValueError:
            print('cant recognize')
            pass
        return voice_data.lower()

def weather():
    reply("Which city do you want for?")
    city = record_audio().title()
    try:
        res = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=9a7e5e726e2c3cf034d05fa60890d518&units=metric").json()

        temp = res["weather"][0]["description"]
        temp2 = res["main"]["temp"]
        reply(f"Temperature is {temp2} degree Celsius. Weather is {temp}.")

    except requests.exceptions.RequestException as e:
        reply("Sorry, I couldn't retrieve the weather information due to a network error.")
        print(f"Network error: {e}")

    except KeyError:
        reply("Sorry, I couldn't retrieve the weather information. Please check the city name.")
        print("KeyError: The response did not contain expected data.")

    except Exception as e:
        reply("Sorry, I couldn't retrieve the weather information.")
        print(f"Weather error: {e}")

def sendwhatmsg():
    try:
        reply("To whom you want to send the message")
        name = record_audio().lower()
        print(f"Recipient: {name}")  # Debugging output
        reply("What is the message")
        message = record_audio()
        print(f"Message: {message}")  # Debugging output
        we.open("https://web.whatsapp.com/send?phone=" + name + "&text=" + message)
        time.sleep(6)
        pyautogui.press("enter")
        reply("Message sent")
    except Exception as e:
        print(e)
        reply("Unable to send the Message")

def idea():
    try:
        reply("What is your idea?")
        data = record_audio().title()
        reply("You said me to remember this Idea: " + data)
        with open("data.txt", "a", encoding="Utf-8") as r:
            print(data, file=r)
    except Exception:
        print(traceback.format_exc())


# Executes Commands (input: string)
def respond(voice_data):
    global file_exp_status, files, is_awake, path
    print(voice_data)
    voice_data.replace('proton','')
    app.eel.addUserMsg(voice_data)

    if is_awake==False:
        if 'wake up' in voice_data:
            is_awake = True
            wish()

    # STATIC CONTROLS
    elif 'hello' in voice_data:
        wish()

    elif 'what is your name' in voice_data:
        reply('My name is Proton!')

    elif ("time" in voice_data):
        reply("Current time is " + datetime.datetime.now().strftime("%I:%M"))

    elif ("date" in voice_data):
        reply("Current date is " + str(datetime.datetime.now().day) + " " +
               str(datetime.datetime.now().month) + " " + str(datetime.datetime.now().year))

    elif ("search" in voice_data):
        reply("What do you want to search?")
        search_query = record_audio()
        try:
            we.open("https://www.google.com/search?q=" + search_query)
        except Exception as e:
            reply("Sorry, I couldn't perform the search. Please try again.")
            print(f"Search error: {e}")
    elif ("youtube" in voice_data):
        reply("what you want to search on YouTube?")
        pywhatkit.playonyt(record_audio())
    elif ("weather" in voice_data):
        weather()
    elif ("idea" in voice_data):
        idea()
    elif ("Msg" in voice_data):
        Msg()


    elif ('bye' in voice_data) or ('by' in voice_data):
        reply("Good bye Sir! Have a nice day.")
        is_awake = False

    elif ('exit' in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()        #sys.exit() always raises SystemExit, Handle it in main loop
        sys.exit()
        
    
    # DYNAMIC CONTROLS
    elif 'launch gesture recognition' in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target = gc.start)
            t.start()
            reply('Launched Successfully')

    elif ('stop gesture recognition' in voice_data) or ('top gesture recognition' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped')
        else:
            reply('Gesture recognition is already inactive')
        
    elif 'copy' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        reply('Copied')
          
    elif 'page' in voice_data or 'pest'  in voice_data or 'paste' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
        reply('Pasted')
        
    # File Navigation (Default Folder set to C://)
    elif 'list' in voice_data:
        counter = 0
        path = 'C://'
        files = listdir(path)
        filestr = ""
        for f in files:
            counter+=1
            print(str(counter) + ':  ' + f)
            filestr += str(counter) + ':  ' + f + '<br>'
        file_exp_status = True
        reply('These are the files in your root directory')
        app.ChatBot.addAppMsg(filestr)
        
    elif file_exp_status == True:
        counter = 0   
        if 'open' in voice_data:
            if isfile(join(path,files[int(voice_data.split(' ')[-1])-1])):
                os.startfile(path + files[int(voice_data.split(' ')[-1])-1])
                file_exp_status = False
            else:
                try:
                    path = path + files[int(voice_data.split(' ')[-1])-1] + '//'
                    files = listdir(path)
                    filestr = ""
                    for f in files:
                        counter+=1
                        filestr += str(counter) + ':  ' + f + '<br>'
                        print(str(counter) + ':  ' + f)
                    reply('Opened Successfully')
                    app.ChatBot.addAppMsg(filestr)
                    
                except:
                    reply('You do not have permission to access this folder')
                                    
        if 'back' in voice_data:
            filestr = ""
            if path == 'C://':
                reply('Sorry, this is the root directory')
            else:
                a = path.split('//')[:-2]
                path = '//'.join(a)
                path += '//'
                files = listdir(path)
                for f in files:
                    counter+=1
                    filestr += str(counter) + ':  ' + f + '<br>'
                    print(str(counter) + ':  ' + f)
                reply('ok')
                app.ChatBot.addAppMsg(filestr)
                   
    else: 
        reply('I am not functioned to do this !')

# ------------------Driver Code--------------------

t1 = Thread(target = app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

wish()
voice_data = None
while True:
    if app.ChatBot.isUserInput():
        #take input from GUI
        voice_data = app.ChatBot.popUserInput()
    else:
        #take input from Voice
        voice_data = record_audio()

    #process voice_data
    if 'proton' in voice_data:
        try:
            #Handle sys.exit()
            respond(voice_data)
        except SystemExit:
            reply("Exit Successfull")
            break
        except:
            #some other exception got raised
            print("EXCEPTION raised while closing.") 
            break
        


