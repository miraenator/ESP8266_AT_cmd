#!/usr/bin/env python3

import ESP8266_ESP201
from time import sleep

e = ESP8266_ESP201.ESP8266_ESP201()
if e.find_device():
    print("----------AT------------")
    print(e.cmd_at())

    # Firmware version
    print("----------VERSION----")
    print(e.get_version())

    # Wifi mode (1: client, 2: AP, 3: dual)
    print("---------WIFI MODE-----")
    mode = e.get_wifi_mode()
    print("Mode: {}, {}".format(mode, e.decode_wifi_mode(mode['data'][0])))
    sleep(1)

    # Clients connected (in AP mode). Error in client mode
    print("---------Clients connected to the ESP-AP (AP mode)---")
    print(e.get_clients_connected())

    # Conn status. N/A as we did not open any conns
    # print("----GET connection status----")
    # print(e.get_connection_status())

    print("-----IP addr (client mode)----")
    print(e.client_get_local_ip_addr())
    print("------AP info (client mode)---")
    print(e.client_get_AP_connected_info())
    print("-----Disconnect and forget (client mode)---")  # in order to see the AP list
    # print("-----------(forget)-----------------")
    # e.client_forget_AP() #did not work for ESP-01
    # e.cmd_reset()
    print("-----------(disconnect)-----------------")
    e.client_disconnect_AP()

    # list the APs
    for i in range(1, 5):
        print("-----AP LIST (client mode)----")
        print(e.client_get_available_AP_list())
        sleep(5)
    sleep(5)
    print("---------RESET (might reconnect)---------")
    print(e.cmd_reset())
    print("------------AT-------")
    print(e.cmd_at())

    e.close()
else:
    print("No ttyUSB devices (responding to AT) found...")

# print("OS Check: {}".format(e.check_OS()))
# print("Devices: {}".format(e.get_ttyUSB_devices()))
