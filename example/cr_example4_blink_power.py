#!/usr/bin/env python3

# whill module example package
# Copyright (c) 2018 WHILL, Inc.
# This software is released under the MIT License.

import time
from whill import ComWHILL

def power_on_callback():
    print('WHILL wakes up')

def main():
    whill = ComWHILL(port='/dev/ttyUSB0')
    whill.register_callback('power_on', power_on_callback)
    while True:
        whill.sleep(3)
        whill.send_power_off()

        whill.sleep(3)
        whill.send_power_on()


if __name__ == "__main__":
    main()



