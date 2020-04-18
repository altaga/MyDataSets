import sys
from auth import MiBand3
from constants import ALERT_TYPES
import time
import os
import paho.mqtt.client as mqtt
import json
import argparse

ORG = "XXXXXX"                   # YOUR ORG ID      
myauth="X-XXXXXX-XXXXXXXXXX"     # API key 
mysecret="XXXXXXXXXXXXXXXXX"     # Authentication Token
mydevice="YourDeviceName"        # Your Device Name
mydeviceid="YourDeviceId"        # Your Device ID

parser = argparse.ArgumentParser()
parser.add_argument("echo")
args = parser.parse_args()

# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc))
def on_message(client, obj, msg):
    global mqttc
    if(str(msg.payload.decode())=="hr"):
        print(str(msg.payload.decode()))
        heart_beat()
    elif(str(msg.payload.decode())=="st"):
        print(str(msg.payload.decode()))
        myd=detail_info()
        steps=myd['steps']
        meters=myd['meters']
        mqttc.publish("iot-2/type/"+mydevice+"/id/"+mydeviceid+"/evt/steps/fmt/json",'{"d":{"steps":'+ str(steps)+',"meters":'+str(meters)+'}}')
        print(detail_info())
        time.sleep(1)
    elif(str(msg.payload.decode())[0:2]=="me"):
        print(str(msg.payload.decode()))
        band.send_custom_alert(3,str(msg.payload.decode())[3:len(str(msg.payload.decode()))])
def call_immediate():
    print('Sending Call Alert')
    time.sleep(1)
    band.send_alert(ALERT_TYPES.PHONE)
def msg_immediate():
    print('Sending Message Alert')
    time.sleep(1)
    band.send_alert(ALERT_TYPES.MESSAGE)
def detail_info():
    return band.get_steps()
def custom_message():
    band.send_custom_alert(5)

def custom_call():
    # custom_call
    band.send_custom_alert(3)

def custom_missed_call():
    band.send_custom_alert(4)
    
def l(x):
    global mqttc
    mqttc.publish("iot-2/type/"+mydevice+"/id/"+mydeviceid+"/evt/bpm/fmt/json",'{"d":{"value":'+ str(x)+'}}')
    print(str(x))
    time.sleep(1)
    a = 1/0

def heart_beat():
    band.start_raw_data_realtime(heart_measure_callback=l)
    

MAC_ADDR = args.echo
print('Attempting to connect to ', MAC_ADDR)
band = MiBand3(MAC_ADDR, debug=True)
band.setSecurityLevel(level = "medium")

# Authenticate the MiBand
if len(sys.argv) > 2:
    if band.initialize():
        print("Initialized...")
    band.disconnect()
    sys.exit(0)
else:
    band.authenticate()
    

mqttc = mqtt.Client(client_id=myauth.replace("-", ':'))
sub="iot-2/type/"+mydevice+"/id/"+mydeviceid+"/cmd/status/fmt/json"

while 1:
    try:

        mqttc.on_message = on_message
        mqttc.on_connect = on_connect

        # Uncomment to enable debug messages
        #mqttc.on_log = on_log

        # Connect
        
        mqttc.username_pw_set(myauth, mysecret)
        mqttc.connect(ORG+".messaging.internetofthings.ibmcloud.com", port=1883, keepalive=60)

        # Start subscribe, with QoS level 0
        mqttc.subscribe(sub, 0)

        # Publish a message
        mqttc.publish("iot-2/type/"+mydevice+"/id/"+mydeviceid+"/evt/hello/fmt/json", "Hello from Covital Gateway")

        # Continue the network loop, exit when an error occurs
        rc = 0
        while rc == 0:
            rc = mqttc.loop()
        print("rc: " + str(rc))
        
    except Exception as msg:
        mqttc.disconnect()
        band.stop_realtime()