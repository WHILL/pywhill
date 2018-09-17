#!/usr/bin/env python3

# whill module example package
# Copyright (c) 2018 WHILL, Inc.
# This software is released under the MIT License.

import time
from whill import ComWHILL

request_speed_mode = 0
whill = ComWHILL(port='COM4')


def callback0():
    global request_speed_mode, whill
    print('callback 0')
    print(whill.speed_profile[request_speed_mode])
    whill.start_data_stream(1000, 1, request_speed_mode)


def callback1():
    global request_speed_mode, whill
    print('callback 1')
    level, current = whill.battery.values()
    print(whill.accelerometer)
    print(whill.gyro)
    print(whill.joy)
    print('Battery Status: remaining capacity {level}%, current draiwng {current}mA'.format(level=level,
                                                                                            current=current))
    print('Motor Status')
    request_speed_mode = (request_speed_mode + 1) % 6
    whill.start_data_stream(1000, 0, request_speed_mode)


def main():
    whill.register_callback('data_set_0', callback0)
    whill.register_callback('data_set_1', callback1)
    whill.start_data_stream(1000, 0, request_speed_mode)
    while True:
        time.sleep(0.1)
        whill.refresh()


if __name__ == "__main__":
    main()



