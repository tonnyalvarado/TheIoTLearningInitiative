##*****************************************************************************
## Graficas
##***************************************************************************
import time
import client as mqtt
import json
import uuid
import pyupm_i2clcd as lcd
import pyupm_grove as grove
import pyupm_ttp223 as ttp223
import client as mqtt
import pyupm_buzzer as upmBuzzer

myLcd = lcd.Jhd1313m1(0, 0x3E, 0x62)

myLcd.setCursor(0,0)

myLcd.setColor(0, 255, 255)

touch = ttp223.TTP223(8)
button = grove.GroveButton(7)

buzzer = upmBuzzer.Buzzer(5)

chords = [upmBuzzer.MI, upmBuzzer.SI];

count=0

#Class for retrieving CPU % utilisation
class CPUutil(object):
		def __init__(self):
				self.prev_idle = 0
				self.prev_total = 0
				self.new_idle = 0
				self.new_total = 0
		def get(self):
				self.read()
				delta_idle = self.new_idle - self.prev_idle
				delta_total = self.new_total - self.prev_total
				cpuut = 0.0
				if (self.prev_total != 0) and (delta_total != 0):
						cpuut = ((delta_total - delta_idle) * 100.0 / delta_total)
				return cpuut
		def read(self):
				self.prev_idle = self.new_idle
				self.prev_total = self.new_total
				self.new_idle = 0;
				self.new_total = 0;
				with open('/proc/stat') as f:
						line = f.readline()
				parts = line.split()
				if len(parts) >= 5:
						self.new_idle = int(parts[4])
						for part in parts[1:]:
								self.new_total += int(part)


macAddress = hex(uuid.getnode())[2:-1]
macAddress = format(long(macAddress, 16),'012x')

organization = "quickstart"
deviceType = "iotsample-gateway"
broker = ""
topic = "iot-2/evt/status/fmt/json"
username = ""
password = ""


error_to_catch = getattr(__builtins__,'FileNotFoundError', IOError)

try:

		file_object = open("./device.cfg")
		
		for line in file_object:
				
				readType, readValue = line.split("=")
			
				if readType == "org":	
						organization = readValue.strip()
				elif readType == "type": 
						deviceType = readValue.strip()
				elif readType == "id": 
						macAddress = readValue.strip()
				elif readType == "auth-method": 
						username = "use-token-auth"
				elif readType == "auth-token": 
						password = readValue.strip()
				else:
						print("please check the format of your config file") #will want to repeat this error further down if their connection fails?
		
		file_object.close()
										
		print("Configuration file found - connecting to the registered service")
		
except error_to_catch:
		print("No config file found, connecting to the Quickstart service")
		print("MAC address: " + macAddress)


#Creating the client connection
#Set clientID and broker
clientID = "d:" + organization + ":" + deviceType + ":" + macAddress
broker = organization + ".messaging.internetofthings.ibmcloud.com"

mqttc = mqtt.Client(clientID)

#Set authentication values, if connecting to registered service
if username is not "":
		mqttc.username_pw_set(username, password=password)

mqttc.connect(host=broker, port=1883, keepalive=60)


#Publishing to IBM Internet of Things Foundation
mqttc.loop_start() 

while mqttc.loop() == 0:
		if button.value():
        	        count+=1
			print buzzer.playSound(chords[0],100000)
			time.sleep(0.1)
       		if touch.isPressed():
                	count-=1
			print buzzer.playSound(chords[1],100000)
			time.sleep(0.1)
        	myLcd.setCursor(1,2)
        	myLcd.write("%6d"%count)
		msg = json.JSONEncoder().encode({"d":{"contador":count}})
		
		mqttc.publish(topic, payload=msg, qos=0, retain=False)
		pass

del button
del touch
del buzzer
