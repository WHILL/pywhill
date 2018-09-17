#!/usr/bin/env python3

# whill module example package
# Copyright (c) 2018 WHILL, Inc.
# This software is released under the MIT License.

import time
from whill import ComWHILL

whill = ComWHILL(port='COM4')
request_speed_mode = 0
whill.start_data_stream(1000, 0, request_speed_mode)
while True:
    time.sleep(1)
    is_refreshed = whill.refresh()
    if whill.latest_received_data_set == 0:
        print(whill.speed_profile[request_speed_mode])
        whill.start_data_stream(1000, 1, request_speed_mode)
    else:
        level, current = whill.battery.values()
        print(whill.acceleration)
        print(whill.gyro)
        print(whill.joy)
        print('Battery Status: remaining capacity {level}%, current draiwng {current}mA'.format(level=level,
                                                                                                current=current))
        print('Motor Status')
        request_speed_mode = (request_speed_mode + 1) % 6
        whill.start_data_stream(1000, 0, request_speed_mode)






