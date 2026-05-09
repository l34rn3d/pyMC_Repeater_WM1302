#!/bin/bash
# WM1302 GPIO reset sequence for Raspberry Pi/SenseCAP installs.

set -e

if command -v pinctrl >/dev/null 2>&1; then
    # GPIO pins: 18=POWER_EN, 17=SX1302_RESET, 5=SX1261_RESET, 13=ADC_RESET
    pinctrl set 18 op dh
    sleep 0.01
    pinctrl set 17 op dh
    sleep 0.01
    pinctrl set 17 dl
    sleep 0.01
    pinctrl set 5 op dl
    sleep 0.01
    pinctrl set 5 dh
    sleep 0.01
    pinctrl set 13 op dl
    sleep 0.01
    pinctrl set 13 dh
    sleep 0.5
    exit 0
fi

echo "pinctrl not found" >&2
exit 1
