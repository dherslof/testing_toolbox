#!/usr/bin/env python3

# Description: Lazy support script for printing IP netmask conversions. Use it as a alias in
#              the console configuration
#
# Author: dherslof

import argparse
import sys
from tabulate import tabulate
# Pip3install tabulate

# Table based on: https://www.pawprint.net/designresources/netmask-converter.php


class NetmaskConversions:
    # def create_netmask_table():
    def __init__(self):
        self.nm_table = [
            ["/0",  "0.0.0.0",         "0x00000000", "00000000 00000000 00000000 00000000"],
            ["/1",  "128.0.0.0",       "0x80000000", "10000000 00000000 00000000 00000000"],
            ["/2",  "192.0.0.0",       "0xc0000000", "11000000 00000000 00000000 00000000"],
            ["/3",  "224.0.0.0",       "0xe0000000", "11100000 00000000 00000000 00000000"],
            ["/4",  "240.0.0.0",       "0xf0000000", "11110000 00000000 00000000 00000000"],
            ["/5",  "248.0.0.0",       "0xf8000000", "11111000 00000000 00000000 00000000"],
            ["/6",  "252.0.0.0",       "0xfc000000", "11111100 00000000 00000000 00000000"],
            ["/7",  "254.0.0.0",       "0xfe000000", "11111110 00000000 00000000 00000000"],
            ["/8",  "255.0.0.0",       "0xff000000", "11111111 00000000 00000000 00000000"],
            ["/9",  "255.128.0.0",     "0xff800000", "11111111 10000000 00000000 00000000"],
            ["/10", "255.192.0.0",     "0xffc00000", "11111111 11000000 00000000 00000000"],
            ["/11", "255.224.0.0",     "0xffe00000", "11111111 11100000 00000000 00000000"],
            ["/12", "255.240.0.0",     "0xfff00000", "11111111 11110000 00000000 00000000"],
            ["/13", "255.248.0.0",     "0xfff80000", "11111111 11111000 00000000 00000000"],
            ["/14", "255.252.0.0",     "0xfffc0000", "11111111 11111100 00000000 00000000"],
            ["/15", "255.254.0.0",     "0xfffe0000", "11111111 11111110 00000000 00000000"],
            ["/16", "255.255.0.0",     "0xffff0000", "11111111 11111111 00000000 00000000"],
            ["/17", "255.255.128.0",   "0xffff8000", "11111111 11111111 10000000 00000000"],
            ["/18", "255.255.192.0",   "0xffffc000", "11111111 11111111 11000000 00000000"],
            ["/19", "255.255.224.0",   "0xffffe000", "11111111 11111111 11100000 00000000"],
            ["/20", "255.255.240.0",   "0xfffff000", "11111111 11111111 11110000 00000000"],
            ["/21", "255.255.248.0",   "0xfffff800", "11111111 11111111 11111000 00000000"],
            ["/22", "255.255.252.0",   "0xfffffc00", "11111111 11111111 11111100 00000000"],
            ["/23", "255.255.254.0",   "0xfffffe00", "11111111 11111111 11111110 00000000"],
            ["/24", "255.255.255.0",   "0xffffff00", "11111111 11111111 11111111 00000000"],
            ["/25", "255.255.255.128", "0xffffff80", "11111111 11111111 11111111 10000000"],
            ["/26", "255.255.255.192", "0xffffffc0", "11111111 11111111 11111111 11000000"],
            ["/27", "255.255.255.224", "0xffffffe0", "11111111 11111111 11111111 11100000"],
            ["/28", "255.255.255.240", "0xfffffff0", "11111111 11111111 11111111 11110000"],
            ["/29", "255.255.255.248", "0xfffffff8", "11111111 11111111 11111111 11111000"],
            ["/30", "255.255.255.252", "0xfffffffc", "11111111 11111111 11111111 11111100"],
            ["/31", "255.255.255.254", "0xfffffffe", "11111111 11111111 11111111 11111110"],
            ["/32", "255.255.255.255", "0xffffffff", "11111111 11111111 11111111 11111111"]]

        self.col_names = [" Bitmask (bits)", "Dotted Decimal", "Hex", "Binary"]

    def print_complete_table(self):
        print(tabulate(self.nm_table, headers=self.col_names, tablefmt="fancy_grid"))

    def print_specific(self, bitmask_value):

        # Note: Create a new tmp table as workaround  since tabulate doesn't support single row printing
        specific_bitmask_row = [self.nm_table[bitmask_value]]
        print(tabulate(specific_bitmask_row, headers=self.col_names, tablefmt="fancy_grid"))


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description='IP Netmask Support Table: Display netmask conversions in relation to each other')

    arg_parser.add_argument(
        '-D', '--display_all',       action='store_true', required=False,  default=False,  help='Display complete table')
    arg_parser.add_argument(
        '-d', '--display',           action='store',      required=False,  type=int,       help='Bitmask to display (without [/-prefix])')

    # Get the input arguments
    args = arg_parser.parse_args()

    netmask_conversion_table = NetmaskConversions()
    if args.display_all is True:
        netmask_conversion_table.print_complete_table()
        sys.exit(0)
    else:
        if args.display is None:
            sys.exit(0)
        else:
            netmask_conversion_table.print_specific(args.display)

sys.exit(0)
