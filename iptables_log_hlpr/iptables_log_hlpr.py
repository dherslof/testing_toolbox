#!/usr/bin/env python3

# Description: Support script for analyzing iptables LOG target output
#
# Author: dherslof

import argparse
import sys

from pathlib import Path


# Support printer for structured host logging
class HostPrinter:

    def __init__(self):
        self.log_tag = "iptables_log_hlpr "
        self.prefix_error = "[ERROR] - "
        self.prefix_info = "[INFO] - "

    def log_info(self, msg):
        print("{}{}{}".format(self.log_tag, self.prefix_info, msg))

    def log_error(self, msg):
        print("{}{}{}".format(self.log_tag, self.prefix_error, msg))

# iptables entry log class
class LogEntry:

    def __init__(self, log_entry_str):
        self.full_log_entry = log_entry_str
        self.in_interface = ""
        self.out_interface = ""
        self.mac_address = ""
        self.src_address = ""
        self.destination_address = ""
# TODO: # self.src_port = ""
        # self.destination_port = ""
        # self.protocol = ""

    def get_in_interface(self):
        splitted_string = self.full_log_entry.split("=")
        tmp = splitted_string[1].split(" ")
        self.in_interface = tmp[0]
        # print(self.in_interface)

    def get_output_interface(self):
        splitted_string = self.full_log_entry.split("=")
        tmp = splitted_string[2].split(" ")
        self.out_interface = tmp[0]
        # if self.out_interface !="":
            # print(self.out_interface)
        # print(self.out_interface)

    def get_mac_address(self):
        splitted_string = self.full_log_entry.split("=")
        tmp = splitted_string[3].split(" ")
        self.mac_address = tmp[0]
        # print(self.mac_address)

    def get_src_address(self):
        splitted_string = self.full_log_entry.split("=")
        tmp = splitted_string[4].split(" ")
        self.src_address = tmp[0]
        # print(self.src_address)

    def get_destination_address(self):
        splitted_string = self.full_log_entry.split("=")
        tmp = splitted_string[5].split(" ")
        self.destination_address = tmp[0]
        # print(self.src_address)

    def populate(self):
        self.get_in_interface()
        self.get_output_interface()
        self.get_mac_address()
        self.get_src_address()
        self.get_destination_address()

# User argument container
class FlagList:

    def __init__(self, argument_flag):
        self.in_interface = argument_flag.input
        self.out_interface = argument_flag.output
        self.mac_address = argument_flag.mac
        self.src_address = argument_flag.source
        self.destination_address = argument_flag.destination
# TODO:  # self.src_port =
        # self.destination_port = ""
        # self.protocol = ""

    def show(self):
        print("Input: {}".format(self.in_interface))
        print("Output: {}".format(self.out_interface))
        print("Mac: {}".format(self.mac_address))
        print("Source: {}".format(self.src_address))
        print("Destination: {}".format(self.destination_address))

# Main log parser functionality class
class Parser:

    def __init__(self, path):
        self.logfile_path_str = path
        self.entries_list = []
        self.display_entries_list = []

    def verify_logfile_path(self):
        path = Path(self.logfile_path_str)

        if path.is_file() is False:
            host_logger.log_error("Failed to verify logfile: {}".format(path))
            return False

        return True

    def verify_ip_table_log(self, log_entry):
        if "IN=" in log_entry and "OUT=" in log_entry:
            log_entry_splitted_str = log_entry.split("]")
            # print(log_entry_splitted_str[1])
            log_entry_obj = LogEntry(log_entry_splitted_str[1])
            self.entries_list.append(log_entry_obj)

    def verify_input(self, log_entry):
        return True if log_entry.in_interface != "" else False

    def verify_output(self, log_entry):
        return True if log_entry.out_interface != "" else False

    def verify_mac_address(self, log_entry, mac_address):
        return True if log_entry.mac_address != "" else False

    def read_log_file(self):
        with open(self.logfile_path_str) as file:
            for line in file:
                self.verify_ip_table_log(line)

    def populate_details(self):
        for e in self.entries_list:
            e.populate()
    # Filter the log string based on the provided user flags
    def filter_entries(self, flags_list):
        tmp_list = []
        if flags_list.mac_address is not None:
            for e in self.entries_list:
                if e.mac_address == flags_list.mac_address:
                    if flags_list.src_address is not False:
                        if e.src_address == flags_list.src_address:
                            if flags_list.destination_address is not False:
                                if e.destination_address == flags_list.destination_address:
                                    tmp_list.append(e)
                            else:
                                tmp_list.append(e)
                    elif flags_list.destination_address is not False:
                        if e.destination_address == flags_list.destination_address:
                            tmp_list.append(e)
                    else:
                        tmp_list.append(e)
                else:
                    continue

        elif flags_list.destination_address is not False:
            for e in self.entries_list:
                if e.destination_address == flags_list.destination_address:
                    if flags_list.src_address is not False:
                        if e.src_address == flags_list.src_address:
                            tmp_list.append(e)
                    else:
                        tmp_list.append(e)
                else:
                    continue

        elif flags_list.src_address is not False:
            for e in self.entries_list:
                if e.src_address == flags_list.src_address:
                    tmp_list.append(e)
                else:
                    continue

        else:
            tmp_list = self.entries_list

        # print("tmp_array size = {}".format(len(tmp_list)))

        input_array = list(filter(self.verify_input, tmp_list))
        # print("size of in_logs = {}".format(len(input_array)))

        output_array = list(filter(self.verify_output, tmp_list))
        # print("size of in_logs = {}".format(len(output_array)))

        if flags_list.in_interface is True:
            for e in input_array:
                self.display_entries_list.append(e)

        if flags_list.out_interface is True:
            for e in output_array:
                self.display_entries_list.append(e)

    def display_filter_entries(self, as_number, limit):
        if as_number is True:
            print(len(self.display_entries_list))

        else:
            c = 0
            for e in self.display_entries_list:
                # print("c= {}".format(c))
                # print("limit= {}".format(limit))
                c += 1
                if limit is False:
                    print(e.full_log_entry)
                else:
                    if c <= limit:
                        print(e.full_log_entry)
                    else:
                        return

    def display_plain_file(self):
        for e in self.entries_list:
            print(e.full_log_entry)
            # print(len(self.entries_list))


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description='Support script for analyzing log output from iptables LOG target. ')

    arg_parser.add_argument(
        '-f', '--logfile', action='store', type=str, required=True, help='The logfile used as input')
    arg_parser.add_argument(
        '-s', '--source', action='store', type=str, required=False,  default=False,  help='Filter on source addresses')
    arg_parser.add_argument(
        '-d', '--destination', action='store', type=str, required=False,  default=False,  help='Filter on destination addresses')
    #arg_parser.add_argument(
    #    '-I', '--interface', action='store', type=str, required=False,  default=False,  help='Filter on specific interface')
    arg_parser.add_argument(
        '-i', '--input', action='store_true', required=False,  default=False,  help='Filter on INPUT traffic')
    arg_parser.add_argument(
        '-o', '--output', action='store_true', required=False,  default=False,  help='Filter OUTPUT traffic')
    arg_parser.add_argument(
        '-m', '--mac', action='store', required=False, help='Filter on mac address')
    arg_parser.add_argument(
        '-n', '--number', action='store_true', required=False,  default=False,  help='Present result as amount found, instead of default detailed information')
    arg_parser.add_argument(
        '-l', '--limit', action='store', required=False, type=int,  default=False,  help='Only display number of logs until the limit set')
    arg_parser.add_argument(
        '-p', '--plain', action='store_true', required=False, help='Display plain output, full parsed log')

    # Get the input arguments
    args = arg_parser.parse_args()
    args_flags_container = FlagList(args)

    # Init host printer
    host_logger = HostPrinter()

    # Read and set log entries
    log_parser = Parser(args.logfile)
    log_parser.read_log_file()
    log_parser.populate_details()

    # Verify existence of logfile
    if log_parser.verify_logfile_path() is False:
        sys.exit(1)

    # display full file and exit
    if args.plain is True:
        log_parser.display_plain_file()
        sys.exit(0)

    host_logger.log_info("Parsing logfile with following filter settings:")
    args_flags_container.show()
    print()
    host_logger.log_info("Found following entries:")
    # Execute commands based on flags
    log_parser.filter_entries(args_flags_container)
    log_parser.display_filter_entries(args.number, args.limit)

    sys.exit(0)
