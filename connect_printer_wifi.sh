#!/bin/bash

# connect_printer_wifi.sh
# Script to connect to a WiFi Direct printer configured in CUPS, run a print command, and disconnect.
#
# Usage: ./connect_printer_wifi.sh <printer_name> <print_command> [args...]
# Example: ./connect_printer_wifi.sh "_192_168_44_35" lp -d "_192_168_44_35" document.pdf
# Example: ./connect_printer_wifi.sh "EPSON_WF_M5298_Series_AAE903" lpr -P "EPSON_WF_M5298_Series_AAE903" file.txt
#
# The script derives the WiFi Direct SSID assuming the pattern "DIRECT-XX-PrinterName"
# where XX is extracted from the printer name:
# - For printer names starting with "_", XX is the last part after the final "_".
# - For other printer names, XX is the last two characters.
#
# It saves the current WiFi network, connects to the printer's WiFi Direct network,
# runs the provided print command, then reconnects to the original WiFi network.
# Assumes no password for the WiFi Direct network.
#
# Requirements: macOS with networksetup command available.
# Run with sudo if necessary for network operations.

# Check if at least two arguments (printer name and command) are provided
if [ $# -lt 2 ]; then
    echo "Error: Invalid number of arguments."
    echo "Usage: $0 <printer_name> <print_command> [args...]"
    exit 1
fi

PRINTER_NAME=$1
shift  # Remove printer_name from args, rest is the command

# Get current SSID
ORIGINAL_SSID=$(networksetup -getairportnetwork en0 2>/dev/null | awk -F': ' '{print $2}')
if [ -z "$ORIGINAL_SSID" ]; then
    echo "Error: Unable to get current WiFi network."
    exit 1
fi
echo "Original SSID: $ORIGINAL_SSID"

# Derive XX and SSID
if [[ $PRINTER_NAME == _* ]]; then
    # IP-based name: extract last part after "_"
    XX=$(echo "$PRINTER_NAME" | awk -F'_' '{print $NF}')
    if [ -z "$XX" ]; then
        echo "Error: Unable to extract XX from printer name '$PRINTER_NAME'."
        exit 1
    fi
else
    # Model-based name: last two characters
    XX=${PRINTER_NAME: -2}
    if [ ${#XX} -ne 2 ]; then
        echo "Error: Printer name '$PRINTER_NAME' is too short to extract XX."
        exit 1
    fi
fi

SSID="DIRECT-${XX}-${PRINTER_NAME}"
echo "Derived SSID: $SSID"

# Assume WiFi interface is en0 (common on macOS; adjust if needed)
INTERFACE="en0"

# Connect to printer's WiFi Direct network (assumes no password)
echo "Connecting to $SSID..."
if ! networksetup -setairportnetwork "$INTERFACE" "$SSID"; then
    echo "Error: Failed to connect to $SSID on $INTERFACE."
    exit 1
fi

# Wait for connection to establish
sleep 5

# Verify connection
CURRENT_SSID=$(networksetup -getairportnetwork "$INTERFACE" 2>/dev/null | awk -F': ' '{print $2}')
if [ "$CURRENT_SSID" != "$SSID" ]; then
    echo "Error: Failed to connect to $SSID. Current SSID: $CURRENT_SSID"
    exit 1
fi
echo "Successfully connected to $SSID."

# Run the print command
echo "Running print command: $@"
if ! "$@"; then
    echo "Error: Print command failed."
    # Still try to reconnect
fi

# Reconnect to original WiFi network
echo "Reconnecting to original network: $ORIGINAL_SSID..."
if ! networksetup -setairportnetwork "$INTERFACE" "$ORIGINAL_SSID"; then
    echo "Error: Failed to reconnect to $ORIGINAL_SSID on $INTERFACE."
    exit 1
fi

# Wait and verify
sleep 5
CURRENT_SSID=$(networksetup -getairportnetwork "$INTERFACE" 2>/dev/null | awk -F': ' '{print $2}')
if [ "$CURRENT_SSID" == "$ORIGINAL_SSID" ]; then
    echo "Successfully reconnected to $ORIGINAL_SSID."
else
    echo "Error: Failed to reconnect to $ORIGINAL_SSID. Current SSID: $CURRENT_SSID"
    exit 1
fi