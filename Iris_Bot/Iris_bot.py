#importing the necessary packages
from __future__ import division
import snowboydecoder
import sys
import signal
import speech_recognition as sr
import os
from ard_ser import *
import RPi.GPIO as GPIO
import sys
from bluepy.btle import *
import struct
import _thread
from time import sleep
from sense import *
import paho.mqtt.client as mqtt
from threading import Thread
GPIO.setwarnings(False)

#starting the mqtt client service
mqttc=mqtt.Client()
mqttc.connect("localhost",1883,60)
mqttc.loop_start()

#conneting to the BLE(thunderboard sense 2)
ble_service = []
ble_service.append(Peripheral())
ble_service[0].connect('"""REPLACE WITH YOUR DEVICE ID"""')
print ("Connected 1 device with addr %s " % ('"""REPLACE WITH YOUR DEVICE ID"""'))
 #assigning the characteristics
VOC_char = Characteristic
CO2_char = Characteristic
Pressure_char = Characteristic
Sound_char = Characteristic
temperature_char = Characteristic
humidity_char = Characteristic
light_char = Characteristic
UV_char = Characteristic    
services = ble_service[0].getServices()
characteristics = ble_service[0].getCharacteristics()
 #assigning uuids to request data from BLE
for k in characteristics:
                 if k.uuid == "efd658ae-c401-ef33-76e7-91b00019103b":
                     CO2_char = k
                 if k.uuid == "efd658ae-c402-ef33-76e7-91b00019103b":
                     VOC_char = k
                 if k.uuid == "2a6d":
                     Pressure_char = k
                 if k.uuid == "c8546913-bf02-45eb-8dde-9f8754f4a32e":
                     Sound_char = k
                 if k.uuid == "2a6e":
                     temperature_char = k
                 if k.uuid == "2a6f":
                     humidity_char = k
                 if k.uuid == "c8546913-bfd9-45eb-8dde-9f8754f4a32e":
                    light_char = k
                 if k.uuid == "2a76":
                     UV_char == k

interrupted = False

global thread

thread=None
#function to publish BLE data to server using mqtt service
def tbs():
 while True:
    mqttc.publish ('VOC',VOC(VOC_char))
    mqttc.publish ('eCO2',CO2(CO2_char))
    mqttc.publish ('Pressure', Pressure(Pressure_char))
    mqttc.publish ('Sound', Sound(Sound_char))
    mqttc.publish ('Temperature',Temperature(temperature_char))
    mqttc.publish ('Humidity',Humidity(humidity_char))
    mqttc.publish ('Light',Light(light_char)) 
    time.sleep(1)

#executing tbs function as thread
if thread is None:
        thread = Thread(target=tbs)
        thread.daemon = True
        thread.start()

#function for bot control using voice
def bot_control():
    r=sr.Recognizer()
    with sr.Microphone() as  source:
        audio=r.adjust_for_ambient_noise(source)
        print("yes...")
        audio = r.record(source, duration=4)
     
        input_data =r.recognize_wit(audio, key = "USE YOUR KEY!")
        print(input_data)
        if (input_data == 'base left'):
            base_l()
        if (input_data == 'base right'):
            base_r()
        if(input_data=='shoulder up'):
            shoulder_u()
        if(input_data=='shoulder down'):
            shoulder_d()
        if(input_data=='elbow up'):
            elbow_u()
        if(input_data=='elbow down'):
            elbow_u()
        if(input_data=='open'):
            gripper_o()
        if(input_data=='close'):
            gripper_c()
        if(input_data=='front'):
            bot_front()
            time.sleep(4)
            bot_stop()
        if(input_data=='back'):
            bot_back()
            time.sleep(4)
            bot_stop()
        if(input_data=='left'):
            bot_left()
            time.sleep(4)
            bot_stop() 
        if(input_data=='right'):
            bot_right()
            time.sleep(4)
            bot_stop()
        if(input_data=='stop'):
            bot_stop()
        if(input_data=='lights on'):
            mqttc.publish("lights","on")
            mqttc.publish("lights","on1")
            mqttc.publish("lights","on2")
        if(input_data=='lights off'):
            mqttc.publish("lights","off")
            mqttc.publish("lights","off1")
            mqttc.publish("lights","off2")
        if (input_data=='fans on'):
            mqttc.publish("fans","on3")
            mqttc.publish("fans","on4")
        if (input_data=='fans off'):
            mqttc.publish("fans","off3")
            mqttc.publish("fans","off4")
            
def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]

signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.38)
print('Listening... Press Ctrl+C to exit')

#starting the snowboy to listen for hotword
detector.start(detected_callback=bot_control,interrupt_check=interrupt_callback,sleep_time=0.01)

detector.terminate()

