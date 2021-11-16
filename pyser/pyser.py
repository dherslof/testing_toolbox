#!/usr/bin/env python3

# Description: Intension to be a tool for sending serial commands in testing etc. where you don't
#              want to use for example minicom.
#
# Author: dherslof

#https://stackoverflow.com/questions/676172/full-examples-of-using-pyserial-package

import argparse
from typing import Sequence
import serial
import time

# Settings for the serial device settings
class SerialSettings:
   def __init__(self, device, baudrate, sw_flow_ctrl, eight_no_one):
      self.serial_device = device
      self.baudrate = baudrate
      self.sw_flow_ctrl = sw_flow_ctrl
      self.eight_no_one = eight_no_one

   def print_settings(self):
      print('*** Serial Settings ***')
      print('serial device: {}'.format(self.serial_device))
      print('baudrate: {}'.format(self.baudrate))
      print('SW flow control: {}'.format(self.sw_flow_ctrl))
      print('8N1: {}'.format(self.eight_no_one))
      print('***********************')

   def use_8n1(self):
      if self.eight_no_one:
         return True
      else:
         return False

   def use_sw_flow_ctrl(self):
      if self.sw_flow_ctrl:
         return True
      else:
         return False

# The command to send to the device
class Command:
   def __init__(self, command_input):
      self.cmd = command_input + '\r\n'
      self.command_str = command_input

   def get_cmd(self):
      return self.cmd

   def as_string(self):
      return self.command_str

# Sender class
class SerialSender:
   def __init__(self, device_settings, command, dsettings):
      self.serial_device_settings = device_settings
      self.command = command
      self.serial = serial.Serial()
      self.display_settings = dsettings

   def setup_port(self):
      self.serial.port = self.serial_device_settings.serial_device
      self.serial.baudrate = self.serial_device_settings.baudrate

      if self.serial_device_settings.use_8n1():
         self.serial.bytesize = serial.EIGHTBITS    # number of bits per bytes
         self.serial.parity = serial.PARITY_NONE    # set parity check: no parity
         self.serial.stopbits = serial.STOPBITS_ONE # number of stop bits

      if self.serial_device_settings.use_sw_flow_ctrl():
         self.serial.xonxoff = True                # software flow control

      #print('display value: {}'.format(self.display_settings))
      if self.display_settings == True:
         self.serial_device_settings.print_settings()

   def open_port(self):
      try:
         print('Opening serial device')
         self.serial.open()
      except Exception as e:
         print('Failed to open serial device: {}'.format(str(e)))
         exit()

   def close_port(self):
      print('Closing device')
      self.serial.close()


   def execute(self):
      if self.serial.isOpen():
         self.serial.flushInput()  #flush input buffer, discarding all its contents
         self.serial.flushOutput() #flush output buffer, aborting current output and discard all that is in buffer

         command_to_send = self.get_cmd()
         #self.serial.write(command_to_send) # Send command
         print('write data: {}, to: {}. Now sleeping 2s'.format(command_to_send, serial_settings.serial_device))
         time.sleep(2)

         # todo: read serial response?

      else:
         print('ERROR: Serial device not open, unable to send command')
         exit

   def send_cmd(self):
      self.open_port()
      self.execute()
      self.close_port()

if __name__ == "__main__":

   arg_parser = argparse.ArgumentParser(description='PySer [PySerial]: Send serial commands to device')

   arg_parser.add_argument('-d', '--device',       action='store',      help= 'The serial device to use', required=True )
   arg_parser.add_argument('-b', '--baudrate',     action='store',      help= 'Selected baudrate', required=True, type=int)
   arg_parser.add_argument('-c', '--command', required=True, action='store', help='Command to send')
   arg_parser.add_argument('-S', '--sw_flow-ctrl', action='store_false', required=False, default=True, help='Disable SW flow control')
   arg_parser.add_argument('-e', '--eight_no_one', action='store_false', required=False, default=True, help='Disable 8N1 configuration')
   arg_parser.add_argument('-D', '--display_settings', action='store_true', required=False, default=False, help='Display settings used before sending command')

   # Get the input arguments
   args = arg_parser.parse_args()

   # Parse the serial settings
   serial_settings = SerialSettings(args.device,
                              args.baudrate,
                              args.sw_flow_ctrl,
                              args.eight_no_one)
   # Get command
   serial_command = Command(args.command)

   # Setup the sender
   serial_sender = SerialSender(serial_settings,
                                serial_command,
                                args.display_settings)

   # Setup port and send command
   serial_sender.setup_port()
   serial_sender.send_cmd()



