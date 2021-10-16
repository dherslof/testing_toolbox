#!/usr/bin/env python3

# Description: Python Ethernet interface sniffer
# Author: dherslof

import argparse
import time
import pyshark # pip3 install pyshark

# main sniffer
class InterfaceSniffer:
   def __init__(self, interface, storage_file, capture_filter, counter, timeout, verbose, details):
      self.eth_interface = interface
      self.storage_file = storage_file
      self.capture_filter = capture_filter
      self.counter = counter
      self.timeout = timeout
      self.verbose = verbose
      self.pkg_details = details

# help functions for input arguments
   def with_filter(self):
      if self.capture_filter:
         return True
      else:
         return False

   def to_file(self):
      if self.storage_file:
         return True
      else:
         return False

   def stop_on_timeout(self):
      if self.timeout != 0:
         return True
      else:
         return False

   def stop_on_counter(self):
      if self.counter != 0:
         return True
      else:
         return False

   def verbose_mode(self):
      if self.verbose:
         return True
      else:
         return False

   def print_pkg_details(self):
      if self.pkg_details:
         return True
      else:
         return False

   # Capture packages
   def start(self):

      if self.verbose_mode():
         print('Interface: {}'.format(self.eth_interface))

      capture = None

      if self.with_filter():
         if self.verbose_mode():
            print('Filter: {}'.format(self.capture_filter))

         if self.to_file():
               if self.verbose_mode():
                  print('Storage-file: {}'.format(self.storage_file))

               capture = pyshark.LiveCapture(interface=self.eth_interface, display_filter=self.capture_filter, output_file=self.storage_file)
         else:
            capture = pyshark.LiveCapture(interface=self.eth_interface, display_filter=self.capture_filter)
      else:
         if self.to_file():
            if self.verbose_mode():
               print('Storage-file: {}'. format(self.storage_file))

            capture = pyshark.LiveCapture(interface=self.eth_interface, output_file=self.storage_file)
         else:
            capture = pyshark.LiveCapture(interface=self.eth_interface)

      if self.stop_on_counter():
         for packet in capture.sniff_continuously(packet_count=self.counter):
            timestamp = time.asctime(time.localtime(time.time()))
            try:
               high_layer = capture[packet].highest_layer
               protocol = packet.transport_layer
               src_addr = packet.ip.src
               src_port = packet[protocol].srcport
               dst_addr = packet.ip.dst
               dst_port = packet[protocol].dstport

               if self.verbose_mode():
                  print('{} IP {}:{} <-> {}:{} ({})'.format(timestamp, src_addr, src_port, dst_addr, dst_port, protocol))

               if self.print_pkg_details():
                  print(packet)

            except AttributeError as e:
               # ignore packets other than TCP, UDP and IPv4 (detailed package info doesn't exists?)
               print('Unknown package [Highest layer: {}, Protocol: {}] '.format(high_layer, protocol))
               pass

         return

      if self.stop_on_timeout():
         print('Timeout: {}'.format(self.timeout))
         capture.sniff(timeout=self.timeout)
         capture.close()

         # summarize (dev purpose)
         #print('{}'.format(capture))

         for packet in range(0, len(capture)):
            try:
               high_layer = capture[packet].highest_layer
               protocol = capture[packet].transport_layer
               src_addr = capture[packet].ip.src
               src_port = capture[packet][protocol].srcport
               dst_addr = capture[packet].ip.dst
               dst_port = capture[packet][protocol].dstport
               timestamp = capture[packet].sniff_time

               if self.verbose_mode():
                  print('{} IP {}:{} <-> {}:{} ({})'.format(timestamp, src_addr, src_port, dst_addr, dst_port, protocol))

               if self.print_pkg_details():
                  print(packet)

            except AttributeError as e:
               print('Unknown package [Highest layer: {}, Protocol: {}] '.format(high_layer, protocol))
               pass

         return

if __name__ == "__main__":

   arg_parser = argparse.ArgumentParser(description='Dump data on selected ethernet interface')

   arg_parser.add_argument('-i', '--interface',    action='store',      help='Interface to listen on', required=True )
   arg_parser.add_argument('-f', '--storage_file', action='store',      help= "Store captured packages in file")
   arg_parser.add_argument('-F', '--filter',       action='store',      help= 'Capture filter - a wireshark display filter')
   arg_parser.add_argument('-c', '--counter',      action='store',      help= 'Number of total packages to capture', type=int, default=0)
   arg_parser.add_argument('-t', '--timeout',      action='store',      help= 'Capture timeout', type=int, default=0)
   arg_parser.add_argument('-V', '--verbose',      action='store_true', help= 'Run a bit more talkative', default=False)
   arg_parser.add_argument('-d', '--details',      action='store_true', help= 'Print the complete captured package, gives a lot of details (and output)')

   args = arg_parser.parse_args()

   interface_sniffer = InterfaceSniffer(args.interface,
                                        args.storage_file,
                                        args.filter,
                                        args.counter,
                                        args.timeout,
                                        args.verbose,
                                        args.details)

   ## Start sniffing based on input arguments
   interface_sniffer.start()
