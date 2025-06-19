# Frequency-Time Converter

A simple helper script to convert between frequency (Hz) and time (ms).

## Usage

Convert frequency (Hz) to time (ms):
```sh
./frequency_time_converter.sh -f <frequency_in_Hz>
```

Convert time (ms) to frequency (Hz):
```sh
./frequency_time_converter.sh -t <time_in_ms>
```

Show help:
```sh
./frequency_time_converter.sh -h
```

## Example

```sh
./frequency_time_converter.sh -f 1000
# Output: 1000Hz = 0.0010s -> 1.00ms

./frequency_time_converter.sh -t 10
# Output: 10ms = 100.0000Hz
```