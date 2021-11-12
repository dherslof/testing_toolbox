# isniffer
Ethernet interface sniffer. Print or store packages captured on specified interface. 

## Dependencies
* pyshark (pip3 install pyshark)
* tshark (included in wireshark)

## Usage 
Depending on permission you might need to use `sudo` (or add correct permissions)

```bash
# Help or options:
$ python3 isniff.py --help

# Sniff on interface
$ python3 isniff.py -i <interface_name> 

# Sniff verbose with 3s timeout
$ python3 isniff.py -i <interface_name> -t 3 -V

# Capture 5 packages and print detailed information
$ python3 isniff.py -i <interface_name> -c 5 -V -d 

# Capture packages with filter
$ python3 isniff.py -i <interface_name> -f <wireshark_display_filter>
```
