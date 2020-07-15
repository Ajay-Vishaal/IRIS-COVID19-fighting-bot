#Iris server python script for establishing control communication for client(user)
#importing necessary packages
from __future__ import division
from flask_socketio import SocketIO, emit
from flask import Flask, render_template, url_for, copy_current_request_context,Response
import time
import sys
import os
from sense import *
from bluepy.btle import *
import struct
import _thread
import board
import busio as bus
import adafruit_mlx90614
import RPi.GPIO as GPIO
from ard_ser import *
from serial import Serial
import paho.mqtt.client as mqtt
from threading import Thread
import eventlet
import picamera
import cv2
import socket
import io

#starting eventlet for socketio and setting up GPIO pin modes 
eventlet.monkey_patch()
GPIO.setwarnings(False)
ir=21
GPIO.setup(ir,GPIO.IN)
#initializing I2C bus
i2c = bus.I2C(board.SCL, board.SDA, frequency=100000)
mlx = adafruit_mlx90614.MLX90614(i2c)

#starting mqtt service
mqttc=mqtt.Client()
mqttc.connect("localhost",1883,60)
mqttc.loop_start()

app = Flask(__name__)

vc = cv2.VideoCapture(0)
socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

thread=None
#function to handle  messages from subscribed topics
def on_message(client, userdata, msg):
  if (msg.topic == 'VOC'):
    print (float(msg.payload))
    socketio.emit ('VOC',{'voc': float(msg.payload)},namespace='/test')
  if (msg.topic == 'eCO2'):
    print (float(msg.payload))
    socketio.emit ('eCO2',{'eco2': float(msg.payload)},namespace='/test')
  if (msg.topic == 'Pressure'):
    print (float(msg.payload))
    socketio.emit ('Pressure',{'pressure': float(msg.payload)},namespace='/test') 
  if (msg.topic == 'Sound'):
    print (float(msg.payload))
    socketio.emit ('Sound', {'sound':float(msg.payload)},namespace='/test')    
  if (msg.topic == 'Temperature'):
    print (float(msg.payload))
    socketio.emit ('Temperature',{'temp': float(msg.payload)},namespace='/test')
  if (msg.topic == 'Humidity'):
    print (float(msg.payload))
    socketio.emit ('Humidity',{ 'humi':float(msg.payload)},namespace='/test')
  if (msg.topic == 'Light'):
    print (float(msg.payload))
    socketio.emit ('Light',{'light': float(msg.payload)},namespace='/test') 

#function for temperature scanning and video streaming executed as thread
def scanner():
  while True:
    rval, frame = vc.read()
    cv2.imwrite('t.jpg', frame)
    yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')
    data=GPIO.input(ir)
    if data == 1: 
        number=mlx.object_temperature
        print(number)
        number=(number * 9/5) + 32
        number=round(number)  
        socketio.emit('temp', {'number': number}, namespace='/test')
        time.sleep(1)
    mqttc.subscribe('VOC')
    mqttc.subscribe('eCO2')
    mqttc.subscribe('Pressure')
    mqttc.subscribe('Sound')
    mqttc.subscribe('Temperature')
    mqttc.subscribe('Humidity')
    mqttc.subscribe('Light')
    
    mqttc.on_message=on_message
    
#function to render template and thread data
@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=scanner)
        thread.daemon = True
        thread.start()
    
    return render_template('Iris_server.html')

#video streming route, src for html video streaming
@app.route('/video_feed')
def video_feed():

    return Response(scanner(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#functions for handling soicketio emit function
@socketio.on('connect', namespace='/test')
def test_connect():
    print('Client connected')
        
@socketio.on('base left',namespace='/test')
def base_left():
  base_l()
    
@socketio.on('base right',namespace='/test')
def base_right():
  base_r()
  
@socketio.on('shoulder up',namespace='/test')
def shoulder_up():
  shoulder_u() 
  
@socketio.on('shoulder down',namespace='/test')
def shoulder_down():
  shoulder_d()
  
@socketio.on('elbow up',namespace='/test')
def elbow_up():
  elbow_u()
     
@socketio.on('elbow down',namespace='/test')
def elbow_down():
  elbow_d()  
  
@socketio.on('open',namespace='/test')
def base_left():
  gripper_o()
  
@socketio.on('close',namespace='/test')
def base_left():
  gripper_c()
  
@socketio.on('front',namespace='/test')
def front():
  bot_front()

@socketio.on('back',namespace='/test')
def back():
  bot_back()

@socketio.on('left',namespace='/test')
def left():
  bot_left()
  
@socketio.on('right',namespace='/test')
def right():
  bot_right() 
  
@socketio.on('stop',namespace='/test')
def stop():
  bot_stop()  

@socketio.on('on',namespace='/test')
def light_on():
  mqttc.publish("lights","on")

@socketio.on('off',namespace='/test')
def light_off():
  mqttc.publish("lights","off")
  
@socketio.on('on1',namespace='/test')
def light1_on():
  mqttc.publish("lights","on1")

@socketio.on('off1',namespace='/test')
def light1_off():
  mqttc.publish("lights","off1")
  
@socketio.on('on2',namespace='/test')
def light2_on():
  mqttc.publish("lights","on2")

@socketio.on('off2',namespace='/test')
def light2_off():
  mqttc.publish("lights","off2")
  
@socketio.on('on3',namespace='/test')
def fan_on():
  mqttc.publish("fans","on3")

@socketio.on('off3',namespace='/test')
def fan_off():
  mqttc.publish("fans","off3")
  
@socketio.on('on4',namespace='/test')
def fan1_on():
  mqttc.publish("fans","on4")

@socketio.on('off4',namespace='/test')
def fan1_off():
  mqttc.publish("fans","off4")
   
@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')

#starts the server and runs the server forever till user interrupts
if __name__ == '__main__':
   socketio.run(app,host='0.0.0.0',port=8000,use_reloader=False)  
   
