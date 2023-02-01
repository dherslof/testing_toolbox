# Apple .HEIC Converter Script
Simple support script around heic-convert. It converts Apple `.HEIC` files (apple pictures) to .`jpg`

Written for Ubuntu (Debian).

## Dependencies
* heic-converter

## Usage
```bash
# Convert all .heic files in foobar directory with verbose logging 
$ ./heic_converter.sh -d foobar -v 

# Convert single file 
$ ./heic_converter.sh -f foobar.HEIC

# Usage and help
$ ./heic_converter.sh -h
```
