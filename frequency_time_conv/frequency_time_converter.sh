#!/bin/env bash

# Description: Simple helper script for converting between time and frequency
# Author: dherslof

usage()
{
   cat <<EOF
Description:
Simple helper script for converting between time and frequency

Usage:
Convert freq -> ms
$0 -f <frequency_in_Hz>

Convert ms -> freq
$0 -t <time_in_ms>

EOF
}

COMMAND="$1"
VALUE="$2"

# Check if help argument provided
if [[ ${COMMAND} == "-h" || ${COMMAND} == "h" || ${COMMAND} == "--help" ]]; then
   usage
   exit
fi

# Input checks
if [ -z "${VALUE}" ]; then
    echo "ERR: No input value provided"
    exit 1
fi

if [[ ${VALUE} =~ ^[0-9]+$ ]]; then
        if [ "${VALUE}" == 0 ]; then
            echo "ERR: Input value can't be = 0"
            exit 1
        fi
else
    echo "ERR: Input value has to be a num value"
    exit 1
fi

# Calculate s/ms
if [[ ${COMMAND} == "-f" ]]; then
    # scale set 4decimals, and bc is for floating-point-arithmetic
    s=$(echo "scale=4; 1 / $VALUE" | bc)
    if [ "${s}" == 0 ]; then
        echo "ERR: scaling factor is to low to calculate output, value_in_s < 0.0000s"
        exit 1
    fi

    ms=$(echo "scale=2; ${s} * 1000" | bc)
    echo "${VALUE}Hz = ${s}s -> ${ms}ms"
    exit 0
# Calculate Hz
elif [[ ${COMMAND} == "-t" ]]; then
    s=$(echo "scale=2; ${VALUE} / 1000" | bc)
    freq=$(echo "scale=4; 1 / $s" | bc)
    if [ "${freq}" == 0 ]; then
        echo "ERR: scaling factor is to low to calculate output"
        exit 1
    fi

    echo "${VALUE}ms = ${freq}Hz"
    exit 0
else
    echo "ERR: Unknown command, for usage: $ $0 -h"
    exit 1
fi