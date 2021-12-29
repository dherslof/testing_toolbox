#!/usr/bin/env python3

# Description: Get location based on address or coordinates. Can be useful when debugging in which
#              the location can be a factor.
#
# Author: dherslof

# https://pypi.org/project/geopy/

# install dependency: $ pip3 install geopy && pip3 install pretty-errors

import argparse
from geopy.geocoders import Nominatim
import pretty_errors

class LocationHlpr:

   def get_location_from_coordinates(self, lon, lat):
      input_coordinates = lat + ", " + lon
      # debug print
      #print("coordinates: {}".format(input_coordinates))

      geolocator = Nominatim(user_agent="pyloc")
      location = geolocator.reverse(input_coordinates)
      print(location.address)

   def get_location_from_address(self, address):
      geolocator = Nominatim(user_agent="pyloc")
      location = geolocator.geocode(address)
      print("Coordinates\nlongitude: {}, latitude: {}".format(location.longitude, location.latitude))

      # Extra info which can be nice some times
      #print("Raw information\n")
      #print(location.raw)

if __name__ == '__main__':

   arg_parser = argparse.ArgumentParser(description="Get location from either coordinates or address")

   subparsers = arg_parser.add_subparsers(dest='subparser_name')

   parser_from_coordinates = subparsers.add_parser('from_coordinates', help='get location address based on coordinates')
   parser_from_coordinates.add_argument('--longitude', help='longitude coordinate', action='store', required=True)
   parser_from_coordinates.add_argument('--latitude', help='latitude coordinate', action='store', required=True)

   parser_from_address = subparsers.add_parser('from_address', help='get location based on address')
   parser_from_address.add_argument('--address', help='Address to get location from', action='store', required=True)

   args = arg_parser.parse_args()

   location_hlpr = LocationHlpr()

   if args.subparser_name == "from_coordinates":
      location_hlpr.get_location_from_coordinates(args.longitude, args.latitude)

   if args.subparser_name == "from_address":
      location_hlpr.get_location_from_address(args.address)
