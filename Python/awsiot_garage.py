#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# use this program to test the AWS IoT certificates received by the author
# to participate to the spectrogram sharing initiative on AWS cloud

# this program will subscribe and show all the messages sent by its companion
# awsiotpub.py using the AWS IoT hub

import paho.mqtt.client as paho
import os
import socket
import ssl
import RPi.GPIO as GPIO
import json
import time

def setup_GPIO():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(17,GPIO.OUT)
	GPIO.setup(27,GPIO.OUT)

def on_connect(client, userdata, flags, rc):
    print("Connection returned result: " + str(rc) )
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("#" , 1 )

def on_message(client, userdata, msg):
	print("topic: "+msg.topic)
	print("payload: "+str(msg.payload))
	if msg.topic == "Garage":
		json_msg = json.loads(msg.payload.decode())
		print json_msg["state"]["reported"]["ON_OFF"]
		if json_msg["state"]["reported"]["ON_OFF"] == "ON":
			print "GPIO HIGH"
			GPIO.output(json_msg["state"]["reported"]["GPIO"],GPIO.HIGH)
		elif json_msg["state"]["reported"]["ON_OFF"] == "OFF":
			print "GPIO LOW"
			GPIO.output(json_msg["state"]["reported"]["GPIO"],GPIO.LOW)
		elif json_msg["state"]["reported"]["ON_OFF"] == "TOGGLE":
			GPIO.output(json_msg["state"]["reported"]["GPIO"],GPIO.LOW)
			time.sleep(0.5)
			GPIO.output(json_msg["state"]["reported"]["GPIO"],GPIO.HIGH)
			time.sleep(0.5)
			GPIO.output(json_msg["state"]["reported"]["GPIO"],GPIO.LOW)
			time.sleep(0.5)
			GPIO.output(json_msg["state"]["reported"]["GPIO"],GPIO.HIGH)

#def on_log(client, userdata, level, msg):
#    print(msg.topic+" "+str(msg.payload))

setup_GPIO()
mqttc = paho.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
#mqttc.on_log = on_log

# Insert AWS host information that is given when creating Resource
awshost = "a29rk36c5id4bi.iot.us-east-1.amazonaws.com"
awsport = 8883
clientId = "GarageDoorOpener"
thingName = "GarageDoorOpener"

caPath = "aws-iot-rootCA.crt"
certPath = "cert.pem"
keyPath = "privkey.pem"

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

mqttc.connect(awshost, awsport, keepalive=60)

mqttc.loop_forever()
