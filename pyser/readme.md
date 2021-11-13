# Pyser - PySerial
Send commands over a serial device

## Dependencies
* serial (pip3 install serial)

## Usage
Depending on permission you might need to use `sudo` (or add correct permissions)


```bash
# Send hello world to USB0
$ python3 pyser.py -d /dev/ttyUSB0 -b 115200 -c "hello world"

# Get help & options 
$ python3 pyser.py --help

# Display default settings
$ python3 pyser.py -d <deive> -b <baudrate> -D
```
