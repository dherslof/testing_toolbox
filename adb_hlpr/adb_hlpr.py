#!/usr/bin/env python3

# Description: Lazy support script for support with special ADB commands which maybe isn't used everyday
#
#
# Author: dherslof

import argparse
import sys
import os

from datetime import datetime
from shutil import which
from typing_extensions import Self

# Support printer for structured host logging
class HostPrinter:

    def __init__(self, is_verbose_enabled):
        self.is_verbose_enabled = is_verbose_enabled
        self.prefix_error="[ERROR] - "
        self.prefix_info="[INFO] - "
        self.prefix_verbose="[VERBOSE] - "

    def log_verbose(self, msg):
        if self.is_verbose_enabled is False:
            return
        else:
            print("{}{}".format(self.prefix_verbose, msg))

    def log_info(self, msg):
        print("{}{}".format(self.prefix_info, msg))

    def log_error(self, msg):
        print("{}{}".format(self.prefix_info, msg))

# Wrapper class around adb commands
class AdbWrapper:

    def __init__(self, logger):
        self.host_logger = logger
        self.dump_logfile_name = "android_logcat_log"
        self.dump_logfile_suffix = ".txt"

        self.screenshot_suffix = ".png"
        self.screenshot_filename = "csd_screenshot"

        self.screen_rec_filename = "screenrecording"
        self.screen_rec_suffix = ".mp4"

        self.android_logtag = "AdbHlpr"
        self.android_storage_dir = "/data/local/tmp/"


    def verify_adb(self):
        adb_bin = which("adb")
        if adb_bin is not None:
            self.host_logger.log_verbose("adb binary found")
            return True
        else:
            self.host_logger.log_error("unable to find adb binary")
            return False

    def verify_adb_device(self):
        # Get output as a list
        devices = os.popen('adb devices').read().splitlines()
        # remove last newline char and first element to only have device id's
        devices.pop()
        del devices[0]
        # debug
        # print("{}".format(len(devices)))
        # print("{}".format(devices))
        if len(devices) > 1:
            self.host_logger.log_error("More then 1 adb device found")
            return False
        else:
            self.host_logger.log_verbose("adb device found")
            return True

    def log_dump_to_local_file(self):
        ts = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        logfile_name = self.dump_logfile_name + "_" + ts + self.dump_logfile_suffix
        os_command = "adb logcat -b all -d >> " + logfile_name
        logcat_return_code = os.system(os_command)

        if logcat_return_code != 0:
            self.host_logger.log_error("Failed to dump log using logcat")
        else:
            self.host_logger.log_info("Log dumped to: {}".format(logfile_name))

    def take_screenshot(self):
        ts = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        file_name = self.screenshot_filename + "_" + ts + self.screenshot_suffix
        os_command = "adb exec-out screencap -p > " + file_name
        adb_return_code = os.system(os_command)

        if adb_return_code != 0:
            self.host_logger.log_error("Failed to take csd screenshot")
        else:
            self.host_logger.log_info("Screenshot taken: {}".format(file_name))

    def inject_log_message(self, message):

        if message is None:
            self.host_logger.log_error("Unable to inject empty log message")
            return

        os_command = 'adb shell log -t ' + self.android_logtag + ' "' + message + '"'

        adb_return_code = os.system(os_command)
        if adb_return_code != 0:
            self.host_logger.log_error("Failed to inject log message")
        else:
            self.host_logger.log_info("Log message injected successfully : {}".format(message))

    def clear_log(self):
        os_command = "adb logcat -b all -c"
        adb_return_code = os.system(os_command)
        if adb_return_code != 0:
            self.host_logger.log_error("Failed to clear log")
        else:
            self.host_logger.log_info("Successfully cleared log")

    def generate_bugreport(self):
        os_command = "adb bugreport"
        adb_return_code = os.system(os_command)
        if adb_return_code != 0:
            self.host_logger.log_error("Failed to clear log")
        else:
            self.host_logger.log_info("Successfully cleared log")

    def record_screen(self, rec_time):
        if isinstance(rec_time, int) is False:
            host_logger.log_error("{} is not a valid recording time".format(rec_time))
            return

        host_logger.log_info("starting screen recording for {}s".format(rec_time))
        ts = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        rec_filename = self.android_storage_dir +  self.screen_rec_filename + "_" + ts + self.screen_rec_suffix
        os_command = "timeout " + str(rec_time) + " adb shell screenrecord " + rec_filename
        # Debug
        #print("{}".format(os_command))
        os.system(os_command)

        self.host_logger.log_verbose("Successfully stopped screen recording, fetching file")
        os_command_2 = "adb pull " + rec_filename + " ."
        adb_return_code2 = os.system(os_command_2)
        if adb_return_code2 != 0:
            self.host_logger.log_error("Failed to adb pull screen recording at: {}".format(rec_filename))
            return

        os_rm_command = "adb shell rm " + rec_filename
        os.system(os_rm_command)
        self.host_logger.log_info("Successfully captured screen recording")




        return

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description='Adb wrapper for easy use of commands which is not used regularly')

    arg_parser.add_argument(
        '-s', '--screenshot', action='store_true', required=False,  default=False,  help='Take a screenshot of the screen')
    arg_parser.add_argument(
        '-d', '--dump_log', action='store_true', required=False,  default=False,  help='Dump the log to a file')
    arg_parser.add_argument(
        '-i', '--inject_log', action='store', type=str, required=False, help='Inject a log message to the android log (no special chars)')
    arg_parser.add_argument(
        '-C', '--clear_log', action='store_true', required=False,  default=False,  help='Clear the logfile')
    arg_parser.add_argument(
        '-c', '--connectivity_status', action='store_true', required=False,  default=False,  help='Get a small connectivity status dump')
    arg_parser.add_argument(
        '-v', '--verbose', action='store_true', required=False,  default=False,  help='Enable verbose host logging')
    arg_parser.add_argument(
        '-b', '--bugreport', action='store_true', required=False,  default=False,  help='Trigger collecting of bugreport')
    arg_parser.add_argument(
        '-r', '--screenrecord', action='store', required=False,  type=int,  help='Record the screen for [n]s of time')

    # Get the input arguments
    args = arg_parser.parse_args()

    host_logger = HostPrinter(args.verbose)

    adb_wrapper = AdbWrapper(host_logger)
    if adb_wrapper.verify_adb() is False:
        sys.exit(1)

    if adb_wrapper.verify_adb_device() is False:
        sys.exit(1)

    # Execute commands
    if args.screenshot is True:
        adb_wrapper.take_screenshot()
        sys.exit(0)
    elif args.dump_log is True:
        adb_wrapper.log_dump_to_local_file()
        sys.exit(0)
    elif args.inject_log is not None:
        adb_wrapper.inject_log_message(args.inject_log)
        sys.exit(0)
    elif args.clear_log is True:
        adb_wrapper.clear_log()
        sys.exit(0)
    elif args.connectivity_status is True:
        host_logger.log_error("Not implemented")
        sys.exit(0)
    elif args.screenrecord is not None:
        adb_wrapper.record_screen(args.screenrecord)
        sys.exit(0)
    else:
        host_logger.log_info("No input command argument provided")


sys.exit(0)
