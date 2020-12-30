# SevenThirtyPi

> SevenThirty on RPi

### What is it?

SevenThirty is a plant caretaker.

Based on the MQTT protocol, its basic functions are composed of services running on the cloud and Raspberry Pi, scripts on several kinds of MCUs, and WeChat mini program.

### What are its capabilities?

* Detect air temperature and humidity and publish
* Detect soil moisture (digital quantities will be replaced by analog quantities in the future, which is more accurate) and publish
* Take photos of plants and upload them regularly
* Automatically supplement light according to light intensity
* Receive commands from the WeChat mini program to water the plants

### What can be improved

* Detection accuracy of soil moisture
* More interesting ways to interact
* ...

### Requirements

python 3.7.x
### Hardware

* Raspberry Pi 3b+
* DHT11 sensor
* GY-30 senser
* NodeMCU(esp8266 module)

### How to start it?

`uvicorn seventhirtypi:app --reload --port 9070`
