# APIPA Scanner
Since I had the need to obtain IP addresses of some devices which was assigned using
`APIPA`, I wrote this tool. It's in two versions, one simple terminal script and one with
a **GUI** based on (customtkinter)[https://customtkinter.tomschimansky.com].

They both work the same, and I use the script more then the GUI, but since I recently came in contact
with `customtkinter` I wanted to check it out.
I also had the intention to share this with some friends that appreciate a GUI more then the command line.

# Disclaimer
Works, but not heavily tested. There will be corner cases and exceptions which isn't handled. Do what you want with that info.

## Dependencies
* customtkinter
* Tkinter
* scapy

```bash
$ pip3 install customtkinter scapy && sudo apt install python3-tk
```

## Usage

Command line script:
```bash
# normal usage
$ python3 apipa_scanner.py --interface <ETH-INTERFACE> --timeout <TIMEOUT> --ip_range <IP_RANGE>

# more help & explanation
$ python3 apipa_scanner.py --help

```

GUI:
```bash
# launch it and everything will make sense
$ python3 python3 apipa_scanner_gui.py
```

## APIPA
APIPA = Automatic Private IP Addressing, and key points described by chatgpt
> - Range → 169.254.0.0/16 (reserved by IANA).
> - Used When → No DHCP response.
> - Subnet Mask → Always 255.255.0.0.
> - No Internet Access → Only local communication.

Basically a feature in modern operating systems that allows a device to assign itself an IP address when it fails to obtain one from a DHCP server.
