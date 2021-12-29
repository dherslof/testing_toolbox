# pyloc
Simple script for fetching the location based on coordinates or street address.
Based on the [pygeo](https://pypi.org/project/geopy/) project and works quite nice.

## Dependencies
* pygeo (pip3 install pygeo)

## Usage
```bash
$ python3 pyloc.py from_coordinates --longitude 13.376294 --latitude 52.509669
Potsdamer Platz, Tiergarten, Mitte, Berlin, 10785, Deutschland
```

```bash
$ python3 pyloc.py from_address --address "inägogatan 4"
Coordinates
longitude: 11.9123399, latitude: 57.7106128
```