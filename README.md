# ESP8266_AT_cmd
A simple python3 library for working with ESP8266 AT commands

I've recently acquired the ESP8266 ESP-201 module...
And found manually entering the AT commands fatiguing.

Therefore I tried to make a python3 library.

So far it works under Linux only and still did not manage to connect to an AP (client mode). (TODO)

## Example code
Make sure you are not connected via minicom, or any other. (I.e. the /dev/ttyUSBX is not used by any other program)
### Autodetect the ttyUSB device
```python
import ESP8266_ESP201
from time import sleep

e = ESP8266_ESP201.ESP8266_ESP201()
if e.find_device():
  print("----------AT------------")
  print(e.cmd_at())
  print("----------VERSION----")
  print(e.get_version())
  print("---------WIFI MODE-----")
  mode = e.get_wifi_mode()
  print("Mode: {}, {}".format(mode, e.decode_wifi_mode(mode[1][0])))
else: 
  print("No ttyUSB devices found...")
```
### Use your own device
```python
import serial

with serial.Serial(port="/dev/ttyUSB0", baudrate=115200) as ser:
    if ser.isOpen():
        ser.write(b'AT\r\n')
        ser.readline()  #Echoed command 
        ser.readline()  #empty line
        ser.readline()  #response, should be OK/ERROR
```
## Installation (Debian Jessie)
```bash
# Install packages (under root)
sudo apt-get install python3 python3-serial
sudo apt-get install git

# Clone the repository
git clone https://github.com/miraenator/ESP8266_AT_cmd.git

# Change the dir and run the example
cd ESP8266_AT_cmd
python3 test_esp8266.py

# Alternatively, you can set the execution permission
chmod u+x ./test_esp8266.py
# and from then you can run it as an executable file
./test_esp8266.py
```

