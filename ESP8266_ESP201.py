# Python3
# Class for working with ESP8266 chip (ESP-201) via AT commands
# Created 170208 by bursam: Get info from ESP8266 ESP-201 via AT commands
# Updated 170309 by bursam: Works with ESP-01 (the easy testing cmd). The
# Reference(s):
#  http://room-15.github.io/blog/2015/03/26/esp8266-at-command-reference/

# ===Connection===
# Pins: CHIP_EN -> 3.3 V (enable the chip)
# Pins: GPIO15 (IO15) -> GND (enable: boot from internal chip).
# Connection: 3.3V, GND, RX-TX, TX-RX (standard power, and RS232)
# Note: Connect the 3.3V as the last one. 
# Note: RST is left floating, for DEEP SLEEP it must be connected (HIGH):
#       Hardware has to support deep-sleep wake up (Reset pin has to be High)

# Worksforme (the Serial.id and device/port name will differ):
# Using Device /dev/ttyUSB0 with speed 115200,
#      info: Serial<id=0x7f4c48d7da58, open=False>(port='/dev/ttyUSB0',
#      baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=None,
#      xonxoff=False, rtscts=False, dsrdtr=False)
# This might help you make your ESP8266 going in minicom/screen
# Worksforme (linux): minicom -b 115200 /dev/ttyUSB0 #or /dev/ttyUSB1, ttyUSB2, ...

# for serial COMM
import serial
# getting ttyUSB files (devices)
import glob
# file permissions checking
import os
# check OS
import sys
# logging
import logging
# delays
import time

# CONFIG
RS_DEFAULT_SPEED = 115200


class ESP8266_ESP201(object):
    def __init__(self, serial_dev=None, speed=RS_DEFAULT_SPEED, **kwargs):
        """ Constructor.
        Params:
          serial:   serial file (for r/w) Default: None (auto-probe): Can be dangerous
          speed:    speed for the RS232 communication: Default: 1151200
        Note: Based on various firmware versions, people have reported various speed working,
              such as: 9600, 57600, 76800, 115200, ...
    """
        #logging.basicConfig(level=logging.DEBUG)
        logging.basicConfig(level=logging.INFO)
        self._log = logging.getLogger("ESP8266_ESP20")
        self._serial = serial_dev
        self._speed = speed
        if not self.check_OS():
            self._log.error("Incorrect OS: {}".format(sys.platform))

    def find_device(self):
        """Probes for available devices. Might be dangerous if multiple are connected.
       Use with care.
       Returns: T/F
    """
        self._log.warn("Probing devices (might be dangerous if multiple are connected). Make sure the device is not used.")
        for dev in self.get_ttyUSB_devices():
            # self._log.debug("Probing device: {} with speed {}".format(dev, self._speed))
            if self.probe_ttyUSB_device(dev, self._speed):
                self._log.info("Using Device {} with speed {}, info: {}".format(dev, self._speed, self._serial))
                return True
                #  else:
                # self._log.debug("Device {} with speed {}: Failed".format(dev, self._speed))
        return False

    def cmd_at(self):
        """Simple testing function to test the 'AT' command.
       Mainly for testing the at_command() function
       Arguments: None
       Returns: list(status, data)
           status: True if OK, False on ERROR
    """
        return self.at_command("AT", TIMEOUT=2)

    def cmd_reset(self):
        """Performs reset of the device (AT+RST).
       After calling reset, multiple data are output. These should
       be captured in the data part of the response.
       Arguments: None
       Returns: list(status, data)
         status: True if OK, False on ERROR
       Note: Might take quite long, as the device first replies with 'OK' and
         data follows, simetimes multiple times. May be caused by weak power supply or wifi connection attempts.
    """
        return self.at_command("AT+RST", TIMEOUT=5)

    def get_version(self):
        """Gets the version info (AT+GMR).
       Arguments: None
        Returns: list(status, data)
         status: True if OK, False on ERROR
    """
        return self.at_command("AT+GMR", TIMEOUT=2)

    def get_wifi_mode(self):
        """Returns Wifi mode (client, AP, Both) (AT+CWMODE?)"""
        return self.at_command("AT+CWMODE?", TIMEOUT=2)

    def set_wifi_mode(self, mode):
        """Sets Wifi mode:
      Argumetns:
         mode: 1 = client, 2=host, 3=dual (AP+client)
    """
        return self.at_command("AT+CWMODE={}".format(mode))

    def get_clients_connected(self):
        """Returns clients connected (if in AP mode) (AT+CWLIF) (Wifi layer)
    """
        return self.at_command("AT+CWLIF")

    def get_connection_status(self):
        """gets connection info (AT+CIPSTATUS) (TCP/IP layer)
    """
        return self.at_command("AT+CIPSTATUS")

    def client_get_local_ip_addr(self):
        """should return local IP address (in client mode) (AT+CIFSR) (TCP/IP layer)
    """
        return self.at_command("AT+CIFSR")

    def client_get_available_AP_list(self):
        """ Lists available APs (AT+CWLAP) (Wifi Layer)
        returns (ecn, ssid, rssi, mac):
           ecn: 0=open, 1=wep, 2=wpa_psk, 3=wpa2_psk, 4=wpa_wpa2_psk
          ssid: string
          rssi: signal strength
          mac: mac addr (string)
          Note: Maybe try disconnect/forget first (client_disconnect_AP()/client_forget_AP())
          """
        return self.at_command("AT+CWLAP")

    def client_connect_AP(self, ssid, password):
        """Connects to SSID with a password
      Arguments:
           # ecn: ecn: 0=open, 1=wep, 2=wpa_psk, 3=wpa2_psk, 4=wpa_wpa2_psk
          ssid: string SSID
          password: string
          """
        return self.at_command('AT+CWJAP="{}","{}"'.format(ssid, password))

    def client_disconnect_AP(self):
        """Disconnects. from AP (AT+CWQAP).
       Note: Does not forget the setting.
    """
        return self.at_command("AT+CWQAP")

    def client_forget_AP(self):
        """Forgets the AP information. If you use AT+CWQAP (client_disconnect_AP()), the
       board disconnects, but after reset it retries the connection, which might lead
       to resets/hanging.
       Warning: ESP-01: Hangs """
        return self.at_command('AT+CWJAP=" "," "')

    def client_get_AP_connected_info(self):
        """Returns info (SSID) about AP, that the ESP is connected to.
    """
        return self.at_command("AT+CWJAP?")

    def decode_wifi_mode(self, mode):
        """Decodes wifi mode string (b'CWMODE:1') into human readable form)
    """
        # TODO: Mode can be (True, ["b'+CWMODE:1']), OR only ["b'+CWMODE:1'], or b'CWMODE:1', or 1
        if mode is None:
            return None
        m = mode.decode('UTF-8').split(":")[1]
        self._log.debug("Decoding wifi mode: {}, param was: {}".format(m, mode))
        if m == '1':
            return "Station mode (client)"
        elif m == '2':
            return "AP mode (host)"
        elif m == '2':
            return "AP + Station mode (dual mode)"
        else:
            return "Unknown: {}".format(mode)

    def at_command(self, cmd="AT", TIMEOUT=30, CNT_WHITES_LIMIT=10):
        """A general function for calling an AT command, waiting for OK/Error response.
           Checks for empty lines, aborts if too many (default: 10)
       Arguments:
         cmd:    command to be executed, default: "AT"
         TIMEOUT: timeout for the serial line (read). Default: 30
         CNT_WHITES_LIMIT: Number of whitelines to abort the command after. Usually for the AT+RST cmd.
       Returns: list(status, data)
         status: True if OK, False on ERROR
         data:   contain other information gathered (a list)
         timestamp_start: from time.time()
         timestamp_end: from time.time()
    """
        timestamp_start = time.time()
        time.sleep(1)
        if not self._serial.isOpen():
            self._log.debug("Opening serial device")
            self._serial.open()
        self._log.debug("Using serial device: {}".format(self._serial))
        EOL = bytes('\r\n', 'UTF-8')
        cmd = bytes(cmd, 'UTF-8')

        # Change timeout
        timeout = self._serial.getTimeout()
        self._serial.setTimeout(TIMEOUT)
        self._log.debug("Changed timeout from {} to {}.".format(timeout, TIMEOUT))

        # Write the first ('AT') command
        self._serial.write(cmd + EOL)
        self._serial.flush()

        # Expect echo response (AT)
        echo_response = self._serial.readline().strip()
        self._log.debug("Device echo response: {}".format(echo_response))
        if echo_response != cmd:
            self._log.debug("Device at test echo error: Expected {}, got: {}, dev: {}"
                            .format(cmd, echo_response, self._serial))

        # Expect new line/error/data
        tmp_response = self._serial.readline().strip()
        self._log.debug("Device first tmp_response: {}".format(tmp_response))
        data = list()
        status = False
        cnt = 0  # count lines received (for debug)
        cnt_whites = 0  # count successive whitelines, abort on CNT_WHITES_LIMIT
        while True:
            self._log.debug("[{}] tmp response (w={}): {}, data: {}".format(cnt, cnt_whites, tmp_response, data))
            if tmp_response == b'OK':
                status = True
                if cmd != b'AT+RST':
                    # We are done. For the RESET command, wait for other data
                    break
                else:
                    self._log.debug("OK received in RST command, waitingfor more data")
            elif tmp_response == b'ERROR':
                break
            elif tmp_response == b'busy p...':
                # not sure what it means, happened when tried to configure AP (CWJAP). Module got stuck...
                # busy p...: COmmand in progress, wait for OK
                # busy s...: Send in progress, wait for OK
                # busy: Not ready yet to receive an AT command
                data.append(tmp_response)
                break
            elif tmp_response == b'WIFI DISCONNECT':
                # async message about disconnection
                self._log.warning("Unexpected (out-of-sync) response, ignoring: {}".format(tmp_response))
            elif cmd == b'AT+RST' and tmp_response == b'ready':
                status = True
                time.sleep(5)
                waiting = self._serial.inWaiting()
                #        self._log.debug("RST: Waiting info: {}".format(waiting))
                if waiting != 0:
                    self._log.error(
                        "Final 'ready' for the command {} received, but still have chars to read: {}. "
                        "Maybe power supply issues are causing device restarts? "
                        "Maybe unsuccessful connection attempts are causing resets."
                        .format(cmd, waiting))
                else:
                    break
            elif tmp_response != b'':
                cnt_whites = 0
                data.append(tmp_response)
            else:
                cnt_whites += 1

            if cnt_whites >= CNT_WHITES_LIMIT:
                self._log.error("Too many empty received: {}, aborting cmd: {}, data received so far: {}".format(cnt_whites, cmd, data))
                self._log.debug("Aborting cmd: {} due to too many empty lines, data: {}".format(cmd, data))
                break
            cnt += 1
            tmp_response = self._serial.readline().strip()

        self._log.debug("final response for cmd: {}: {}, data: {}".format(cmd, tmp_response, data))

        # restore timeout setting
        self._log.debug("Restoring timeout from {} to {}".format(self._serial.getTimeout(), timeout))
        self._serial.setTimeout(timeout)

        return {"status": status, "data": data, "timestsamp_start": timestamp_start, "timestamp_end": time.time()}

    def check_OS(self):
        """Checks the platform (for the access to serial devices.
       Currently only Linux is supported
       Returns: True if the platform is supported"""
        if sys.platform == "linux" or sys.platform == "linux2":
            return True
        self._log.error("Unsupported platform: {}".format(sys.platform))
        return False

    def probe_at_supported(self, ser):
        """Probes if the AT commands are supported on the serial device.
       Sets the timeout to 1 sec. Increase if not ok.
       Arguments: ser: serial device to be used
       Returns: True if the AT commands are supported
       Note: Might be needed to be tuned for different boards/firmwares
       Note: This function can use the general one, but as it is the first
             and important, I've implemented it as a separate function.
    """
        EOL = bytes('\r\n', 'UTF-8')
        cmd = bytes("AT", 'UTF-8')
        # Seems to be in SEC
        TIMEOUT = 1

        # Change timeout
        timeout = ser.getTimeout()
        ser.setTimeout(TIMEOUT)
        # self._log.debug("Changed timeout from {} to {}.".format(timeout, TIMEOUT))

        # Write the first ('AT') command
        ser.write(cmd + EOL)
        ser.flush()

        # Expect echo response (AT)
        echo_response = ser.readline().strip()
        # self._log.debug("Device echo response: {}".format(echo_response))
        if echo_response != cmd:
            # self._log.debug("Device at test echo error: Expected {}, got: {}, dev: {}"
            #  .format(cmd, echo_response, ser))
            return False

        # Expect new line
        nl_response = ser.readline().strip()
        # self._log.debug("Device nl response: {}".format(nl_response))
        if nl_response != b'':
            # self._log.debug("Device at test newline error: Expected {}, got: {}, dev: {}"
            #   .format('', nl_response, ser))
            return False

        # Read the final response
        response = ser.readline().strip()
        # self._log.debug("Device at test response: {}".format(response))
        if response == b'OK':
            # restore timeout setting
            # self._log.debug("Restoring timeout from {} to {}".format(ser.getTimeout(), timeout))
            ser.setTimeout(timeout)
            # self._log.debug("Device probe: OK, info: {}".format(ser))
            self._serial = ser  # store serial line
            return True
        return False

    def get_ttyUSB_devices(self, dir="/dev", mask_prefix="ttyUSB"):
        """Gets list of devices, currently implemented for linux only.
       The list is sorted in reverse order, in order to get the last device added.
     Params:
       dir:         directory to search in (Default: "/dev")
       mask_prefix: Mask of the ttyUSB files (Default: "ttyUSB")
    Returns:        list of ttyUSB devices
    """
        devs = glob.glob(dir + os.sep + mask_prefix + '*')
        if devs is not None:
            devs.sort(reverse=True)  # Reverse sort: Usually we want the last added device
            self._log.debug("Found ttyUSB devices: {}".format(len(devs)))
        return devs

    def probe_ttyUSB_device(self, device, speed=RS_DEFAULT_SPEED):
        if not os.access(device, os.R_OK):
            self._log.debug(
                "Device not readable: {} (Make sure the user is a member of the 'dialout' group.)".format(device))
            return False
        if not os.access(device, os.W_OK):
            self._log.debug(
                "Device not writable: {} (Make sure the user is a member of the 'dialout' group.)".format(device))
            return False
        try:
            with serial.Serial(port=device, baudrate=speed) as ser:
                if not ser.isOpen():
                    self._log.debug("Cannot open serial device: {} with speed {}".format(device, speed))
                    return False
                elif not ser.readable():
                    self._log.debug("Device is not readable: {}".format(device))
                    return False
                elif not ser.writable():
                    self._log.debug("Device is not writable: {}".format(device))
                    return False
                else:
                    try:
                        return self.probe_at_supported(ser)
                    except:
                        e = sys.exc_info()[0]
                        self._log.debug("Device exception1: {}: {}".format(device, e))
        except:
            e = sys.exc_info()[0]
            self._log.debug("Device exception2: {}: {}".format(device, e))

    def close(self):
        return self._serial.close()
