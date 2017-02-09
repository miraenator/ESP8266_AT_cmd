#!/usr/bin/env python3

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
  print("---------CLIents connected---")
  print(e.get_clients_connected())
  print("----GET connection status----")
  print(e.get_connection_status())
  print("-----IP addr (client)----")
  print(e.client_get_local_ip_addr())
  print("------AP info (client)---")
  print(e.client_get_AP_connected_info())
  for i in range(1,5):
    print("-----AP LIST----")
    print(e.client_get_available_AP_list())
    sleep(5)

  sleep(5)
  print("---------RESET---------")
  print(e.cmd_reset())
  print("------------AT-------")
  print(e.cmd_at())


  e.close()
else: 
  print("No ttyUSB devices (responding to AT) found...")

#print("OS Check: {}".format(e.check_OS()))
#print("Devices: {}".format(e.get_ttyUSB_devices()))


