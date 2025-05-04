#!/bin/env python3

# Description: This script scans (by default) the APIPA (Automatic Private IP Addressing, /16) range in order to
# identify devices that are using self-assigned IP addresses. This can be useful for identifying unknown device IP addresses.

# Author: dherslof

import argparse
import ipaddress
import time
import sys
import signal
from scapy.all import ARP, Ether, srp, conf, IFACES

def signal_handler(sig, frame):
    print("\nCtrl+C detected! Aborting!")
    sys.exit(0)

def check_interface(interface):
    """Check if the given network interface exists."""
    if interface not in [i.name for i in IFACES.data.values()]:
        print(f"Error: Interface {interface} not found.")
        return False
    return True

# 169.254.0.0/16
def scan_apipa_range(interface, ip_range="169.254.4.0/24", timeout=60):
    """Scan the APIPA range for active devices."""

    # Verify the interface exists before proceeding
    if not check_interface(interface):
        return []

    # Create an ARP request packet
    arp_request = ARP(pdst=ip_range)
    ether_frame = Ether(dst="ff:ff:ff:ff:ff:ff")

    packet = ether_frame / arp_request

    # Set the timeout for the scan
    start_time = time.time()
    devices = []

    while time.time() - start_time < timeout:
        # Send the packet and capture responses with a 2-second timeout per cycle
        answered_list = srp(packet, iface=interface, timeout=2, verbose=False)[0]

        for sent, received in answered_list:
            device_info = {'ip': received.psrc, 'mac': received.hwsrc}
            if device_info not in devices:  # Avoid duplicates
                devices.append(device_info)

        if devices:
            break  # Stop scanning once we find a device

    return devices

def matching_ip_address_suggestion(target_ip):
    target_ip_obj = ipaddress.ip_interface(target_ip)
    network = target_ip_obj.network
    for ip in network.hosts():
        if ip != target_ip_obj.ip:  # Ensure we don't suggest input IP address
            return ip

    return None

# Example usage
if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description='Scan eth interface for visible devices. Note: Requires root privileges.')

    arg_parser.add_argument('--interface',   required=False, type= str, action='store', help='Ethernet interface to scan')
    arg_parser.add_argument('--timeout',  required=False, type=int, action='store', help='Timeout in seconds')
    arg_parser.add_argument('--ip_range',  required=False, type=int, action='store', help='IP range to scan, Supported: 16,24')
    arg_parser.add_argument('--suggest_address',  required=False,  action='store_true', help='Suggest a matching IP address to results')

    args = arg_parser.parse_args()

    # Catch ctrl +x signal
    signal.signal(signal.SIGINT, signal_handler)

    # Set variables from arguments or defaults
    if args.interface is not None or args.interface != "":
        interface = args.interface
    else:
        interface = "enx0c37968073e8"
        print(f"No interface provided, using default interface: {interface}")

    if args.timeout is not None or args.timeout != "":
        timeout = args.timeout
    else:
        print("setting default timeout")
        timeout = 120
        print(f"No timeout provided, using default timeout: {timeout}")

    if args.ip_range is not None or args.ip_range != "":
        if args.ip_range == 16:
            ip_range = "169.254.0.0/16"
        elif args.ip_range == 24:
            ip_range = "169.254.4.0/24"
        else:
            ip_range = "169.254.0.0/16"
            print(f"Invalid IP range provided, using default IP range: {ip_range}")
    else:
        ip_range = "169.254.0.0/16"
        print(f"No IP range provided, using default IP range: {ip_range}")

    print(f"Scanning APIPA range on interface {interface} in range {ip_range} with {timeout}s timeout.")

    devices = scan_apipa_range(interface, ip_range, timeout)

    if devices:
        print("Found devices:")
        for device in devices:
            print(f"IP: {device['ip']}, in range:{ip_range}, MAC: {device['mac']}")

        if len(devices) >= 1 and args.suggest_address is True:
            for device in devices:
                suggested_ip = matching_ip_address_suggestion(device['ip'])
                if suggested_ip:
                    print(f"Suggested IP address for {device['ip']}: {suggested_ip}")
                else:
                    print(f"No suggested IP address found for {device['ip']}")

    else:
        print("No devices found in the APIPA range.")
