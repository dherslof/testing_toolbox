#!/usr/bin/env python3

import argparse
import pretty_errors
from os.path import exists

from logcat_support import LogcatEntry

class ParseHlpr:
   def __init__(self, logfile="", output_method='DISPLAY'):
      self.logfile = logfile
      self.output_method = output_method
      self.logfile_lines = []

   def init(self):
      if not exists(self.logfile):
         print('Unable to find: {}'.format(self.logfile))
         exit(-1)

   def set_output_method(self, output_method):
      self.output_method = output_method

   def read_logfile(self):
      file = open(self.logfile, 'r')
      all_read_lines = file.readlines()
      file.close()

      #! börja här med parsning, fungerar ej
      for e in all_read_lines:
         logcat_entry_fields = e.split(': ') #Todo: find a better delimeter?
         if len(logcat_entry_fields) > 1:
            entry_details = logcat_entry_fields[0]
            entry_msg = logcat_entry_fields[1]
            print('{} '.format(entry_details))
            #for detail in entry_details:
             #  parts = detail.split(' ')
              # print('{}'.format(len(parts)))
               #for i in parts:
               #   logcat_entry = LogcatEntry(parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip(), parts[4].strip(), parts[5].strip(), parts[6].strip(), entry_msg)
               #   self.logfile_lines.append(logcat_entry)
         else:
            bad_formatted_entry = LogcatEntry()
            bad_formatted_entry.set_non_formatted_entry(logcat_entry_fields[0])
            #print('{}'.format(logcat_entry_fields[0]))

      #print('{}'.logcat_entry.display())




if __name__ == '__main__':

   arg_parser = argparse.ArgumentParser(description="Parse and collect log entry's from a explicit POI, to either display or store")

   # General arguments
   arg_parser.add_argument("--logfile", help='Logcat file to parse', action='store', required=True)
   arg_parser.add_argument("--output", help='Choose parsing output option', choices=['DISPLAY', 'FILE'], action='store', required=False)

   subparsers = arg_parser.add_subparsers(dest='subparser_name')

   parser_logtag = subparsers.add_parser('logtag', help='parse log based on process logcat tag')
   parser_logtag.add_argument('--tag', help='The logtag of process to get logs for', action='store', required=True)

   args = arg_parser.parse_args()

   parse_hlpr = ParseHlpr(args.logfile)
   parse_hlpr.init()

   if args.output:
      parse_hlpr.set_output_method(args.output)

   parse_hlpr.read_logfile()

   if args.subparser_name == 'logtag':
      print('logtag sub command')
      print('output = {}'.format(parse_hlpr.output_method))


   print('dev-print: exiting')