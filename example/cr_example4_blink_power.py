#!/usr/bin/env python3

# whill module example package
# Copyright (c) 2018 WHILL, Inc.
# This software is released under the MIT License.

import time
from whill import ComWHILL


def main():
    whill = ComWHILL(port='COM4')
    while True:
        time.sleep(3)
        whill.send_power_off()
        time.sleep(3)
        whill.send_power_on()


if __name__ == "__main__":
    main()



