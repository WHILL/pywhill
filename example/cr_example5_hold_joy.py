#!/usr/bin/env python3

# whill module example package
# Copyright (c) 2018 WHILL, Inc.
# This software is released under the MIT License.


import threading
import time
from whill import ComWHILL


def main():
    whill = ComWHILL(port='COM6')

    count = 0
    side = -50
    whill.hold_joy(front=int(0), side=side, timeout=30000)
    while True:
        count += 1
        print(count)
        if count >= 10:
            count = 0
            side *= -1
            print('Reverse turning direction')
            whill.hold_joy(front=int(0), side=side, timeout=30000)
        time.sleep(1)


if __name__ == '__main__':
    main()