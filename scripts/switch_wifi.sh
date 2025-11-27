#!/bin/bash

# Usage: ./switch_wifi.sh [martin|epson]
# This script switches between two predefined WiFi networks on macOS.
# - 'martin': Connects to "MartinRouterKing"
# - 'epson': Connects to "DIRECT-34-EPSON-WF-M5298 Series"
# The script disconnects from the current network before attempting to connect to the specified one.
# Error handling includes checking for valid arguments and verifying successful connection.

AIRPORT="/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"

if [ $# -ne 1 ]; then
    echo "Usage: $0 [martin|epson]"
    exit 1
fi

case $1 in
    martin)
        SSID="MartinRouterKing"
        ;;
    epson)
        SSID="DIRECT-34-EPSON-WF-M5298 Series"
        ;;
    *)
        echo "Invalid option. Use 'martin' or 'epson'."
        exit 1
        ;;
esac

# Disconnect from current network
$AIRPORT -z
sleep 2

# Attempt to connect to the specified network
$AIRPORT -A "$SSID"
sleep 5  # Allow time for connection attempt

# Verify connection
CURRENT_SSID=$($AIRPORT -I | grep " SSID:" | awk '{print $2}')
if [ "$CURRENT_SSID" = "$SSID" ]; then
    echo "Successfully connected to $SSID"
else
    echo "Failed to connect to $SSID. Please check network availability and credentials."
    exit 1
fi