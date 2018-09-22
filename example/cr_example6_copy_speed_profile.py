#!/usr/bin/env python3

# whill module example package
# Copyright (c) 2018 WHILL, Inc.
# This software is released under the MIT License.

import time
from whill import ComWHILL

whill = ComWHILL(port='COM6')
request_speed_mode = 0
while True:
    whill.start_data_stream(1000, 0, request_speed_mode)
    time.sleep(1)
    is_refreshed = whill.refresh()
    print('{request_speed_mode}: {profile}'.format(request_speed_mode=request_speed_mode+1,
                                                   profile=whill.speed_profile[request_speed_mode]))
    request_speed_mode += 1
    if request_speed_mode >= 6:
        print('All 6 speed profiles have been read. Enter [1-4] which you want to apply to 6 (CR).')
        print('Enter "0" to exit')
        key_input = -1
        acceptable_index = [1, 2, 3, 4]
        while key_input not in acceptable_index:
            key_input = int(input('>>>  '))
            if key_input == 0:
                exit()

        whill.set_speed_profile_via_dict(5, whill.speed_profile[key_input - 1])
        request_speed_mode = 0
