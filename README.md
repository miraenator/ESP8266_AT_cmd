# ESP8266_AT_cmd
A simple python3 library for working with ESP8266 AT commands

Command reference: https://room-15.github.io/blog/2015/03/26/esp8266-at-command-reference/

I've recently acquired the ESP8266 ESP-201 module...
And found manually entering the AT commands fatiguing.

Therefore I tried to make a python3 library.

So far it works under Linux only and still did not manage to connect to an AP (client mode). (TODO)

Problems:
  * Upon start the module tries to connect, spontaneously resets multiple times (?power issue)
  * AT+RST resets multiple times, outputs a lot of garbage
  * AT+CWLAP hangs sometimes (after AT+CWJAP?), maybe: http://www.esp8266.com/viewtopic.php?f=6&t=571

## Connection
### ESP-201
```
Serial connection (PC(USBtoSerial) <--> ESP8266): 3.3V, GND, RX-TX, TX-RX
Chip enable (ESP8266): CHIP_EN -> 3.3V
Boot flom flash (ESP8266): GPIO15 (IO15) -> GND
```
### ESP-01
```
Serial connection (PC(USBtoSerial) <--> ESP8266): 3.3V, GND, RX-TX, TX-RX
RESET (ESP8266): 3.3 V
```
### Power supply
Power supply: Used second USBtoSerial to supply more power (needs around 300-400mA peak). Some resources state that Arduiono/USBtoSerial does not provide enough power.

For me worked the speed of 115200 baud, some people reported speeds like 9600, 86400, 57600, ...

Info about the connection (from the serial.Serial object):
```
Serial: (port='/dev/ttyUSB0', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)
```

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
  
else: 
  print("No ttyUSB devices found...")
```
### Use your own device
#### Without this lib
You can use it as a simple test for your device.
```python
import serial

with serial.Serial(port="/dev/ttyUSB0", baudrate=115200) as ser:
    if ser.isOpen():
        ser.write(b'AT\r\n')
        ser.readline()  #Echoed command 
        ser.readline()  #empty line
        ser.readline()  #response, should be OK/ERROR
```
#### With this lib
```python
import serial
ser = serial.Serial(port="/dev/ttyUSB0", baudrate=115200)
ser.isOpen()
# Should output: True

import ESP8266_ESP201
e = ESP8266_ESP201.ESP8266_ESP201(serial_dev = ser)
e.cmd_at()
# Should output: {'status': True, 'data': []}
```
#### Using minicom
Use <Ctrl-m><Ctrl-j> after typing the command (without Enter). Or <Enter> and <Ctrl-j>.
```bash
minicom -b 115200 -D /dev/ttyUSB0
AT<Ctrl-m><Ctrl-j>

#<Ctrl-A> <X> to exit
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

